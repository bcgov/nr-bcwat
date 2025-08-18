# Software Version Control Process

## Introduction

This document attempts to detail the processes required for upgrading versions of the software (NR-BCWAT), and to detail the software versioning/branching process.

## Software Versioning

[NR-BCWAT](https://github.com/bcgov/NR-BCWAT/) is developed with git branching as the main component to allow for Pull Requests to add features into several branches. In order to implement a feature or fix a bug, you will need to create a branch which has the issue number in the branch name. The branch name should summarize and describe the changes which will be implemented in the branch - for example, for a task to document the software upgrade and versioning processes which has an issue ID of 411, you could make a branch like so:

```bash
git checkout -b 411-version-control-process
```
