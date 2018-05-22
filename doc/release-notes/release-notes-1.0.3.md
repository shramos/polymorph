## Polymorph Upgrade

```
pip3 install polymorph --upgrade
```

## Major changes

### 1. Prompt-toolkit within the project
A stable version of prompt-toolkit has been introduced into the project because version 2.0.0 is currently in development and in constant change that breaks compatibility with Polymorph.
When prompt-toolkit 2.0.0 is released in a stable version, it will be removed from the project directory and installed as a normal dependency with pip.

### 2. *--process-dependency-lnks* removed in Polymorph installation
Having prompt-toolkit inside the project, among other things, avoid the use of the option --process-dependency-links in the Polymorph installation through pip. This option is deprecated and will be eliminated in the new versions of pip.