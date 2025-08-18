# Software Version Control Process

## Introduction

This document attempts to detail the processes required for upgrading versions of the software (NR-BCWAT), and to detail the software versioning/branching process, as well as the version number logic for the actual software.

## NR-BCWAT Version Numbers

NR-BCWAT follows the `major.minor.patch` semantic versioning system. To see the current version of NR-BCWAT, please look at the github repository tags here: [NR-BCWAT Tag List](https://github.com/bcgov/nr-bcwat/tags), which are mainly auto-incremented through a github workflow and/or by updating `package.json` in `/client`. The tags are auto incremented when code is pushed to dev, which should only happen after a successful PR, see [Software Versioning](#software-versioning) below.

## Software Versioning

[NR-BCWAT](https://github.com/bcgov/NR-BCWAT/) is developed with git branching as the main method to allow for adding features into several branches via Pull Requests. i.e. In order to implement a feature or fix a bug, you will need to create a new branch from `dev` and, when the feature or bugfix is complete, make a Pull Request to merge back into `dev`. The branch name should summarize and describe the changes which will be implemented in the branch - for example, for a task to document the software upgrade and versioning processes which has an issue ID of 411, you could make a branch like so:

```bash
git checkout -b 411-version-control-process
```

To merge your code back into dev, you would make a PR in github, after which code is reviewed and accepted by peers, and finally merged into `dev`. There are workflows in github to provide continuous deployment of NR-BCWAT when certain criteria are met.

Code should never be committed directly to dev, as any emergency requirements for code should be able to be handled by downgrading a running container to a known-good version, or by merging a bugfix branch.

## Updating Libraries

### Frontend

The frontend is located in `/client` in the top level directory. All following commands assume you have changed to this directory first (`cd client`).

The frontend uses common Javascript libraries and [npm](https://www.npmjs.com/) to manage them.

#### Auditing Javascript Libraries

you should be able to run `npm audit` and `npm audit fix` to install bug fixes or security fixes. This should be done periodically, or at least with every branch.

#### Updating Javascript Libraries

You should also be able to simply request an update to a specific library by running `npm update <example>` or all libraries with `npm update`. This _usually_ will only update non-breaking changes.

#### Anything else

Bigger library updates may be required for security or feature requests. To do so, modify the package.json, or install a specific version using a command like so: `npm install example@version`

#### After Updating/Upgrading Client

Upgrading libraries may require some code changes depending on the library and version installed. If you upgrade the libraries, please run unit tests and perform Q/A on a local development environment before making a PR as described above.

### Backend

The backend is located in `/backend` in the TLD. All following commands assume you have changed to this directory first (`cd backend`).

The backend is written in Python and managed using virtual environments to help prevent tainting the host OS python packages. Foundry Spatial uses `virtualenv`, others should work similarly. Please refer to your virtual environment documentation to understand how to initiate and use your virtual environment.

#### Updating Python Libraries

To list outdated libraries, use the `pip` command which should be automatically installed with your virtual environment: `pip list --outdated`. Using this list, you can install or upgrade specific libraries and initiate tests/QA with the upgraded libraries: `pip install example==version`, or just update the library `pip install -U example`

#### After Updating/Upgrading Backend

Remember to commit your library versions to `requirements.txt`: `pip freeze > requirements.txt`, and commit along with any code changes in a PR, using the system detailed above.

* _Last update: 2025-08-18_
