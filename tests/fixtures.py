
import os
import subprocess
import tempfile
import pathlib
import json
import random
from typing import Iterator

TMP_DIR = pathlib.Path(tempfile.gettempdir()) 
TMP_DOCKERFILE_DIR = TMP_DIR / 'Dockerfile_generator' / 'scratch'
TMP_DOCKERFILE_DIR.mkdir(exist_ok=True, parents=True)
TMP_DOCKERFILE_PATH = TMP_DOCKERFILE_DIR / 'Dockerfile'


ENFORCE_ALL_VERSION_PINNING_WARNINGS = os.getenv('TEST_DOCKERFILE_GENERATOR_ENFORCE_ALL_VERSION_PINNING_WARNINGS', "False") == "True"

VERSION_PINNING_RULES = {'DL3008', 'DL3013', 'DL3016', 'DL3018', 'DL3028',}
RULES_TO_ALWAYS_IGNORE = {'DL3059',}
#                         Apt-get   Pip       Npm       Apk       Gem
# E.g: https://github.com/hadolint/hadolint/wiki/DL3008


def _generate_Dockerfile(
    config: pathlib.Path | str ='configs/debian.json',
    params='ash dash zsh heirloom fish elvish',
    docker_file_path: pathlib.Path = TMP_DOCKERFILE_PATH,
    ) -> tuple[str, subprocess.CompletedProcess, pathlib.Path]:
    
    cmd = f'jinja2 Dockerfile.jinja {str(config)} --format=json -D params="{params}" > {docker_file_path}'
        

    print(cmd)

    result = subprocess.run(
        cmd,
        shell = True,
        stderr = subprocess.STDOUT,
        stdout = subprocess.PIPE,
        )
    output = result.stdout.decode(encoding = 'utf8')

    return output, result, docker_file_path, 




def versioned(pkgs):
    return all(any(c in pkg for c in ('<','>','=')) for pkg in pkgs)


def rules_to_ignore(pkgs):
    if ENFORCE_ALL_VERSION_PINNING_WARNINGS or versioned(pkgs):
        return RULES_TO_ALWAYS_IGNORE
    
    return RULES_TO_ALWAYS_IGNORE | VERSION_PINNING_RULES


def _generate_test_data(a = 2, b = None, n = 10) -> Iterator[tuple[pathlib.Path, str, set[str]]]:
    """ Yields different test data depending on an env variable,
        and on whatever json config files 
        are in the repo.  And ends with n random test cases per config.  
        Set the bool ENFORCE_ALL_VERSION_PINNING_WARNINGS 
        to True to require all
        configs to pass hadolint's version pinning rules.
    """

    for path in pathlib.Path('.').glob('**/*.json'):



        with open(path, 'rt') as f:
            config = json.load(f).get('config', None)

        if config is None:
            continue

        yield path, '', RULES_TO_ALWAYS_IGNORE

        params = [param
                  for command in config.get('commands', {}).values()
                  for param in command.get('supported_parameters', []) 
                 ]

        params.extend(config.get('build_stages', {}))

        if not params: 
            continue

        yield path, ' '.join(params), rules_to_ignore(params)


        for param in params:
            yield path, param, rules_to_ignore([param])


        max_sample_size = len(params) - 1 if b is None else b


        for _ in range(n):
            try:
                k = random.randint(a, max_sample_size)
                sample = random.sample(params, k)
            except ValueError as e:
                print(f'{a=}, {max_sample_size=}, {k=}, {path=}, {b=}')
                raise e
            yield path, sample, rules_to_ignore(sample)