import subprocess
import warnings
import re

import pytest


def _sys_argv_from_args(args: Iterable[str]) -> tuple[str, subprocess.CompletedProcess]:
    
    # 
    result = subprocess.run(f'python -X utf8 args.py {" ".join(args)}'
                           ,shell = True
                           ,stderr=subprocess.STDOUT
                           ,stdout = subprocess.PIPE
                           )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result


HADOLINT_VERSION = '2.12.0'

result = subprocess.run(['hadolint','--version'], capture_output=True)

output = res.stdout.decode()

match = re.search(r'\d+\.\d+\.\d+')

if match[0] != HADOLINT_VERSION:
    warnings.warn(f"Dockerfile_generator is currently tested "
                  f"using Hadolint version {HADOLINT_VERSION}. "
                  f"Version: {} of Hadolint found "
                  f"on the path of this environment. "
                 )





def _generate_Dockerfile_and_run_hadolint_on_it(config, pkgs, output) -> tuple[str, subprocess.CompletedProcess]:
    
    result = subprocess.run(HADOLINT_TEST_CMD.format(config=config, params=params)
                           ,shell = True
                           ,stderr=subprocess.STDOUT
                           ,stdout = subprocess.PIPE
                           )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result


@pytest.mark.parametrize("config, pkgs, expected_output", [])
def test_hadolint_Dockerfile(config, pkgs, expected_output):
    actual_output = _generate_Dockerfile_and_run_hadolint_on_it(config, pkgs, output)
    assert actual_output == expected_output