import os 

# secrets
def manage_sensitive(name):
    v1 = os.getenv(name)
    secret_fpath = f'/run/secrets/{name}'
    existence = os.path.exists(secret_fpath)
    
    if v1 is not None:
        return v1
    
    if existence:
        v2 = open(secret_fpath).read().rstrip('\n')
        return v2
    
    if not existence:
        print(name)
        return KeyError(f'{name}')