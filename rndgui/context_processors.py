

def get_version(request):
    with open('VERSION') as f:
        version = f.read().strip()
    return {"version": version}
