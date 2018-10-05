import os

class Settings (object):

    def __init__(self):
        self._poisoner = None
        self.path = os.path.expanduser("~/.polymorph")

        self.paths = {
            "": self.path,
            "conditions": "{}/conditions".format(self.path),
            "preconditions": "{}/conditions/preconditions".format(self.path),
            "postconditions": "{}/conditions/postconditions".format(self.path),
            "executions": "{}/conditions/executions".format(self.path),
        }

        # TODO; Ensure that all App reuse this iface._polym_path instead of redefine it
        for _path in self.paths.values():
            _full_path = "{}/{}".format(self.path, _path)
            if not os.path.exists(_full_path):
                os.makedirs(_full_path)
