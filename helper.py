import pygame as p
import os
from constants import *

p.init()


def set_working_dir():
    # Ensures working directory is set to the location of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_font(size):
    """Returns a font."""
    return p.font.Font("assets/font.ttf", size)


def margin(width):
    """Returns the margin width."""
    return width * 1 // 15


def in_board(board_config, coords=None, pos=None):
    """Returns true if the coordinates given are on the board."""
    if coords is not None:
        if (
            coords[0] >= 0
            and coords[0] < board_config.sqrs
            and coords[1] >= 0
            and coords[1] < board_config.sqrs
        ):
            return True
        return False
    if pos is not None:
        if (
            pos[0] > board_config.gs_pos[0]
            and pos[0] < board_config.gs_pos[0] + board_config.width
            and pos[1] > board_config.gs_pos[1]
            and pos[1] < board_config.gs_pos[1] + board_config.width
        ):
            return True
        return False


def get_board_coords(pos, board_config):
    """Converts screen position (e.g. 100, 100) to board coorinates (e.g. 1, 0), based on the position of the board on the screen."""
    return (
        int((pos[0] - board_config.gs_pos[0]) // board_config.sqr_size),
        int((pos[1] - board_config.gs_pos[1]) // board_config.sqr_size),
    )


def get_screen_pos(coords, board_config):
    """Converts board coordinates into screen position."""
    return (
        int(coords[0] * board_config.sqr_size),
        int(coords[1] * board_config.sqr_size),
    )


def draw_text(
    screen,
    size,
    text,
    pos=(WIDTH // 2, HEIGHT * 1 // 8),
    colour=GREEN,
    alignment="center",
):
    title_text = get_font(size).render(text, True, colour)
    if alignment == "center":
        title_rect = title_text.get_rect(center=pos)
    elif alignment == "topleft":
        title_rect = title_text.get_rect(topleft=pos)
    screen.blit(title_text, title_rect)


def get_board(board):
    """Prevents passing by reference. Only works for 2D lists."""
    return [[piece for piece in row] for row in board]


def print_board(board):
    """Testing purposes only. Prints the board."""
    output = ""
    ls = []
    for row in board:
        ls_row = []
        for piece in row:
            if piece.name == "Knight":
                ls_row.append(piece.name_colour[0] + "N")
            elif piece.name == "Empty":
                ls_row.append("--")
            else:
                ls_row.append(piece.name_colour[:2])
        ls.append(ls_row)
    for row in ls:
        for piece in row:
            output += piece + "|"
        output = output[:-1] + "\n"
    print(output)


# def print_board(board):
#     """Testing purposes only. Prints the board."""
#     output = "-" * 120 + "\n"
#     ls = []
#     for row in board:
#         ls_row = []
#         for piece in row:
#             ls_row.append(piece.name_colour)
#         ls.append(ls_row)
#     for row in ls:
#         for col in row:
#             output += "{:>11}".format(col) + "  "
#         output += "\n"
#     output += "-" * 120
#     print(output)
#     print(f"Dimensions: {len(board[0])}x{len(board)}")
