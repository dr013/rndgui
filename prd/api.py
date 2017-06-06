import gitlab
from django.conf import settings
from jira.client import JIRA
from jira.exceptions import JIRAError
import datetime
import requests
import json
import logging

logger = logging.getLogger('prd')


class GitLab:
    def __init__(self):
        self.gl = None
        self.url = settings.GITLAB_URL
        self.token = settings.GITLAB_TOKEN
        self._connect()

    def _connect(self):
        self.gl = gitlab.Gitlab(self.url, self.token)
        self.gl.auth()

    def project_list(self):
        return self.gl.projects.list(all=True)

    def get_project(self, pid):
        obj = self.gl.projects.get(pid)
        return obj

    def check_tag(self, project_id, tag):
        project_obj = self.get_project(project_id)
        tags = project_obj.tags.list(all=True)
        tag_list = [x.name for x in tags]
        if tag in tag_list:
            return True
        else:
            return False

    def create_tag(self, project_id, tag, ref, desc, user=None):
        # TODO check permission for sudo user  - add tag available only for Developer, Master and Owner role.
        logger.debug("Check Gitlab tag")
        if self.check_tag(project_id, tag):
            logger.debug("Found gitlab tag {tag} in GitLab project {prd}".format(tag=tag, prd=project_id))
        else:
            try:
                tag = self.gl.project_tags.create({'tag_name': tag, 'ref': ref},
                                                  project_id=project_id, sudo=user)
                tag.set_release_description(desc)
            except gitlab.GitlabCreateError as errm:
                logger.error(str(errm))

            logger.info("Create new tag {tag} in GitLab project {prd}".format(tag=tag, prd=project_id))

    def get_revision_list(self, project_id, ref_name, since):
        project = self.gl.projects.get(project_id)
        logger.info("Project_id:{}".format(project_id))
        logger.info('Ref name: {}'.format(ref_name))
        logger.info(str(since))
        commits = project.commits.list(ref_name=ref_name, since=str(since), all=True)

        return commits


