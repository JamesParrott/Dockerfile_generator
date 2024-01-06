import sys
import argparse
import pathlib
import types
from typing import Iterable, Callable
import itertools

import jinja2


CONFIGS_DIR = pathlib.Path(__file__).parent / 'configs'
TEMPLATES_DIR = pathlib.Path(__file__).parent / 'templates'
DEFAULT_TEMPLATE = TEMPLATES_DIR / 'Dockerfile.jinja'


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

# Lazy imports.  
# Dots need to be included in key for simple ext searcher below.
CONFIG_IMPORTERS = types.MappingProxyType(
                      {'.json' : _get_json_importer,
                       '.toml' : _get_toml_importer,
                      }
                     )


def _config_dict(
    config: str,
    encoding: str = 'utf8',
    )-> dict:
    if config in BUILT_IN_CONFIGS:
        config_path = CONFIGS_DIR / BUILT_IN_CONFIGS[config]
    else:
        
        error_msg = ''

        for ext in itertools.chain(CONFIG_IMPORTERS.keys(), ['']):
            config_path = pathlib.Path(config + ext)
            if config_path.exists() and config_path.is_file():
                break
        else:

            if not config_path.exists():
                error_msg = f'No file found: {config=}. '
            elif not config_path.is_file():
                error_msg = f'{config=} is not file (is it a directory?). ' 
                
            error_msg = (f'{error_msg} config must be a file '
                         f'or in {", ".join(BUILT_IN_CONFIGS)} '
                        )
            raise FileNotFoundError(error_msg)

    ext = config_path.suffix
    if ext.lower() not in CONFIG_IMPORTERS:
        raise NotImplementedError(
            f'Unsupported file extension: {ext} for {config=}. '
            f'Supported extensions: {", ".join(CONFIG_IMPORTERS)} (case insensitive)'
            ) 

    importer = CONFIG_IMPORTERS[ext]()

    with config_path.open('rt', encoding=encoding) as f:
        return importer(f)['config']


def _get_loader(
    template: str | pathlib.Path = DEFAULT_TEMPLATE,
    ) -> jinja2.BaseLoader | None:
    
    path = pathlib.Path(template)

    if path.is_file():
        return jinja2.FileSystemLoader(path.parent)

    return None


def _get_template(
    environment: jinja2.Environment = None,
    # template could be a file path, str of a template, or any arg accepted by get_template
    template: str | pathlib.Path = DEFAULT_TEMPLATE,  
    loader: jinja2.BaseLoader = None,
    **kwargs
    ):

    # _get_loader returns None if template is not 
    # a path to an existing file 
    loader = loader or _get_loader(template)


    environment = environment or jinja2.Environment(
                                            loader = loader,
                                            extensions = extensions,
                                            )

    if loader is None:
        # template not a path to an existing file
        return environment.from_string(str(template))

    return environment.get_template(str(template))


def render(
    config: str,
    params: Iterable[str],
    encoding: str = 'utf8',
    template: str | pathlib.Path = DEFAULT_TEMPLATE,
    template_obj: jinja2.Template = None,
    environment: jinja2.Environment = None,
    extensions = ['jinja2.ext.do',  # So statements need not return values.
                  'jinja2.ext.loopcontrols'], # For continue and break
    loader: jinja2.BaseLoader = None,
    **kwargs
    ) -> str:

    config_dict = _config_dict(config, encoding)

    # For compatibility with jinja2-cli's -d option, the Params are 
    # provided as a space separated string 
    ws_separated_params = ' '.join(params)


    template_obj = template_obj or _get_template(
                                            environment = environment,
                                            loader = loader,
                                            template = template,
                                            )

    return template_obj.render(
                config = config_dict,
                params = ws_separated_params,
                **kwargs
                )

# for backward compatibility
rendered_Dockerfile = render


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
        '--template',
        help = ('The Dockerfile template chosen, corresponding to the  '
                'configuration in config.  '
                f'Default: {DEFAULT_TEMPLATE} '
               ),
        type=str,
        default = DEFAULT_TEMPLATE
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

    print(render(**vars(namespace)))

    return 0


if __name__ == '__main__':
    sys.exit(main())