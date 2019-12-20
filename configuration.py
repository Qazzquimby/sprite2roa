from configparser import ConfigParser

import typing


def interpret_config(config_parser: ConfigParser, args: typing.Dict, query: str, default=None, coerce=None):
    arg_query = f'--{query}'
    arg_result = args[arg_query]
    if arg_result:
        result = arg_result
    else:
        try:
            config_result = config_parser['CONFIG'][query]
            result = config_result
        except KeyError:
            return default

    if coerce:
        result = coerce(result)
    return result


def read_game_config(game_directory: str) -> ConfigParser:
    config = ConfigParser()
    config.read(f'{game_directory}/config.ini')
    return config


def read_character_config(game_config: ConfigParser, char_directory: str) -> ConfigParser:
    config = game_config
    try:
        config.read(f'{char_directory}/config.ini')
    except FileNotFoundError:
        pass
    return config
