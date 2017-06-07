# tag structure
# tag method ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattr__',
# '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
# '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_constructorTypes', '_create',
# '_data_for_gitlab', '_from_api', '_get_display_encoding', '_get_object', '_id_in_delete_url', '_id_in_update_url',
# '_module', '_obj_to_str', '_set_from_dict', '_set_manager', '_update', '_url', '_urlPlural', 'as_dict', 'canCreate',
# 'canDelete', 'canGet', 'canList', 'canUpdate', u'commit', 'create', 'delete', 'display', 'get', 'getRequiresId',
# 'gitlab', 'id', 'idAttr', 'json', 'list', 'managers', u'message', u'name', 'optionalCreateAttrs', 'optionalGetAttrs',
# 'optionalListAttrs', 'optionalUpdateAttrs', 'pretty_print', 'project_id', u'release', 'requiredCreateAttrs',
# 'requiredDeleteAttrs', 'requiredGetAttrs', 'requiredListAttrs', 'requiredUpdateAttrs', 'requiredUrlAttrs', 'save',
# 'set_release_description', 'shortPrintAttr', 'short_print']

# tag attributes
# <class 'gitlab.v3.objects.ProjectTag'> => {'_module':
#  <module 'gitlab.v3.objects' from 'C:\Python27\lib\site-packages\gitlab\v3\objects.pyc'>,
# u'name': u'v2.10.4', 'gitlab': <gitlab.Gitlab object at 0x0000000002270518>, '_from_api': True, u'release': None,
# u'commit': <ProjectCommit id:1d248f4dfc95707a4ee42c48c1a979e8ea4a9234>, u'message': u'CORE-11218 v2.10.4',
# 'project_id': 470, 'id': None}

import gitlab

GITLAB_URL = 'http://gitlab.bt.bpc.in'
GITLAB_TOKEN = 'SasnDpte7dhAMgNAFPLA'
project_id = 470  # devops/back
tag = 'v2.14.0'
new_tag = 'v2.14.2'
gl = gitlab.Gitlab(GITLAB_URL, GITLAB_TOKEN)
project = gl.projects.get(project_id)

tags = project.tags.list()
tag_list = [x.name for x in tags]
for rec in tags:
    print rec

# create tag function
tag_create = project.tags.create({'tag_name': new_tag, 'ref': 'future'}, sudo='kazakov')
