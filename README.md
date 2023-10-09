# Dockerfile generator

## Installation
 - Install Python >= 3.7 from [python.org]
 - Clone the repo where you want to install it `git clone --depth=1 --branch main https://github.com/JamesParrott/Dockerfile_generator`
 - Make a venv and activate it.
 - `pip install jinja2-cli`

## Usage
`jinja2 Dockerfile.jinja configs/debian.json --format=json -D packages="ash dash zsh heirloom fish elvish" > Dockerfile`

## Features
 - Multi-stage builds if needed.  The only requirement for them to work nicely together and for Dockerfile_generator to generate  correct base image and `COPY from= ` command are: 
   - The build stage is based on the same base image as the final
     runner stage
   - build stage stub templates must copy their build artifacts to a copy of the target directory in the runner root, as a sub directory of `{{ binaries_dir }}`.
   - User must supply compilation instructions.
 - Special tags are automatically applied, e.g. for extra repos, if any packages are to be installed that require Alpine Edge. 
 - Dockerfiles produces have been designed to follow [Docker's recommendations](https://docs.docker.com/develop/develop-images/guidelines/), and have been tested by linting with `hadolint` and building some in CI.
 - Version pinning (*).
 - Labels.
 - User config files can support arbitrary docker commands by referring to sub templates.  Parameters are not limited to packages to be installed.
 - Config files are supplied for Alpine, Debian and Ubuntu images with apk and apt-get.  You no longer have to remember the
 apt-get "incantation.
   - Base image and Base tag args for maintainability.
   - Commands ordered from most common to least common, to make
     best use of Docker's build cache.

(*) Not in the default config images - see `/tests/pinned_versions`.  For my use case, I amd using Dockerfile_generator in a parametric testing process.  I want to know if an external dependency from an unpinned version breaks an app, as users will also be using getting that broken dependency.  Alternatively, if you require version pinning for reproducibility, Dockerfile_generator supports that.  But tests
based on this have an external dependency, so still may break.  Such environments are only be reproducible in practise, until a repository being relied on yanks the required version of a package (so perhaps building from source or self-hosting is then required too).  Let me know what your usage cases are, and I'll see how much demand there is for a versioning system in Python, that does more than read a version requirements string from the config file (e.g. calling package manager APIs, or even Dockerfile test builds)

## Development
This Branch is for posterity, the historical record, and published as a warning to others...

After working on this project again after a gap of a couple of months break, I now fully appreciate the wisdom of not implementing business logic in a templating language...  

This branch is pure Jinja2 Templates plus Json config files (so theoretically no Python is needed, just a Jinja 2 renderer).  It works by and large - it generates Dockerfiles that Hadolint only has minor differences of opinion with me about.  A refactor would be the best long term solution, but the project currently more than fulfills my own needs and passes plenty of tests.

But it contains the hardest to maintain, and outright ugliest code I've ever written.