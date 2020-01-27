#  Copyright (c) 2020.  James Dunlop
import sys

def insideMaya():
    # type: () -> Bool

    inside = True
    if not "maya.api.maya" in sys.modules:
        inside = False

    try:
        import maya.cmds as cmds
    except ImportError:
        inside = False

    return inside

