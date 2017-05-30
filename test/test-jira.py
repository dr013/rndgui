# jira credential
from jira.client import JIRA

JIRA_USER = 'jira-system'
JIRA_PASS = '3WqOGzrj9G'
# Jira
JIRA_URL = 'http://jira.bpc.in:8080'

JIRA_OPTIONS = {
            'server': JIRA_URL,
            'verify': False
        }

jira = JIRA(options=JIRA_OPTIONS, basic_auth=(JIRA_USER, JIRA_PASS))
task_key = 'DVPT-31'
issue = jira.issue(task_key)

print issue.fields.status, dir(issue)
