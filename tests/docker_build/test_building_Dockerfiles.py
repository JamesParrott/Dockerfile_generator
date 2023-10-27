import subprocess
import pathlib
import pytest

from ..test_case_parameters import (_generate_test_data,
                                    _only_all_param_tests,
                                    )
from ..test_cli import (_generate_Dockerfile,
                        TMP_DOCKERFILE_PATH,
                        )





def _build_image_from(
    dockerfile_path: pathlib.Path = TMP_DOCKERFILE_PATH,
    tag: str = None
    ) -> tuple[str, subprocess.CompletedProcess, pathlib.Path]:

    if tag:
        cmd = f'docker build --no-cache -t {tag} {dockerfile_path}'
    else:
        cmd = f'docker build --no-cache {dockerfile_path}'

    print(cmd)

    result = subprocess.run(cmd,
                            shell = True,
                            stderr = subprocess.STDOUT,
                            stdout = subprocess.PIPE,
                            )
    output = result.stdout.decode(encoding = 'utf8')
    return output, result, dockerfile_path





@pytest.mark.parametrize('config_path, params, __', _only_all_param_tests()) #[('configs/debian', 'ash dash zsh heirloom fish elvish')])
def test_generating_and_building_Dockerfiles(config_path, params, __):

    print(f'{config_path=}, {params=}')

    df_gen_output, df_gen_result, dockerfile_path = _generate_Dockerfile(config_path, params)

    config = str(config_path).replace("/","_").replace("\\","_").replace(".","_")
    params_str = params.replace(" ","_")

    # TODO: Ensure valid tag name
    # The tag must be valid ASCII and can contain lowercase and uppercase letters, digits, underscores, periods, 
    # and hyphens. It cannot start with a period or hyphen and must be no longer than 128 characters. 
    # https://docs.docker.com/engine/reference/commandline/tag/

    tag = f'dockerfile_generator_test_image_{config}_{params_str}'.replace('+','p')

    docker_output, result, __ = _build_image_from(
        dockerfile_path.parent,
        tag,
        )

    assert df_gen_result.returncode == 0
    assert result.returncode == 0
