# Dockerfile_generator

## In Browser
Pyodide may need a minute to load and is almost a [20 MB download](https://jamesparrott.github.io/Dockerfile_generator/) 

`dockerfile_generator debian ash dash zsh heirloom fish elvish`

Only the default configs are supported for now.

## Installation with Python
Either:
 - Install pipx, e.g. `pip install pipx`
 - `pipx install dockerfile_generator`

Or
 - Make a venv and activate it.
 - `pip install dockerfile_generator` 


## Example command line use
`dockerfile_generator debian ash dash zsh heirloom fish elvish > Dockerfile`

## Features
 - Multi-stage builds if needed.  The only requirements for them to work nicely together and for Dockerfile_generator to generate  a correct base image tag and `COPY from= ` command are: 
   - The build stage is based on the same base image as the final
     runner stage
   - build stage stub templates must copy their build artifacts to a copy of the target directory in the runner root, as a sub directory of `{{ binaries_dir }}`.
   - User must supply compilation instructions.
 - Special tags are automatically applied, e.g. for extra repos, if any params are to be installed that require Alpine Edge. 
 - Dockerfiles produced follow [Docker's recommendations](https://docs.docker.com/develop/develop-images/guidelines/), and have been tested by linting with `hadolint` and building some in CI.
 - Version pinning support (not in the default config images - but see `/tests/pinned_versions/alpine_pinned.json` for an example).  See testing notes.
 - Labels.
 - User config files can support arbitrary docker commands by referring to sub templates.  Parameters are not limited to params to be installed.
 - Config files are supplied for Alpine, Debian and Ubuntu images with apk and apt-get.  You no longer have to remember the
 apt-get "incantation".
   - Base image and Base tag args for maintainability.
   - Commands ordered from most common to least common, to make best use of Docker's build cache.

## Description
Containerisation is incredibly powerful.  It is worth any programmer's time to learn how to use it, as is the basics of Dockerfiles.  dockerfile_generator can ease the barrier of entry, and let people get up and running quickly, especially those who just want an image for particular distro with their choice of apps installed.

Dockerfile_generator provides a set of nested Jinja 2 templates, that are configurable (e.g. by JSON files), that match a 
required data structure, that describe the possible contents and purpose of the Dockerfile.  The config files are reusable, and can refer to Jinja 2 sub-templates, e.g. that describe the best practise use of a particular package manager
This allows multiple Dockerfiles to be generated from the same configuration, for parametric testing.
A configuration can determine which parameters to do something with on the command line (and which default command to use 
with unrecognised parameters).  The order of the commands can be adjusted, e.g. to manage the use of Docker's build cache.
Parameters are most likely to be the names of packages to be installed with a package manager, but could be any arbitrary string, or none (the empty string), and Commands need not be 'RUN' Commands. Special commands that necessitate multi-stage Dockerfiles only when their param is provided, are also supported by referring to a Jinja 2 sub-template or a build script (e.g. .sh), for packages to be built from source.  No effort is made to validate extra custom stages. So e.g. to guarantee compilation the user must tell Dockerfile_generator exactly what to do, either in the sub-template or build script, and refer to it against a parameter in their configuration.
The outputs from Dockerfile_generator with the included config files, are inteded to reflect the best practise in writing Dockerfiles
and pass linting by Hadolint (with some rules relaxed, described below).  An image has been successfully built with Docker from each provided config file, for the Dockerfile generated from it when all supported parameters are provided.

## Alternatives
Dockerfiles for some official images are already generated using an [alternative templating system](https://github.com/docker-library/python/blob/master/Dockerfile-linux.template) to Jinja 2, which is rendered using Bash scripts and an [Awk script](https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk).  



## Config files

Toml is supported where tomllib is available (>= Python 3.11)

### 'JSON' Example.
```
{"config" :  # Required boilerplate.  Makes the code tidier.
{
"base_image" : the name (and owner if any) of the base image, e.g. "alpine"
 "base_tag" : the base image tag, e.g. "3.18.2"
 "need_special_tags" : a mapping of commands from below, to alternative image tags.  If any of a command's supported parameters are present
 in the rendering args, the image tag is used to override "base_tag" e.g. {"install_from_testing" : "edge"},

 "builder_default_binaries_dir": the dir in the build stage the binaries will be copied from (and to, for stages after the first), e.g. "/tmp/runner_root_dir" 
 "runner_binaries_dir" : the dir in the build stage the binaries will be copied to, e.g. "/",

 "build_stages" : a mapping of param names to mappings configuring build stages that will added to the Dockerfile if their param is in the render args.
 {
    "rc" :       {"build_script" : The path of a file in the tree where Dockerfile_generator was called (e.g. a Bash script containing compilation commands) to be copied into the stage and called, if the next argument is omitted, e.g. "",
                  "file_path" : The path of a sub template file defining the build stage for this param, e.g. "./build_stage_templates/alpine/rc/Dockerfile_plan9_build_stage.jinja"
                 }
 },

 "commands" : { a mapping of command names to mappings configuring commands, these sub mappings containing "supported_parameters".  If a param
 in the render args is in a command (in commands_order)'s "supported_parameters", the information in the sub mapping is used to add the corresponding command to the runner stage.
      "install_from_main_and_community" : {
       "string" : string defining the command to be renderred verbatim if the next argument is omitted, e.g. "CMD ["python3"]" 
       "file_path" : File path to a sub template for this command, e.g. "/command_templates/apk.jinja",
       "supported_parameters" : a list or mapping containining the params, that if included in the render args, will cause this command to be added to the Dockerfile, e.g. ["ash", "dash", "zsh"].  Params can appear in "supported_parameters" for more than one command.  Params in a list are rendered as themselves.   Params in a mapping have their value rendered if a string, or the last value in an array rendered.  This enables version pinning to be configured, while keeping short package names or even aliases, in the render args.
         },
            ...
                              },

 "commands_order" : an array of strings defining the order the commands should appear in (if they have supported params in the render args) in the runner stage.  The special name "build_stages" refers to the position of the command copying the binaries from the last build stage.
 This order can be different to the order of the commands in commands, in order to control Docker image cache invalidation.  
 list of["install_from_main_and_community",
                     "build_stages"
                    ],
 "unused_parameters_command" : The name of the default command to pass an unrecognised param in the render args to, that doesn't, appear in any command in commands_order's "supported_parameters", e.g. "install_from_main_and_community"
}
}
```
## Development

Other than a small CLI wrapper and the tests, the code is pure Jinja2 Templates plus JSON config files.  It works well - it generates Dockerfiles that Hadolint only has minor differences of opinion with me about.  Following a couple of months break from it, and after having worked on Dockerfile_generator again, I now fully appreciate the wisdom of not implementing business logic in a templating language.  The templates contain the hardest to maintain, and outright ugliest code I've ever written!  

However, the self-contained templates have one major advantage.  Advanced users and devs alike (that are willing to learn the basics of Jinja 2), are able to access vastly more flexibility in how they use any part of it, by the native mechanisms of Jinja 2 alone.  Namely: imports, template inheritance, overrides, and includes.   

In future the CLI wrapper could be developed to include more of the logic, for example to send requests to a package manager API to check the packages to be installed are correct. 

## Testing

### Linting tests
`tox` to test using hadolint

### Dockerfile build tests
- start the docker daemon, e.g. by opening Docker Desktop.
`tox -e docker_build-py311` to build test dockerfiles (can take ~20 minutes or longer)

### Relaxation of Hadolint's version pinning rules.

Dockerfile_generator was written to allow parametric testing, and to programmatically vary properties of test environments defined by Dockerfiles.  Other applications of Dockerfiles prioritise reproducible builds, and recommend pinning versions of apps installed in Containers (and base Dockerfile image versions). 

Parametric integration or acceptance testing enables a project to determine which third party params (e.g. shells) it is possible to support.  In this context, one of the goals of testing is precisely to discover if an unpinned external dependency breaks the project.  Users will experience exactly the same breakage.  

This was the reason for which Dockerfile_generator was written, therefore the default configs do not specify pinned versions in the provided example apps.  There is an exclusion in the testing - it is assumed the user does not want version pinning.  

If you require version pinning (for reproducibility, better cacheing etc.) Dockerfile_generator does support this.  Instead of picking one set of versions (for all the shells in the example configs) and forcing everyone to use them, the specific version numbers to be pinned at (or other constraints) must be chosen by each user, and added to their config file.  Version constraints can either be
included directly in the param identifier strings in supported_parameters, or more conveniently by setting supported_parameters to be a mapping of command line aliases to the actual strings to be rendered.  

Reproducible builds, containing external dependencies, may still break e.g. if a repository being relied on drops, or an author yanks the pinned version of a package (so for true reproducibility,  self-hosting and perhaps also building from source is also required). 
