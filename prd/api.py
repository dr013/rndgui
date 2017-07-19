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

    def get_gl(self):
        return self.gl

    def check_tag(self, project_id, tag):
        project_obj = self.get_project(project_id)
        tags = project_obj.tags.list(all=True)
        for rec in tags:
            if tag in rec.name:
                return rec.commit.id

        return None

    def check_ref(self, project_id, ref, ref_type='branch'):
        revision = None
        project_obj = self.get_project(project_id)
        if 'branch' in ref_type:
            branches = project_obj.branches.list()
            for rec in branches:
                if ref in rec.name:
                    return rec.commit['id']
        else:
            revision = ref
        return revision

    def create_tag(self, project_id, tag, ref, desc, user=None, ref_type='branch'):
        revision = None
        result = ''
        logger.debug("Check Gitlab tag {}".format(tag))
        revision = self.check_tag(project_id, tag)
        if revision:
            logger.debug("Found gitlab tag {tag} in GitLab project {prd}.".format(tag=tag, prd=project_id))

            result = 'Found existing tag {tag} in GitLab project {prj}'.format(tag=tag,
                                                                               prj=self.get_project(project_id).name)
        else:
            revision = self.check_ref(project_id=project_id, ref=ref, ref_type=ref_type)
            if revision:
                try:
                    tag = self.gl.project_tags.create({'tag_name': tag, 'ref': ref},
                                                      project_id=project_id)
                    tag.set_release_description(desc)
                    result = "Create new tag {tag} in GitLab project {prd}.".format(tag=str(tag),
                                                                                    prd=self.get_project(
                                                                                        project_id).name)
                except gitlab.GitlabCreateError as errm:
                    logger.error(str(errm))
                    result = str(errm)
            else:
                result = 'Ref {ref} not found in project {prj}. Skip create tag {tag}.'
        logger.info(result)
        return revision

    def get_revision_list(self, project_id, ref_name, since=None):
        project = self.gl.projects.get(project_id)
        logger.info("Project_id:{}".format(project_id))
        logger.info('Ref name: {}'.format(ref_name))
        logger.info(str(since))
        if since:
            commits = project.commits.list(ref_name=ref_name, since=str(since), all=True)
        else:
            commits = project.commits.list(ref_name=ref_name, all=True)
        if not commits:
            commits = project.commits.list(ref_name=ref_name)[0:1]

        return commits


# noinspection PyCompatibility
class JiraProject:
    def __init__(self, project=None, user=settings.JIRA_USER, password=settings.JIRA_PASS):
        self.logger = logging.getLogger('jira')
        self.user = user
        self.password = password
        self.jira = None
        self.project = project
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

    def get_jira(self):
        return self.jira

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

    def check_version(self, version):
        versions = self.jira.project_versions(self.project)
        find_version = [x.name for x in versions]
        x = {x.name: x for x in versions}
        if version in find_version:
            return x[version]
        else:
            return False

    def create_version(self, version_name, start=datetime.datetime.now().isoformat(), released=False, archived=False,
                       description=None):

        version = self.check_version(version_name)
        if not version:
            logger.info("Create version {ver} in Jira {prj}".format(ver=version_name, prj=self.project))
            version = self.jira.create_version(name=version_name, project=self.project.key, description=description,
                                               released=released, archived=archived, startDate=start)
        else:
            logger.info("Found version {ver} in Jira {prj}".format(ver=version_name, prj=self.project))
        return version

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
        logger.debug(str(fields))

        if "customfield_10024" in fields:
            params["customfield_10024"] = {"value": "Core"}

        if "customfield_10067" in fields:  # Affects to Release Notes
            params["customfield_10067"] = {"value": "No"}

        res = self.jira.create_issue(fields=params)

        return res

    def create_release_task(self, release):
        summary = "Release {}".format(release)
        version_number = '{rel}.0'.format(rel=release)

        res = self.create_task(summary, version_number)
        return res

    def create_sub_task(self, parent, build):
        desc = "Build {b}".format(b=build)
        self.create_version(version_name=build, description=desc)
        params = {
            "project": {"key": self.project.key},
            "parent": {"key": parent},
            "summary": desc,
            "issuetype": {"name": "Sub-task"},
            "versions": [{"id": self.get_version_id(build)}]
        }

        fields = self.get_required_field(self.project.key, 'Sub-task')

        if "customfield_10024" in fields:
            params["customfield_10024"] = {"value": "Core"}
        logger.debug(msg=str(params))
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

    def find_transition(self, task, act):
        issue = self.jira.issue(task)
        transitions = self.jira.transitions(issue)
        logger.debug(transitions)
        for rec in transitions:
            if act in rec['name']:
                return issue, rec['id']
        return issue, None

    def close_task(self, task):
        act = 'Close Issue'
        issue, transition = self.find_transition(task, act)
        if transition:
            res = self.jira.transition_issue(issue, transition)
        else:
            res = None
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

    def get_all_issue_type(self):
        obj_list = self.jira.createmeta(projectKeys=self.project, expand='projects.issuetypes')
        issue_type = [x['name'] for x in obj_list['projects'][0]['issuetypes']]
        return issue_type

    def get_favorive_filter(self):
        return self.jira.favourite_filters()

    def get_filter(self, filter_id):
        return self.jira.filter(filter_id)

