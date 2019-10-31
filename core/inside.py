import sys


def insideMaya():
    inside = True
    if not "maya.api.maya" in sys.modules:
        inside = False

    try:
        from maya import cmds
    except:
        inside = False

    return inside
