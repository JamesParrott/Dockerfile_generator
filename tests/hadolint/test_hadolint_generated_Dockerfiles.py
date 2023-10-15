import subprocess
import warnings
import re

import pytest

from ..fixtures import _generate_test_data, _generate_Dockerfile, VERSION_PINNING_RULES, TMP_DOCKERFILE_PATH


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






def _run_hadolint(
    dockerfile_path = TMP_DOCKERFILE_PATH,
    enforce_version_pinning_warnings = False
    ):

    if enforce_version_pinning_warnings or not VERSION_PINNING_RULES:
        cmd = f'hadolint {dockerfile_path}'
    else:
        cmd = f'hadolint --ignore {" --ignore ".join(VERSION_PINNING_RULES)}  {dockerfile_path}'

    result = subprocess.run(cmd,
                            shell = True,
                            stderr = subprocess.STDOUT,
                            stdout = subprocess.PIPE,
                            )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result, dockerfile_path


@pytest.mark.skip(reason="Takes too long")
@pytest.mark.parametrize('config, params, enforce_version_pinning_warnings', _generate_test_data()) #[('configs/debian', 'ash dash zsh heirloom fish elvish')])
def test_config(config, params, enforce_version_pinning_warnings):

    df_gen_output, df_gen_result, dockerfile_path = _generate_Dockerfile(config, params)

    hadolint_output, result, ___ = _run_hadolint(dockerfile_path, enforce_version_pinning_warnings)

    assert result.returncode == 0
    assert 'warning' not in hadolint_output.lower()