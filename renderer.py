import pygame as p
from constants import *
import os
from button import Button
import sys
from helper import *
from piece import *


class Renderer:
    def __init__(self, screen, board_config, sqr_size=None):
        self.screen = screen
        self.sqr_size = board_config.sqr_size if sqr_size is None else sqr_size
        self.board_config = board_config
        self.pieces = list(board_config.available_pieces.values())
        # Loads all images into images dictionary
        self.promotable_pieces = [
            piece.name_colour
            for piece in self.pieces
            if piece.name_colour[1:] not in ["King", "Pawn"]
        ]

        self.images = {}

        for piece in self.pieces:
            # Loads and transforms the image to the same size as the squares.
            image = p.image.load(
                os.path.join("assets", "piece_images", f"{piece.name_colour}.png")
            )
            image = p.transform.scale(image, (self.sqr_size, self.sqr_size))
            self.images[piece.name_colour] = image

    def draw_board(self, board):
        """Draws the actual board."""
        for y, row in enumerate(board):
            for x in range(len(row)):
                square = p.Rect(
                    (get_screen_pos((x, y), self.board_config)),
                    (self.sqr_size, self.sqr_size),
                )
                # If column even, row even, then light, else dark
                if (x % 2 == 0 and y % 2 == 0) or (x % 2 == 1 and y % 2 == 1):
                    p.draw.rect(self.screen, DARK_SQR, square)
                else:
                    p.draw.rect(self.screen, LIGHT_SQR, square)

    def draw_pieces(self, board, dragged_piece):
        """Draws all the pieces, except the piece being dragged."""
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if piece.name != "Empty" and piece is not dragged_piece:
                    self.screen.blit(
                        self.images[piece.name_colour],
                        get_screen_pos((x, y), self.board_config),
                    )

    def draw_check(self, game):
        # If the king of the current player's turn is in check, change colour of square.
        for y, row in enumerate(game.board):
            for x, piece in enumerate(row):
                square = p.Rect(
                    get_screen_pos((x, y), self.board_config),
                    (self.sqr_size, self.sqr_size),
                )
                if piece.name_colour == f"{game.turn[0]}King" and game.in_check(
                    game.turn
                ):
                    p.draw.rect(self.screen, CHECK_SQR, square)

    def draw_all(self, game, dragged_piece):
        self.draw_board(game.board)
        self.draw_check(game)
        self.draw_pieces(game.board, dragged_piece)

    def draw_moves(self, piece, game, coords, display_all=False):
        if (piece.colour == game.turn or display_all) and in_board(
            self.board_config, coords=coords
        ):
            moves = (
                piece.get_all_moves(game, coords)
                if display_all
                else piece.get_valid_moves(game, coords)
            )
            for move in moves:
                # Colour
                colour = (
                    HIGHLIGHT_1
                    if (move.coords_f[1] + move.coords_f[0]) % 2 == 0
                    else HIGHLIGHT_2
                )
                # Rectangle
                rect = (
                    get_screen_pos(move.coords_f, self.board_config),
                    (self.sqr_size, self.sqr_size),
                )
                p.draw.rect(self.screen, colour, rect, 5, 5)

    def get_promoted_piece(self, move, sounds, display_scn, board_pos):
        """Displays GUI for pawn promotion and returns the selected piece as a string."""
        direction = move.piece_moved.direction
        p.display.update()
        while True:
            mouse_pos = p.mouse.get_pos()
            buttons = {}

            i = 0
            # Iterates through each piece that can be promoted
            for piece in self.promotable_pieces:
                if piece[0] == move.piece_moved.colour[0]:
                    # The background of the squares where the possible pieces are displayed
                    pos_x = move.coords_f[0] * self.sqr_size + board_pos[0]
                    pos_y = (
                        move.coords_f[1] - i * direction
                    ) * self.sqr_size + board_pos[1]

                    bg_rect = (
                        (pos_x, pos_y),
                        (self.sqr_size, self.sqr_size),
                    )
                    p.draw.rect(display_scn, GREEN, bg_rect)

                    # Draws in the pieces as clickable buttons.
                    piece_button = Button(
                        image=self.images[piece],
                        pos=(pos_x, pos_y),
                        alignment="topleft",
                    )
                    buttons[piece] = piece_button
                    piece_button.draw(display_scn)
                    i += 1

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()
                # If the user is pressing down, check if a button is being clicked.
                if event.type == p.MOUSEBUTTONDOWN:
                    for piece, button in buttons.items():
                        if button.check_input(mouse_pos):
                            if sounds.sfx_on:
                                sounds.click.play(sounds.sfx_on)
                            return piece[1:]

            p.display.update()

    def draw_and_get_palettes(self, pos_w, pos_b):
        # Returns a dictionary of buttons that make up the palette
        sqr_size = self.sqr_size
        palettes = {
            "white": pos_w,
            "black": pos_b,
        }
        buttons = {}
        # Cycles through every piece for each colour
        for colour, palette_pos in palettes.items():
            i = 0
            for piece in list(ALL_PIECES.values()):
                if piece.colour == colour and piece.name != "King":
                    # Display background behind the pieces to be placed.
                    pos = (i * self.sqr_size + palette_pos[0], palette_pos[1])
                    bg_rect = (
                        pos,
                        (sqr_size, sqr_size),
                    )

                    p.draw.rect(self.screen, GREEN, bg_rect)

                    # Display button
                    piece_button = Button(
                        image=self.images[piece.name_colour],
                        pos=pos,
                        alignment="topleft",
                    )
                    buttons[piece] = piece_button
                    piece_button.draw(self.screen)
                    i += 1

        return buttons
