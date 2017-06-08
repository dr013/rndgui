from __future__ import unicode_literals


def json_data(request):
    a = {'fieild': 'value', }
    return json.dumps(a)
