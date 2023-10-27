


import subprocess
import tempfile
import pathlib

TMP_DIR = pathlib.Path(tempfile.gettempdir()) 
TMP_DOCKERFILE_DIR = TMP_DIR / 'Dockerfile_generator' / 'tmp_dockerfiles'
TMP_DOCKERFILE_DIR.mkdir(exist_ok=True, parents=True)
TMP_DOCKERFILE_PATH = TMP_DOCKERFILE_DIR / 'Dockerfile'


def _generate_Dockerfile(
    config: pathlib.Path | str ='configs/debian.json',
    params='ash dash zsh heirloom fish elvish',
    docker_file_path: pathlib.Path = TMP_DOCKERFILE_PATH,
    ) -> tuple[str, subprocess.CompletedProcess, pathlib.Path]:
    
    # cmd = f'jinja2 Dockerfile.jinja {str(config)} --format=json -D params="{params}" > {docker_file_path}'
    cmd = f'dockerfile_generator {str(config)} {params} > {docker_file_path}'
        

    print(cmd)

    result = subprocess.run(
        cmd,
        shell = True,
        stderr = subprocess.STDOUT,
        stdout = subprocess.PIPE,
        )
    output = result.stdout.decode(encoding = 'utf8')

    return output, result, docker_file_path, 
