

def set_version(request):
    return {"version": get_version()}


def get_version():
    with open('VERSION') as f:
        return f.read().strip()
