# coding=utf-8
import xlsxwriter
from prd.api import JiraProject
from .models import JiraReportField

all_fld = (
    'Project', 'Key', 'Summary', 'Issue Type', 'Status', 'Priority', 'Resolution', 'Assignee', 'Reporter', 'Creator',
    'Created', 'Last Viewed', 'Updated', 'Resolved', 'Affects Version/s', 'Fix Version/s', 'Component/s', 'Due Date',
    'Votes', 'Watchers', 'Images', 'Original Estimate', 'Remaining Estimate', 'Time Spent', 'Work Ratio', 'Sub-Tasks',
    'Linked Issues', 'Environment', 'Description', 'Security Level', 'Progress', u'Σ Progress', u'Σ Time Spent',
    u'Σ Remaining Estimate', u'Σ Original Estimate', 'Labels', 'Test issues', 'Test-cases', 'SAD is not stored',
    'Request participants', 'Additional information', 'Testing', 'Network traffic encryption', 'QcIssueType',
    'New CHD locations', 'Product by question', 'QcDebug', 'Test case update', 'Time to resolution', 'Answer',
    'Found in version', 'In MS Project', 'Root cause analysis[RCA]', 'Customer Request Type', 'Issue Resolution',
    'SVFE development', 'Time to first response', 'Current On-hold reason', 'Issue Priority', 'Phase found',
    'Testing type',
    'gitBranch', 'Business analysis', 'Document Category', 'Primary review', 'Target Release', 'BPC Group', 'Testfield',
    'Start Date', 'gitCommitsReferenced', 'Affects to Release Notes', 'Java issues', 'Subject Matter Expert',
    'Test scenario', 'MS Project Task Name', 'SVFE issues', 'MS Project task', 'Owner', 'System analysis',
    'Target Language', 'Development estimation', 'Need transfer to trunk', 'Order', 'Resource Documents', 'Hotfix',
    'List of additional third party software', 'Database options', 'FrontEnd library/ies', 'Database encoding',
    'FrontEnd module/s', 'Application server', 'Enviroment type', 'QcFoundInVersion', 'Who needs access', 'Public key',
    'Duration', 'Product', 'Platform', 'Business Value', 'Enviroment purpose', 'Flagged',
    'Release Notes description/ Installation Notes', 'Story Points', 'EsmRegistrationDate', 'EsmClientExecutor',
    'Release',
    'Browser', 'QcAssignedTo', 'Issue Resolution(old)', 'Environment Type', 'Problem Sla',
    'Automatic set priority to Major', 'Hardware', 'Functionality(Lotus)', 'Operational System', 'Impact on end user',
    'Important', 'End Date', 'Expected Result', 'MS Project', 'Story Points', 'Epic/Theme', 'Steps to Reproduce',
    'Fixed by', 'QcSystem', 'Sprint', 'Business Value', 'QcRootCause', 'Epic Link', 'Epic Name', 'Decline reason',
    'Epic Color', 'Epic Status', 'Rank', 'Customer', 'Priority to Fix', 'Sprint', 'Tested Version',
    'Link to original Issue', 'Branch', 'Flagged', 'Actual Result', 'QcDetectInVersion', 'Blocked', 'QcDetectionDate',
    'Contact', 'Block Date', 'Installation instructions', 'QcWrittenBy', 'Chargeable', 'Temp Field',
    'Installation impact',
    'Actual PoC scenario', 'Installation note', 'Suggestions to improve', 'QcDetectedBy', 'Useful features',
    'Future steps of PoC', 'Customer Severity', 'SVBO development', 'Java development', 'SVBO issues',
    'Description for Release Notes', 'Estimated time', 'Phase Name', 'Analyzed By', 'Impact', 'Developed by',
    'Found in Company', 'QcBugId', 'Resolve date', 'Tested By', 'Closed By', 'Expected Date', 'QcIncidentDate',
    'Incident description', 'Project', 'Delivery date', 'Project Manager', 'Incident cause', 'Name of patch',
    'Delivered',
    'Incident solution', 'QcComments', 'Verified by', 'Jira Project', 'QcJiraSynch', 'preAssigne', 'preStatus',
    'IsDocumented', 'Module', 'Assessment by pre-sale consultant', 'Assessment by client', 'PAN screens',
    'Data encryption',
    'Functionality', 'Account data usage', 'TLS 1.2 protection', 'Key generation', 'Key protection', 'CHD export',
    'Validated by', 'PANs is masked', 'Source Document', 'CHD is not stored on internet facing servers', 'ExtTicketID',
    'Include into plan', 'Insecure protocols usage', 'QcSourceSystem', 'Reopened by', 'Satisfaction', 'Resolved by')


def excel_by_filter(filter_id, user, passwd, fields=None):
    jira = JiraProject(user=user, password=passwd).get_jira()
    flt = jira.filter(filter_id)

    issues = jira.search_issues(flt.jql)

    field_list = JiraReportField.objects.filter(jira_filter__pk=filter_id).values_list('field_name')

    allfields = jira.fields()
    name_map = {field['id']: field['name'] for field in allfields}
    filename = '/tmp/report.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    # set title
    i = 0
    fild_ord = []
    bold = workbook.add_format({'bold': True})
    for field_name in all_fld:
        for key, value in issues[0].raw['fields'].iteritems():
            if name_map[key] in field_name:
                worksheet.write(0, i, name_map[key], bold)
                fild_ord.append(key)
            else:
                worksheet.write(0, i, field_name, bold)
        i += 1
    j = 1
    i = 0
    for rec in issues:
        a = rec.raw['fields']
        for fld in fild_ord:
            if fld in a:
                if a[fld]:
                    if isinstance(a[fld], unicode):
                        worksheet.write(j, i, a[fld])
                    elif isinstance(a[fld], dict):
                        if 'displayName' in a[fld]:
                            worksheet.write(j, i, a[fld]['displayName'])
                        elif 'value' in a[fld]:
                            worksheet.write(j, i, a[fld]['value'])
                        elif 'name' in a[fld]:
                            worksheet.write(j, i, a[fld]['name'])
                    elif isinstance(a[fld], int) or isinstance(a[fld], float):
                        worksheet.write(j, i, a[fld])
                    elif isinstance(a[fld], list):
                        if isinstance(a[fld][0], unicode):
                            worksheet.write(j, i, a[fld][0])
                        elif isinstance(a[fld][0], dict):
                            if 'value' in a[fld][0]:
                                worksheet.write(j, i, a[fld][0]['value'])
                            elif 'name' in a[fld][0]:
                                worksheet.write(j, i, a[fld][0]['name'])

            i += 1
        worksheet.write(j, 1, rec.raw['key'], bold)
        j += 1
        i = 0

    workbook.close()
    return filename
