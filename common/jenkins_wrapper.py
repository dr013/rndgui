import jenkins
import logging

JENKINS_HOST = 'http://jenkins2.bt.bpc.in:8080/'
JENKINS_USER = 'dorontcov'
JENKINS_PASS = 'V6LqKu5F'

# Get an instance of a logger
logger = logging.getLogger(__name__)


class JenkinsWrapper:
    def __init__(self):
        try:
            self.server = jenkins.Jenkins(JENKINS_HOST, username=JENKINS_USER, password=JENKINS_PASS)
            self.user = self.server.get_whoami()
        except jenkins.JenkinsException:
            logger.error("Could not connect to jenkins host - {h}".format(h=JENKINS_HOST))

    def check_build_perm(self, task):
        # TODO check job permissions
        return self.server.get_job_info(name=task)

    def run_build(self, task, param):
        try:
            return self.server.build_job(name=task, parameters=param)
        except jenkins.JenkinsException, err:
            logger.error("Auth error - {e}".format(e=err))
            print err.message
            return False


if __name__ in '__main__':
    task1 = 'test.host.deploy'
    task2 = 'test.django'
    j = JenkinsWrapper()
    print j.run_build(task=task1, param={'PROJECT': 'backoffice_test_ci'})