# noinspection PyCompatibility
class JiraProject:
    def __init__(self, project):
        self.logger = logging.getLogger('jira')
        self.user = settings.JIRA_USER
        self.password = settings.JIRA_PASS
        self.jira = None
        self.project = None
        self.connect_jira()
        if project:
            self.set_project(project)

    def connect_jira(self):
        try:
            self.jira = JIRA(options=settings.JIRA_OPTIONS, basic_auth=(self.user, self.password))
        except JIRAError as msg:
            self.logger.error('Error connect')
            self.logger.error(str(msg))
            return

    def project_list(self):
        project_list = self.jira.projects()
        return project_list

    def set_project(self, project):
        self.project = self.jira.project(project.upper())

    def get_project_desc(self):
        return self.project.description

    def get_version_id(self, version_number):
        versions = self.jira.project_versions(self.project)
        if versions:
            for version in versions:
                if version_number in version.name:
                    return version.id

    def release_version(self, version_id):
        url = "{server}/rest/api/2/version/{version}".format(version=version_id, server=settings.JIRA_SERVER)
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        param = json.dumps({'released': 'true'})
        req = requests.put(url, data=param, auth=(self.user, self.password), headers=headers)
        if req.status_code == 200:
            return True
        else:
            return False

    def create_version(self, version_name):
        cur_date = datetime.datetime.now()
        res = self.jira.create_version(version_name, self.project, startDate=cur_date.isoformat())
        return res

    def move_version(self, version_id, after_id):
        res = self.jira.move_version(after_id, version_id)
        return res

    def create_failed_task(self, summary, description, issuetype, components, branch, phase, vesion_id):
        params = {
            "project": {"key": self.project.key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
            "components": [{"name": components}],
            "customfield_10024": {"value": branch},
            "customfield_14705": {"id": vesion_id},
            "customfield_14706": {"value": phase},
            "versions": [{"id": vesion_id}]
        }
        res = self.jira.create_issue(fields=params)
        return res

    def create_task(self, summary, version_number):
        params = {
            "project": {"key": self.project.key},
            "summary": summary,
            "issuetype": {"name": "Task"},
            "versions": [{"id": self.get_version_id(version_number)}]
        }
        fields = self.get_required_field(self.project.key, 'Task')
        if "customfield_10024" in fields:
            params["customfield_10024"] = "Core"
        res = self.jira.create_issue(fields=params)
        return res

    def create_release_task(self, release):
        summary = "Release {}".format(release)
        version_number = '{rel}.0'.format(rel=release)

        res = self.create_task(summary, version_number)
        return res

    def create_sub_task(self, parent, build):
        params = {
            "project": {"key": self.project.key},
            "parent": {"key": parent},
            "summary": "Build {b}".format(b=build),
            "issuetype": {"name": "Sub-task"},
            "versions": [{"id": self.get_version_id(build)}]
        }

        fields = self.get_required_field(self.project.key, 'Sub-task')

        if "customfield_10024" in fields:
            params["customfield_10024"] = "Core"

        res = self.jira.create_issue(fields=params)
        return res

    def create_sub_task_sv(self, parent, build, vesion_id):
        params = {
            "project": {"key": self.project.key},
            "parent": {"key": parent},
            "summary": "Build {b}".format(b=build),
            "issuetype": {"name": "Sub-task"},
            "customfield_10024": {"value": "Core"},
            "versions": [{"id": vesion_id}]
        }
        res = self.jira.create_issue(fields=params)
        return res

    def create_sub_task_fm(self, parent, build):
        params = {
            "project": {"key": self.project.key},
            "parent": {"key": parent},
            "summary": "Build {b}".format(b=build),
            "issuetype": {"name": "Sub-task"},
            "customfield_10024": {"value": "Core"}
        }
        res = self.jira.create_issue(fields=params)
        return res

    def create_sub_task_for_build(self, parent, build, vesion_id):
        params = {
            "project": {"key": self.project.key},
            "parent": {"key": parent},
            "summary": "Build {b}".format(b=build),
            "issuetype": {"name": "Sub-task"},
            "customfield_10024": {"value": "Core"},
            "versions": [{"id": vesion_id}]
        }
        res = self.jira.create_issue(fields=params)
        return res

    def assign_task(self, task, author):
        issue = self.jira.issue(task)
        res = issue.update(assignee={'name': author})
        return res

    def start_task(self, task):
        issue = self.jira.issue(task)
        res = self.jira.transition_issue(issue, '4')
        return res

    def stop_task(self, task):
        issue = self.jira.issue(task)
        res = self.jira.transition_issue(issue, '5', resolution={'id': '1'})
        return res

    def close_task(self, task):
        issue = self.jira.issue(task)
        res = self.jira.transition_issue(issue, '701')
        return res

    def add_comment(self, task, msg):
        issue = self.jira.issue(task)
        res = self.jira.add_comment(issue, msg)
        return res

    def add_work(self, task, worktime, username):
        issue = self.jira.issue(task)
        res = self.jira.add_worklog(issue, timeSpent=worktime, comment="Work on task", user=username)
        return res

    def attach_file(self, task, attachment):
        try:
            with open(attachment):
                attach = self.jira.add_attachment(task, attachment)
        except IOError as e:
            self.logger.error("ERROR: Unable to open file - {a}".format(a=attachment))
            self.logger.error(str(e))
            attach = False
        return attach

    def add_watcher(self, task, author):
        res = self.jira.add_watcher(task, author)
        return res

    def search_issue(self, summary):
        search_str = 'summary~"{sum}" and project="{prj}"'.format(sum=summary, prj=self.project.key)
        issue_list = self.jira.search_issues(search_str)
        if issue_list:
            return issue_list[0]
        else:
            return None

    def get_required_field(self, project, task_type):
        obj_list = self.jira.createmeta(projectKeys=project, issuetypeNames=task_type,
                                        expand='projects.issuetypes.fields')
        fields = []
        field_dict = obj_list['projects'][0]['issuetypes'][0]['fields']
        for key, value in field_dict.iteritems():
            if value['required'] and not value['hasDefaultValue']:
                fields.append(key)
        return fields

    def get_task_status(self, task):
        status = str(self.jira.issue(task).fields.status)
        return status
