import os

class Settings (object):

    def __init__(self):
        self._poisoner = None
        self.path = os.path.expanduser("~/.polymorph")

        # TODO; Just a PoC with hardcoded dirs, integrate some kind of settings
        # TODO; Ensure that all App reuse this iface._polym_path instead of redefine it
        # Iterate all paths down the "~/.polymorph" to initialize it if needed
        _conditions_path = ["", "conditions", "conditions/executions", "conditions/postconditions", "conditions/preconditions"]
        for _path in _conditions_path:
            _full_path = "{}/{}".format(self.path, _path)
            if not os.path.exists(_full_path):
                os.makedirs(_full_path)
