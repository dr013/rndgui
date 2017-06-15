import jenkins
import logging
from django.conf import settings
import requests

# Get an instance of a logger
logger = logging.getLogger(__name__)


class JenkinsWrapper:
    def __init__(self):
        try:
            self.server = jenkins.Jenkins(settings.JENKINS_HOST,
                                          username=settings.JENKINS_USER,
                                          password=settings.JENKINS_PASS)
            self.user = self.server.get_whoami()
        except jenkins.JenkinsException:
            logger.error("Could not connect to jenkins host - {h}".format(h=settings.JENKINS_HOST))

    def check_build_perm(self, task):
        # TODO check job permissions
        pass

    def run_build(self, task, param):
        """
            Run Jenkins task via python-jenkins package
            :param task: jenkins task name
            :param param: jenkins param, e.g param={'param1': 'test value 1', 'param2': 'test value 2'}
            :return:
        """
        result = ''
        try:
            next_build = self.server.get_job_info(task)['nextBuildNumber']
            self.server.build_job(name=task, parameters=param)
            result = '{j}job/{t}/{b}/'.format(j=settings.JENKINS_HOST, t=task, b=next_build)
        except jenkins.JenkinsException, err:
            logger.error("Auth error - {e}".format(e=err))
        return result

    def stop_build(self, task_url):
        try:
            url = '{u}stop'.format(u=task_url)
            auth = (settings.JENKINS_USER, settings.JENKINS_PASS)
            req = requests.post(url=url, auth=auth)
        except requests.HTTPError, err:
            logger.error("HTTP error - {e}".format(e=err))

if __name__ in '__main__':
    pass
