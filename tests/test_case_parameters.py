
import os
import pathlib
import json
import random
from typing import Iterator



ENFORCE_ALL_VERSION_PINNING_WARNINGS = os.getenv('TEST_DOCKERFILE_GENERATOR_ENFORCE_ALL_VERSION_PINNING_WARNINGS', "False") == "True"

VERSION_PINNING_RULES = {'DL3008', 'DL3013', 'DL3016', 'DL3018', 'DL3028',}
RULES_TO_ALWAYS_IGNORE = {'DL3059',}
#                         Apt-get   Pip       Npm       Apk       Gem
# E.g: https://github.com/hadolint/hadolint/wiki/DL3008





def versioned(pkgs):
    return all(any(c in pkg for c in ('<','>','=')) for pkg in pkgs)


def rules_to_ignore(pkgs):
    if ENFORCE_ALL_VERSION_PINNING_WARNINGS or versioned(pkgs):
        return RULES_TO_ALWAYS_IGNORE
    
    return RULES_TO_ALWAYS_IGNORE | VERSION_PINNING_RULES


def _generate_test_data(a = 2, b = None, n = 4) -> Iterator[tuple[pathlib.Path, str, set[str]]]:
    """ Yields different test data depending on an env variable,
        and on whatever json config files 
        are in the repo.  And ends with n random test cases per config.  
        Set the bool ENFORCE_ALL_VERSION_PINNING_WARNINGS 
        to True to require all
        configs to pass hadolint's version pinning rules.
    """

    for path in pathlib.Path('.').glob('**/*.json'):



        with open(path, 'rt') as f:
            config = json.load(f).get('config', None)

        if config is None:
            continue

        # Test generating Dockerfile with no params
        yield path, '', RULES_TO_ALWAYS_IGNORE

        params = [param
                  for command in config.get('commands', {}).values()
                  for param in command.get('supported_parameters', []) 
                 ]

        params.extend(config.get('build_stages', {}))

        if not params: 
            continue

        # Test generating Dockerfile with all the params
        yield path, ' '.join(params), rules_to_ignore(params)


        # Test generating Dockerfile with each param on its own
        for param in params:
            yield path, param, rules_to_ignore([param])


        max_sample_size = len(params) - 1 if b is None else b


        # Test generating Dockerfile with n random selections of between a and b params
        for _ in range(n):
            try:
                k = random.randint(a, max_sample_size)
                sample = random.sample(params, k)
            except ValueError as e:
                print(f'{a=}, {max_sample_size=}, {k=}, {path=}, {b=}')
                raise e
            yield path, sample, rules_to_ignore(sample)


def _only_all_param_tests(except_params = [('rc', ('alpine')),]):  # rc does compile on alpine.  This subtemplate just 
                                                                   # compiles Plan9 too, which takes almost an hour
    """ Assumes each config_path's test with all supported params 
        is immediately after the one with none.
    """
    prev_params = None
    for config_path, params, rules in _generate_test_data():
        if prev_params == '':
            for param, distros in except_params:
                for distro in distros:
                    first_str = f'{param} '
                    param_str = first_str if params.startswith(first_str) else f' {param}'
                    if distro in str(config_path.stem) and param_str in params:
                        params = params.replace(param_str,'') 
            yield config_path, params, rules
        prev_params = params