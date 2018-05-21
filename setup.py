# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from distutils.core import setup
import platform

REQUIRES = [
    'scapy',
    'pyshark',
    'dill',
    'hexdump',
    'termcolor',
    'construct',
    'netaddr',
    'prompt-toolkit==2.0.0',
]

if platform.system() == "Linux":
    SCRIPTS = ['bin/polymorph', 'bin/phcli']
    REQUIRES += ['NetfilterQueue']
elif platform.system() == "Windows":
    SCRIPTS = ['bin/polymorph.bat', 'bin/polymorph']
    REQUIRES += ['pydivert']

setup(
    name="polymorph",
    version="1.0.1",
    packages=[
        "polymorph",
        "polymorph/UI",
        "polymorph/conditions",
        "polymorph/conditions/preconditions",
        "polymorph/conditions/executions",
        "polymorph/conditions/postconditions",
        "polymorph/spoofs",
        "polymorph/CLI",
    ],
    scripts=SCRIPTS,
    license="MIT",
    description="A real time network packet manipulation framework",
    platforms=["Linux", "Windows"],
    url="https://github.com/shramos/polymorph",
    author="Santiago Hernandez Ramos",
    author_email="shramos@protonmail.com",
    install_requires=REQUIRES,
    dependency_links=[
        'https://github.com/jonathanslenders/python-prompt-toolkit/tarball/2.0/#egg=prompt-toolkit-2.0.0'],
    keywords=[
        'network',
        'packet',
        'modification',
        'real-time',
        'real',
        'time',
        'manipulation',
        'modify',
        'on-the-fly',
        'crafter'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
