# Dockerfile generator

## Installation
 - Install Python >= 3.7 from [python.org]
 - Clone the repo where you want to install it `git clone --depth=1 --branch main https://github.com/JamesParrott/Dockerfile_generator`
 - Make a venv and activate it.
 - `pip install jinja2-cli`

## Usage
`jinja2 Dockerfile.jinja configs/debian.json --format=json -D params="ash dash zsh heirloom fish elvish" > Dockerfile`

## Features
 - Multi-stage builds if needed.  The only requirement for them to work nicely together and for Dockerfile_generator to generate  correct base image and `COPY from= ` command are: 
   - The build stage is based on the same base image as the final
     runner stage
   - build stage stub templates must copy their build artifacts to a copy of the target directory in the runner root, as a sub directory of `{{ binaries_dir }}`.
   - User must supply compilation instructions.
 - Special tags are automatically applied, e.g. for extra repos, if any params are to be installed that require Alpine Edge. 
 - Dockerfiles produces have been designed to follow [Docker's recommendations](https://docs.docker.com/develop/develop-images/guidelines/), and have been tested by linting with `hadolint` and building some in CI.
 - Version pinning support (not in the default config images - but see `/tests/pinned_versions/alpine_pinned.json` for an example).  See testing notes.
 - Labels.
 - User config files can support arbitrary docker commands by referring to sub templates.  Parameters are not limited to params to be installed.
 - Config files are supplied for Alpine, Debian and Ubuntu images with apk and apt-get.  You no longer have to remember the
 apt-get "incantation.
   - Base image and Base tag args for maintainability.
   - Commands ordered from most common to least common, to make
     best use of Docker's build cache.


## Config files
### 'JSON' Example.
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

## Development
This Branch is for posterity, the historical record, and published as a warning to others...

After working on this project again after a gap of a couple of months break, I now fully appreciate the wisdom of not implementing business logic in a templating language...  

This branch is pure Jinja2 Templates plus Json config files (so theoretically no Python is needed, just a Jinja 2 renderer).  It works by and large - it generates Dockerfiles that Hadolint only has minor differences of opinion with me about.  However it does contain the hardest to maintain, and outright ugliest code I've ever written does!

By keeping this project pure Jinja 2, advanced users and devs alike that are willing to learn the basics of Jinja 2, are able to access vastly more flexibility in how they use it, by the native mechanisms of Jinja 2 alone.  Namely: import, template inheritance, overrides, and includes, of any of the sub templates (.jinja files).   

A small Python wrapper (that does what we use Jinja2-cli for, without a cli) more suitable for development of extra features (e.g. sending requests to package manager APIs) or defining the Dockerfile generation logic entirely,

## Testing

### Relaxation of Hadolint's version pinning rules.

Dockerfile_generator was written to allow parametric testing, and to programmatically vary properties of test environments defined by Dockerfiles.  Other applications of Dockerfiles prioritise reproducible builds, and recommend pinning versions of apps installed in Containers (and base Dockerfile image versions). 

Parametric integration or acceptance testing enables a project to determine which third party params (shells) it is possible to support.  In this context, one of the goals of testing is to discover if unpinned external dependencies break the project.  Users will experience exactly the same breakage.  

This was the reason for which Dockerfile_generator was written, therefore the default configs do not specify pinned versions in the provided example apps.  There is an exclusion in the testing - it is assumed the user does not want version pinning.  

If you require version pinning (for reproducibility, better cacheing etc.) Dockerfile_generator does support this.  Instead of picking one set of versions (for all the shells in the example configs) and forcing everyone to use them, the specific version numbers to be pinned at (or other constraints) chosen by each user, must be added to the config file they use, by including these constraints in the strings in supported_parameters, or setting it to be a mapping of aliases to the actual strings to be rendered.  

Reproducible builds, containing external dependencies, may still break e.g. if a repository being relied on drops or an author yanks the pinned version of a package (so perhaps building from source and/or self-hosting is also required). 
