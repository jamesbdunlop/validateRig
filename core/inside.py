#  Copyright (c) 2019.  James Dunlop
import sys


def insideMaya():
    # type: () -> Bool
    inside = True
    if not "maya.api.maya" in sys.modules:
        inside = False

    try:
        from maya import cmds
    except:
        inside = False

    return inside
