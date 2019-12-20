"""sprite2roa command line interface

Usage:
    sprite2roa.py
    sprite2roa.py [<game_name> [<char_name>]] [options]
    sprite2roa.py -h|--help
    sprite2roa.py -v|--version

Options:
    # <game_name>     The game to process, matching the name of a directory in the input folder.
    # <char_name>     The character to process, matching the name of a directory in a game's folder.
    # Eg. sprite2roa.py skullgirls filia (reads from the directory input/skullgirls/filia)
    -h --help       Show this screen.
    -v --version    Show version.

    --avg_char_height <height>
    # The average character height in the source images, in pixels.
    # Required unless specified in config.ini
    # Used to appropriately scale character's to Rivals of Aether average height of ~30 px.
    # Larger value produces smaller sprites.
    # Eg. 230

    --one_frame_per_file
    # When this is *not* set, it is assumed that each file represents an animation (either a sprite sheet or a gif)
    # When this is set, it is assumed that each directory of files represents an animation,
    #    with each file in the directory being a frame in that animation.

    --should_outline
    # When this is set, a single pixel outline is added to the output sprites. Recommended.

    --background_color <color>
    # Replaces the given rgb value with transparency.
    # Must have three values in the range [0, 255]
    # Eg. 64 64 64

    --saturation <amount>
    # Scales the sprites color saturation by the given amount.
    # Eg. 1.5
"""

import configparser
import glob
import os

import PIL.GifImagePlugin
from PIL import Image
import typing

import configuration
from configuration import read_game_config, read_character_config
from gif import read_gif_as_frames
import transformations as trans

import docopt


def get_game_directories() -> typing.List[str]:
    dirs = glob.glob('input/*')
    return dirs


def process_game(game_directory: str, args: typing.Dict):
    game_config = read_game_config(game_directory)

    if args['<char_name>']:
        char_directories = [f"{game_directory}/{args['<char_name>']}"]
    else:
        char_directories = [d for d in glob.glob(f'{game_directory}/*') if d[-3:] != 'ini']

    for char_directory in char_directories:
        process_character(char_directory, game_config, args)


def process_character(char_directory: str, game_config: configparser.ConfigParser, args: typing.Dict):
    char_config = read_character_config(game_config=game_config, char_directory=char_directory)

    one_page_per_file = configuration.interpret_config(char_config, args, 'one_frame_per_file', default=False)
    if one_page_per_file:
        process_directory_animations(char_directory, char_config, args)
    else:
        process_file_animations(char_directory, char_config, args)


def process_file_animations(char_directory: str, char_config: configparser.ConfigParser, args: typing.Dict):
    animation_file_paths = get_file_animations_file_paths(char_directory)
    for file_path in animation_file_paths:
        process_file_animation(file_path, char_config, args)


def process_directory_animations(char_directory: str, char_config: configparser.ConfigParser, args: typing.Dict):
    animation_directories = get_directory_animation_directories(char_directory)
    for directory in animation_directories:
        process_directory_animation(directory, char_config, args)


def get_file_animations_file_paths(char_directory: str) -> typing.List[str]:
    directories = glob.glob(f'{char_directory}/**.*')
    directories = [d for d in directories if d[-3:] != 'ini']
    return directories


def get_directory_animation_directories(char_directory: str) -> typing.List[str]:
    directories = glob.glob(f'{char_directory}/**/', recursive=True)
    directories = [d for d in directories if d[-3:] != 'ini']
    return directories


def process_file_animation(file_path: str, char_config: configparser.ConfigParser, args: typing.Dict):
    out_path = file_path.replace('input', 'output')[:-4]
    matching_file = glob.glob(f'{out_path}*')

    if not matching_file:
        print(f'Processing {file_path}')
        if file_path[-3:] == 'gif':
            frames = read_gif_as_frames(file_path)
        else:
            frame = PIL.Image.open(file_path)
            frame = frame.convert('RGBA')
            frames = [frame]

        frames = process_frames(frames, char_config, args)
        save_frames(frames, out_path)


def process_directory_animation(directory: str, char_config: configparser.ConfigParser, args: typing.Dict):
    out_path = directory.replace('input', 'output')

    files = [f for f in glob.glob(f'{directory}/*.*') if f[-3:] != 'ini']
    if files:
        print(f'Processing {directory}')

        frames = []
        for f in files:
            try:
                frame = PIL.Image.open(f)
            except PermissionError:
                continue
            frame = frame.convert('RGBA')
            frames.append(frame)

        frames = process_frames(frames, char_config, args)
        save_frames(frames, out_path)


def parse_background_color(background_color_string: str) -> typing.Tuple[int, int, int]:
    digits = [int(s) for s in background_color_string.split() if s.isdigit()]

    if len(digits) != 3:
        raise ValueError(f'{len(digits)} color values given. 3 Needed. Colors given are {digits}')

    for digit in digits:
        if not 0 <= digit <= 255:
            raise ValueError(f'color value {digit} must be between 0 and 255')
    return digits[0], digits[1], digits[2]


def process_frames(frames: typing.List[PIL.Image.Image], char_config: configparser.ConfigParser, args: typing.Dict):
    background_color_str = configuration.interpret_config(char_config, args, 'background_color', None)
    if background_color_str:
        background_color = parse_background_color(background_color_str)
        frames = [trans.delete_background_color(frame, background_color) for frame in frames]

    avg_char_height = configuration.interpret_config(char_config, args, 'avg_char_height', coerce=int)
    if avg_char_height is None:
        raise ValueError('avg_char_height must be defined in a config file or argument.')
    frames = [trans.resize(frame, trans.get_scale(avg_char_height))
              for frame in frames]

    saturation = configuration.interpret_config(char_config, args, 'saturation', 1.0, coerce=float)
    if saturation != 1.0:
        frames = [trans.saturate(frame, saturation) for frame in frames]

    should_outline = configuration.interpret_config(char_config, args, 'should_outline', False, coerce=bool)
    if should_outline:
        frames = [trans.stroke(frame) for frame in frames]

    return frames


def save_frames(frames: typing.List[PIL.Image.Image], path: str):
    if frames:
        sheet = trans.layout_sheet(frames)
        out_path = path + f'_{len(frames)}.png'

        directory, _ = os.path.split(out_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        sheet.save(out_path)


if __name__ == '__main__':
    try:
        args = docopt.docopt(__doc__, version='1.0')
    except docopt.DocoptExit:
        print('That input is invalid.')
        print(docopt.printable_usage(__doc__))
        args = []

    if args:
        if args['<game_name>']:
            game_directories = [f"input/{args['<game_name>']}"]
        else:
            game_directories = get_game_directories()

        for game_directory in game_directories:
            process_game(game_directory, args)
