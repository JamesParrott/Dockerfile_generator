import os
import subprocess
import warnings
import re
import tempfile
import pathlib
import random
import json

import pytest



# def _sys_argv_from_args(args: Iterable[str]) -> tuple[str, subprocess.CompletedProcess]:
    
#     # 
#     result = subprocess.run(f'python -X utf8 args.py {' '.join(args)}'
#                            ,shell = True
#                            ,stderr=subprocess.STDOUT
#                            ,stdout = subprocess.PIPE
#                            )
#     output = result.stdout.decode(encoding = 'utf8')
#     return output, result


HADOLINT_VERSION = '2.12.0'

result = subprocess.run(['hadolint','--version'], capture_output=True)

output = result.stdout.decode()

match = re.search(r'\d+\.\d+\.\d+', output)

if match[0] != HADOLINT_VERSION:
    warnings.warn(f'Dockerfile_generator is currently tested '
                  f'using Hadolint version {HADOLINT_VERSION}. '
                  f'Version: {match[0]} of Hadolint found '
                  f'on the path of this environment. '
                 )

TMP_DIR = pathlib.Path(tempfile.gettempdir()) 
TMP_DOCKERFILE_DIR = TMP_DIR / 'Dockerfile_generator' / 'scratch'
TMP_DOCKERFILE_DIR.mkdir(exist_ok=True, parents=True)
TMP_DOCKERFILE_PATH = TMP_DOCKERFILE_DIR / 'Dockerfile'


ENFORCE_ALL_VERSION_PINNING_WARNINGS = os.getenv('TEST_DOCKERFILE_GENERATOR_ENFORCE_ALL_VERSION_PINNING_WARNINGS', "False") == "True"

VERSION_PINNING_RULES = ('DL3008', 'DL3013', 'DL3016', 'DL3018', 'DL3028')
#                         Apt-get   Pip       Npm       Apk       Gem
# E.g: https://github.com/hadolint/hadolint/wiki/DL3008

def _generate_Dockerfile_and_run_hadolint_on_it(
    config='configs/debian.json',
    params='ash dash zsh heirloom fish elvish',
    enforce_version_pinning_warnings = False,
    ) -> tuple[str, subprocess.CompletedProcess]:
    
    subprocess.run(
        f'jinja2 Dockerfile.jinja {config} --format=json -D params={params} > {TMP_DOCKERFILE_PATH}',
        shell = True,
         )

    if enforce_version_pinning_warnings or not VERSION_PINNING_RULES:
        cmd = f'hadolint {TMP_DOCKERFILE_PATH}'
    else:
        cmd = f'hadolint --ignore {" --ignore ".join(VERSION_PINNING_RULES)}  {TMP_DOCKERFILE_PATH}'

    result = subprocess.run(cmd,
                            shell = True,
                            stderr = subprocess.STDOUT,
                            stdout = subprocess.PIPE,
                            )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result


def versioned(pkgs):
    return all(any(c in pkg for c in ('<','>','=')) for pkg in pkgs)


def _generate_test_data(a = 2, b = None, n = 10):
    for path in pathlib.Path('.').glob('**/*.json'):



        with open(path, 'rt') as f:
            config = json.load(f).get('config', None)

        if config is None:
            continue

        yield str(path), '', True

        params = [param
                  for command in config.get('commands', {}).values()
                  for param in command.get('supported_parameters', []) 
                 ]

        if not params: 
            continue

        yield path, ' '.join(params), ENFORCE_ALL_VERSION_PINNING_WARNINGS or versioned(params)

        for param in params:
            yield path, param, ENFORCE_ALL_VERSION_PINNING_WARNINGS or versioned([param])


        max_sample_size = len(params) - 1 if b is None else b


        for _ in range(n):
            try:
                k = random.randint(a, max_sample_size)
                sample = random.sample(params, k)
            except ValueError as e:
                print(f'{a=}, {max_sample_size=}, {k=}, {path=}, {b=}')
                raise e
            yield path, sample, ENFORCE_ALL_VERSION_PINNING_WARNINGS or versioned(sample)




@pytest.mark.parametrize('config, params, enforce_version_pinning_warnings', _generate_test_data()) #[('configs/debian', 'ash dash zsh heirloom fish elvish')])
def test_config(config, params, enforce_version_pinning_warnings):

    actual_output, result = _generate_Dockerfile_and_run_hadolint_on_it(config, params, enforce_version_pinning_warnings)

    assert result.returncode == 0
    assert 'warning' not in actual_output.lower()