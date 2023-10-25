import os
import subprocess
import warnings
import re

import pytest

from ..test_case_parameters import (_generate_test_data,
                        VERSION_PINNING_RULES,
                        RULES_TO_ALWAYS_IGNORE
                       )
from ..test_jinja2_cli import (_generate_Dockerfile,
                               TMP_DOCKERFILE_PATH
                              )

HADOLINT_EXECUTABLE = ENFORCE_ALL_VERSION_PINNING_WARNINGS = os.getenv('HADOLINT_EXECUTABLE', 'hadolint')

HADOLINT_VERSION = '2.12.0'

result = subprocess.run([HADOLINT_EXECUTABLE,'--version'], capture_output=True)

output = result.stdout.decode()

match = re.search(r'\d+\.\d+\.\d+', output)

if match[0] != HADOLINT_VERSION:
    warnings.warn(f'Dockerfile_generator is currently tested '
                  f'using Hadolint version {HADOLINT_VERSION}. '
                  f'Version: {match[0]} of Hadolint found '
                  f'on the path of this environment. '
                 )






def _run_hadolint(
    dockerfile_path = TMP_DOCKERFILE_PATH,
    rules_to_ignore: set[str] = VERSION_PINNING_RULES | RULES_TO_ALWAYS_IGNORE,
    ):


    cmd = f'{HADOLINT_EXECUTABLE} --ignore {" --ignore ".join(rules_to_ignore)}  {dockerfile_path}'

    print(cmd)

    result = subprocess.run(cmd,
                            shell = True,
                            stderr = subprocess.STDOUT,
                            stdout = subprocess.PIPE,
                            )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result, dockerfile_path



@pytest.mark.parametrize('config, params, rules_to_ignore', _generate_test_data()) #[('configs/debian', 'ash dash zsh heirloom fish elvish')])
def test_config(config, params, rules_to_ignore):

    df_gen_output, df_gen_result, dockerfile_path = _generate_Dockerfile(config, params)

    hadolint_output, result, ___ = _run_hadolint(dockerfile_path, rules_to_ignore)

    assert result.returncode == 0
    assert 'warning' not in hadolint_output.lower()