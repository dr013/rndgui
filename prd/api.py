import gitlab
from django.conf import settings


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
        return self.gl.projects.list()

    def project(self, pid):
        obj = self.gl.projects.get(pid)
        return obj
