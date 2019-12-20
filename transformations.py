import typing

import PIL.Image
import PIL.ImageEnhance
import numpy as np
from PIL import Image

TARGET_AVG_HEIGHT = 30


def get_scale(src_avg_height: int) -> float:
    scale = TARGET_AVG_HEIGHT / src_avg_height
    return scale


def delete_background_color(in_image: PIL.Image.Image,
                            background_color: typing.Tuple[int, int, int]) -> PIL.Image.Image:
    # noinspection PyTypeChecker
    pixels = np.array(in_image)
    try:
        color = pixels[:, :, :3]
    except IndexError:
        return in_image
    mask = np.all(color == background_color, axis=-1)

    transparent = [0, 0, 0, 0]
    pixels[mask] = transparent

    no_bg = Image.fromarray(pixels)
    return no_bg


def resize(in_image: PIL.Image.Image, scale: float) -> PIL.Image.Image:
    size = (max(1, int(dim * scale)) for dim in in_image.size)
    resized = in_image.resize(size, Image.NEAREST)
    return resized


def saturate(in_image: PIL.Image.Image, saturation: float) -> PIL.Image.Image:
    converter = PIL.ImageEnhance.Color(in_image)
    saturated = converter.enhance(saturation)
    return saturated


def _get_diff_array(data, shifted_data, level):
    # distance_map = np.absolute(np.sum(data - shifted_data, axis=2))
    distance_map = np.absolute(data - shifted_data)
    different = np.asarray(distance_map > level)
    return different


def stroke(img, level=250):
    data = np.asarray(img)
    transparency = data[:, :, 3]  # transparency
    level = min(max(1, level), 255)

    edges_left = _get_diff_array(
        np.concatenate((transparency[:, 1:], transparency[:, -1:]), axis=1), transparency, level)
    edges_up = _get_diff_array(
        np.concatenate((transparency[1:, :], transparency[-1:, :]), axis=0), transparency, level)

    edges_right = _get_diff_array(transparency, np.concatenate((transparency[:, 1:], transparency[:, -1:]), axis=1),
                                  level)
    edges_down = _get_diff_array(transparency, np.concatenate((transparency[1:, :], transparency[-1:, :]), axis=0),
                                 level)

    out = data.copy()

    edges = np.logical_or.reduce((edges_left, edges_up, edges_right, edges_down))

    out[edges] = [0, 0, 0, 255]
    stroked = Image.fromarray(out, 'RGBA')

    return stroked


def limit_palette():
    pass
    # Get palette
    # - Get hues
    # - Get tones
    # Set to palette


def layout_sheet(frames: typing.List[PIL.Image.Image]) -> PIL.Image.Image:
    frame_height = max([frame.height for frame in frames])
    frame_width = max([frame.width for frame in frames])

    strip_height = frame_height
    strip_width = frame_width * len(frames)

    sheet = PIL.Image.new('RGBA', (strip_width, strip_height))
    for i, frame in enumerate(frames):
        this_frame_width = frame.size[0]
        this_frame_height = frame.size[1]

        slot_left = frame_width * i
        slot_up = frame_height
        slot_right = frame_width * (i + 1)
        slot_down = 0

        width_difference = frame_width - this_frame_width
        height_difference = frame_height - this_frame_height

        left = slot_left + width_difference // 2
        up = slot_up - this_frame_height
        right = left + this_frame_width
        down = frame_height - height_difference
        sheet.paste(frame, box=(left, up))  # , right, down))
    return sheet
