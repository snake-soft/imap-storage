"""compare tool"""


def list_compare(old, new):
    """ compare """
    remove = [x for x in old if x not in new]
    add = [x for x in new if x not in old]
    return remove, add
