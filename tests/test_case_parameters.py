
import os
import pathlib
import json
import random
from typing import Iterator



ENFORCE_ALL_VERSION_PINNING_WARNINGS = os.getenv('TEST_DOCKERFILE_GENERATOR_ENFORCE_ALL_VERSION_PINNING_WARNINGS', "False") == "True"

VERSION_PINNING_RULES = {'DL3008', 'DL3013', 'DL3016', 'DL3018', 'DL3028',}
#                         Apt-get   Pip       Npm       Apk       Gem
# E.g: https://github.com/hadolint/hadolint/wiki/DL3008

RULES_TO_ALWAYS_IGNORE = {'DL3059',}


def _contains_constraint(name):
    return any(c in name for c in ('<','>','='))



def _rendered_names_generator_factory(config):
    pkgs_that_could_be_unaliased = []
    alias_dicts = []

    for command_name in config.get('commands_order'):
        command = config.get('commands', {}).get(command_name, {})
        supported_parameters = command.get('supported_parameters', []) 
        if isinstance(supported_parameters, dict):
            alias_dicts.append(supported_parameters)
        else:
            # assert isinstance(supported_parameters, list)
            pkgs_that_could_be_unaliased.extend(supported_parameters)

    def _rendered_names(pkgs):
        for pkg in pkgs:

            recognised = False
            
            if pkg in pkgs_that_could_be_unaliased:
                yield pkg
                recognised = True
            
            for alias_dict in alias_dicts:
                if pkg in alias_dict:
                    yield alias_dict[pkg]
                recognised = True

            if (not recognised and 
                'unused_parameters_command' in config and
                config['unused_parameters_command'] in config['commands_order']):
                yield pkg
    
    return _rendered_names



def _all_versioned(pkgs, config):

    _rendered_names_gen = _rendered_names_generator_factory(config)
    
    return all(not _contains_constraint(name)
               for name in _rendered_names_gen(pkgs)
              )   



def rules_to_ignore(pkgs, config):
    if ENFORCE_ALL_VERSION_PINNING_WARNINGS or _all_versioned(pkgs, config):
        return RULES_TO_ALWAYS_IGNORE
    
    return RULES_TO_ALWAYS_IGNORE | VERSION_PINNING_RULES


def _all_configs_paths_and_params() -> Iterator[dict, tuple[pathlib.Path, list[str]]]:

    for path in pathlib.Path('.').glob('**/*.json'):

        with open(path, 'rt') as f:
            config = json.load(f).get('config', None)

        if config is None:
            continue

        params = [param
                  for command in config.get('commands', {}).values()
                  for param in command.get('supported_parameters', []) 
                 ]

        params.extend(config.get('build_stages', {}))

        yield config, path, params


def _generate_test_data(a = 2, b = None, n = 4) -> Iterator[tuple[pathlib.Path, str, set[str]]]:
    """ Yields different test data depending on an env variable,
        and depending on whatever json config files 
        are in the repo.  And ends with n random test cases per config.  
        Set the bool ENFORCE_ALL_VERSION_PINNING_WARNINGS 
        to True to require all
        configs to pass hadolint's version pinning rules.
    """

    for config, path, params in _all_config_paths_and_params():


        # Test generating Dockerfile with no params
        yield path, '', RULES_TO_ALWAYS_IGNORE

        if not params: 
            continue

        # Test generating Dockerfile with all the params
        yield path, ' '.join(params), rules_to_ignore(params, config)


        # Test generating Dockerfile with each param on its own
        for param in params:
            yield path, param, rules_to_ignore([param], config)


        max_sample_size = len(params) - 1 if b is None else b


        # Test generating Dockerfile with n random selections of between a and b params
        for _ in range(n):
            try:
                k = random.randint(a, max_sample_size)
                sample = random.sample(params, k)
            except ValueError as e:
                print(f'{a=}, {max_sample_size=}, {k=}, {path=}, {b=}')
                raise e
            yield path, ' '.join(sample), rules_to_ignore(sample, config)


def _only_all_param_tests(except_params = [('rc', ('alpine')),])  -> Iterator[tuple[pathlib.Path, str, set[str]]]:  
                                            # rc does compile on alpine.  The particular subtemplate 
                                            # currently used compiles all of Plan9, which 
                                            # takes almost an hour

    for config, path, params in _all_config_paths_and_params():
        for param_to_remove, distros in except_params:
            if param_to_remove in params and any(distro in str(path) 
                                                 for distro in distros
                                                ):
                params.remove(param_to_remove)
        yield path, ' '.join(params), rules_to_ignore(params, config)

