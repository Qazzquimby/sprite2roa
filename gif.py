import glob
import os
import subprocess
import typing

import PIL.Image


def make_animation_dir_for_gif(path: str) -> str:
    directory = get_dir_name_for_gif(path)
    os.mkdir(directory)
    return directory



def read_gif_as_frames(path: str) -> typing.List[PIL.Image.Image]:
    directory = get_dir_name_for_gif(path)
    if not os.path.exists(directory):
        directory = make_animation_dir_for_gif(path)

        image_magick_convert = r'E:\Program Files\ImageMagick-7.0.9-Q16\convert'

        cmd = [image_magick_convert,
               path,
               '-coalesce',
               f'{directory}/img.png']
        subprocess.run(cmd)

    frames = []
    for f in glob.iglob(f'{directory}/*'):
        frame = PIL.Image.open(f)
        frame = frame.convert('RGBA')
        frames.append(frame)

    return frames


def get_dir_name_for_gif(path: str) -> str:
    """Makes a directory with the same name as the gif, to store its contents."""
    directory = os.path.splitext(path)[0]
    return directory