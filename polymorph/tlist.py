# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import itertools


class TList:
    """This class provides a container to store a set of templates, with some
    methods that facilitate access to them."""

    def __init__(self, tgen, length, names):
        """Initialization method of the class.

        Parameters
        ----------
        tgen : :obj:`TGenerator`
            A templates generator.
        length : int
            The number of `Template`.
        names : :obj:`list` of str
            The name of all the `Template`.

        """
        self._tgen = tgen
        self._len = length
        self._names = names
        self._templates = []

    def __getitem__(self, i):
        """This method generates the templates from the generator as long as
        it has not been previously generated. In the event that it has been
        generated, it will only be accessed."""
        if i == -1:
            i = self._len - 1
        if i >= self._len:
            raise IndexError
        elif i - len(self._templates) < 0:
            return self._templates[i]
        else:
            for item in itertools.islice(self._tgen, i - len(self._templates) + 1):
                name = self._name(item)
                item.name = name
                self._templates.append(item)
                self._names[self._templates.index(item)] = name
            return self._templates[-1]

    def __len__(self):
        return self._len

    def __repr__(self):
        return "<tlist.TemplatesList: " + \
            str(self._len) + " templates>"

    def write(self, path="../templates"):
        """Writes `TemplateList` to disk.

        Notes
        -----
        Because the templates are generated in execution time when they are
        accessed, if the user has already accessed some, they are not
        generated again, and they are generated from that point.

        Parameters
        ----------
        path : str
            The path where the `Template` will be written.

        """
        self._generate_templates()
        for t in self._templates:
            t.write(path)

    def show(self):
        """Show a list of the templates in the `TList`."""
        i = 0
        for name in self._names:
            name = name.replace(":", ": ")
            name = name.replace("/", " / ")
            print("%i %s" % (i, name))
            i += 1
        print("")

    def _generate_templates(self):
        """Generates all the remaining templates from the TGenerator."""
        for item in self._tgen:
            self._templates.append(item)

    @staticmethod
    def _name(template):
        """Generates a name for each template based on the layers of the
        packet."""
        return 'Template:' + "/".join(template.layernames())

