import subprocess
import warnings
import re
import tempfile
import pathlib

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


def _generate_Dockerfile_and_run_hadolint_on_it(
    config='debian',
    pkgs='ash dash zsh heirloom fish elvish',
    ) -> tuple[str, subprocess.CompletedProcess]:
    
    subprocess.run(
        f'jinja2 Dockerfile.jinja configs/{config}.json --format=json -D packages={pkgs} > {TMP_DOCKERFILE_PATH}',
        shell = True,
         )

    result = subprocess.run(f'hadolint {TMP_DOCKERFILE_PATH}'
                           ,shell = True
                           ,stderr = subprocess.STDOUT
                           ,stdout = subprocess.PIPE
                           )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result


@pytest.mark.parametrize('config, pkgs, expected_output', [('debian', 'ash dash zsh heirloom fish elvish', '')])
def test_hadolint_Dockerfile(config, pkgs, expected_output):
    actual_output, result = _generate_Dockerfile_and_run_hadolint_on_it(config, pkgs)
    assert result.returncode == 0
    #assert actual_output == expected_output