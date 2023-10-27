import sys
import argparse
import pathlib
import types
from typing import Iterable

import jinja2


CONFIGS_DIR = pathlib.Path(__file__).parent / 'configs'
TEMPLATE = pathlib.Path(__file__).parent / 'templates' / 'Dockerfile.jinja'

# Make a read only 'dictionary'
BUILT_IN_CONFIGS = types.MappingProxyType(
                      {'alpine' : 'alpine.json',
                       'debian' : 'debian.json',
                       'ubuntu' : 'ubuntu.json',
                       'ubuntu_gcc' : 'ubuntu_gcc.json',
                      }
                     )


def _get_json_importer():
    import json
    return json.load

def _get_toml_importer():
    import tomllib
    return tomllib.load


CONFIG_IMPORTERS = types.MappingProxyType(
                      {'.json' : _get_json_importer,
                       '.toml' : _get_toml_importer,
                      }
                     )


def rendered_Dockerfile(
    config: str,
    params: Iterable[str],
    encoding: str = 'utf8',
    template: str | pathlib.Path = TEMPLATE,
    ):
    
    # For compatibility with jinja2-cli's -d option, the Params are 
    # provided as a space separated string 
    ws_separated_params = ' '.join(params)

    if config in BUILT_IN_CONFIGS:
        path = CONFIGS_DIR / BUILT_IN_CONFIGS[config]
    else:
        path = pathlib.Path(config)

        error_msg = ''

        if not path.exists():
            error_msg = f'No file found: {config=}. '

        if not path.is_file():
            error_msg = f'{config=} is a directory. ' 
        
        if error_msg:
            error_msg = f'{error_msg} config must be a file or in {", ".join(BUILT_IN_CONFIGS)} '
            raise FileNotFoundError(error_msg)

    ext = path.suffix
    if ext.lower() not in CONFIG_IMPORTERS:
        raise NotImplementedError(
            f'Unsupported file extension: {ext} for {config=}. '
            f'Supported extensions: {", ".join(CONFIG_IMPORTERS)} (case insensitive)'
            ) 

    importer = CONFIG_IMPORTERS[ext]

    with path.open('rt', encoding=encoding) as f:
        config_dict = importer(f)

    env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(TEMPLATE.parent)
        )

    template = env.get_template(TEMPLATE.name)

    return template.render(config = config_dict, params = ws_separated_params)


def main(args = sys.argv[1:]):
    
    parser = argparse.ArgumentParser(description=('Parse the config defining '
                                                  'the Dockerfile type, and '
                                                  'the params to render the '
                                                  'particular Dockerfile with')
                                    )
    
    parser.add_argument(
        'config',
        help = ('The configuration for the general type of Dockerfile chosen, '
                'e.g. for an Alpine Linux image, or a Ubuntu image with gcc '
                'must be the path of a config file, or one of the key words '
                f'for a built in config: {", ".join(BUILT_IN_CONFIGS)} '
               ),
        type=str,
        default = 'alpine'
        )
    
    parser.add_argument(
        'params',
        nargs = '*',
        help = ('The params to render the Dockerfile with.  If config=ubuntu_gcc, '
                'then for example params could be the packages to be installed: '
                '"make", "cmake", "gcc", "g++" '
               ),
        type=str
        )

    namespace = parser.parse_args(args)

    print(rendered_Dockerfile(**vars(namespace)))

    return 0


if __name__ == '__main__':
    sys.exit(main())