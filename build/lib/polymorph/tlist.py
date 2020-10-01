# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from termcolor import colored


class TList:
    """This class provides a container to store a set of templates, with some
    methods that facilitate access to them."""

    def __init__(self, tgen, pcap_path=None):
        """Initialization method of the class.

        Parameters
        ----------
        tgen : :obj:`TGenerator`
            A templates generator.
        pcap_path : :obj:str
            Disk path to the pcap file containing the original packets.

        """
        self._names = []
        self._templates = []
        self.pcap_path = pcap_path
        # Generate all the `Template` objects
        self._generate_templates(tgen)

    def __getitem__(self, i):
        """This method generates the templates from the `TGenerator`."""
        return self._templates[i-1]

    def __len__(self):
        return len(self._templates)

    def __repr__(self):
        return "<tlist.TemplatesList: " + \
            str(len(self._templates)) + " templates>"

    def write(self, path="../templates"):
        """Writes `TemplateList` to disk.

        Parameters
        ----------
        path : str
            The path where the `Template` will be written.

        """
        for t in self._templates:
            t.write(path)

    def show(self):
        """Show a list of the templates in the `TList`."""
        i = 1
        for name in self._names:
            print("%i %s" % (i, name))
            i += 1
        print("")

    def _generate_templates(self, tgen):
        """Generates all the templates from the TGenerator."""
        i = 1
        for item in tgen:
            self._templates.append(item)
            self._names.append(self._name(item))
            print("\r[", colored("+", 'green', attrs=['bold']), "] ",
                  "Parsing packet: {0}".format(i), sep='', end='')
            i += 1
        print("\n[", colored("+", 'green', attrs=['bold']), "] ",
              "Parsing complete!", sep='')

    @staticmethod
    def _name(template):
        """Generates a name for each template based on the layers of the
        packet."""
        return template.name
