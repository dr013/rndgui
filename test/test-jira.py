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
# task_key = 'CORE-36'
# issue = jira.issue(task_key)
#
# print (issue.fields.status, dir(issue))
# for rec in issue.raw['fields']:
#     print ("Field:", rec, "Value:", issue.raw['fields'][rec])

project = 'SVCI'
task_type = 'Task'
obj_list = jira.createmeta(projectKeys=project, issuetypeNames=task_type,
                           expand='projects.issuetypes.fields')

fields = []
field_dict = obj_list['projects'][0]['issuetypes'][0]['fields']
for key, value in field_dict.iteritems():
    if value['required'] and not value['hasDefaultValue']:
        print key, value
        print
        print
        fields.append(key)

# project = jira.project('CORE')
# version = jira.project_versions(project)
# print [x.name for x in version]
# # for rec in version:
# #     print rec
# #     print rec.released
# #     print rec.name
# #     print rec.archived
# #     print '='*30
# issue = jira.issue('CORE-13121')
# transitions = jira.transitions(issue)
# print transitions

project = jira.project('CORE')
version = jira.project_versions(project)
print [x.name for x in version]
# for rec in version:
#     print rec
#     print rec.released
#     print rec.name
#     print rec.archived
#     print '='*30
issue = jira.issue('CORE-13121')
transitions = jira.transitions(issue)
print transitions

filter = jira.favourite_filters()
for rec in filter:
    print rec, rec.id, rec.jql
