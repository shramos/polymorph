# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

class CommandParser(object):
    def __init__(self, options):
        self._it = None
        self._opts = options
        self._args = {e: options[e]["default"]
                      for e in options}

    def parse(self, command):
        self._it = iter(command[1:])
        for c in self._it:
            try:
                # Handle options that receive bool values
                if self._opts[c]["type"] is bool:
                    self._args[c] = True
                # Handle options that receive int values
                if self._opts[c]["type"] is int:
                    value = next(self._it)
                    parse_val = CommandParser._parse_int(value)
                    if parse_val:
                        self._args[c] = parse_val
                    else:
                        return None
                # Handle options that receive str values
                elif self._opts[c]["type"] is str:
                    value = next(self._it)
                    parse_val = self._parse_string(value)
                    if parse_val:
                        self._args[c] = parse_val
                    else:
                        return None
            # Handles wrong options
            except (KeyError, StopIteration) as e:
                return None
        return self._args

    @staticmethod
    def _parse_int(value):
        if value.isdecimal():
            return int(value)
        else:
            return None

    def _parse_string(self, value):
        if value[0] == '"':
            f = value
            while value[-1] != '"':
                try:
                    value = next(self._it)
                    f += " " + value
                except StopIteration:
                    return None
            return f.strip('"')
        else:
            if value[-1] != '"':
                return value
            return None
