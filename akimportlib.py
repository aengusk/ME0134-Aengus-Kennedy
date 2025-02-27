import sys

def reload(modl):
    '''
    DOES NOT CURRENTLY WORK
    Uses sys.modules.pop to unimport a module,
    then reimports it. 
    Corresponds to Python's importlib.reload function.
    '''
    modl_name = modl.__name__

    print('modl.__name__ is {}'.format(modl.__name__))

    sys.modules.pop(modl_name, None)

    new_modl = __import__(modl_name)

    globals()[modl_name] = new_modl

    return new_modl