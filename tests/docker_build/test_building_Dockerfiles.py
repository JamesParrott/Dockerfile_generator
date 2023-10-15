import subprocess
import pathlib
import pytest

from ..fixtures import _generate_test_data, _generate_Dockerfile, TMP_DOCKERFILE_PATH





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


@pytest.mark.parametrize('config, params, __', _generate_test_data(n=0)) #[('configs/debian', 'ash dash zsh heirloom fish elvish')])
def test_generating_and_building_Dockerfiles(config, params, __):

    print(f'{config=}, {params=}')

    df_gen_output, df_gen_result, dockerfile_path = _generate_Dockerfile(config, params)

    config_str = str(config).replace("/","_").replace("\\","_").replace(".","_")
    params_str = params.replace(" ","_")

    docker_output, result, __ = _build_image_from(
        dockerfile_path,
        f'dockerfile_generator_test_image_{config_str}_{params_str}'
        )

    assert df_gen_result.returncode == 0
    assert 'warning' not in docker_output.lower()