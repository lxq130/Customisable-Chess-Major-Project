from constants import *
from piece import *

CLASSIC_PIECES = {
    "bQueen": Queen("black"),
    "bKing": King("black"),
    "bKnight": Knight("black"),
    "bPawn": Pawn("black"),
    "bBishop": Bishop("black"),
    "bRook": Rook("black"),
    "wQueen": Queen("white"),
    "wKing": King("white"),
    "wKnight": Knight("white"),
    "wPawn": Pawn("white"),
    "wBishop": Bishop("white"),
    "wRook": Rook("white"),
}

BOARD = [
    [
        Rook("black"),
        Knight("black"),
        Bishop("black"),
        Queen("black"),
        King("black"),
        Bishop("black"),
        Knight("black"),
        Rook("black"),
    ],
    [Pawn("black") for i in range(8)],
    [Empty() for i in range(8)],
    [Empty() for i in range(8)],
    [Empty() for i in range(8)],
    [Empty() for i in range(8)],
    [Pawn("white") for i in range(8)],
    [
        Rook("white"),
        Knight("white"),
        Bishop("white"),
        Queen("white"),
        King("white"),
        Bishop("white"),
        Knight("white"),
        Rook("white"),
    ],
]


class Board:
    def __init__(self, width=512, gs_pos=None, board=BOARD, sqrs=8):
        self.board = board
        self.width = width
        self.sqrs = sqrs
        self.available_pieces = CLASSIC_PIECES

        # The top left coordinate of the board
        self.gs_pos = (
            (
                int(WIDTH / 2 - self.width / 2),
                int(HEIGHT / 2 - self.width / 2),
            )
            if gs_pos is None
            else gs_pos
        )

        # DEFAULT VALUES
        self.def_width = width
        self.def_gs_pos = [coord for coord in self.gs_pos]
        self.def_sqrs = sqrs
        self.def_board = get_board(board)

        self.sqr_size = self.get_sqr_size()

    def edit(self, **kwargs):
        """Edits the attribute specified, and updates the rest if necessary."""
        for key, value in kwargs.items():
            if key == "sqrs":
                self.sqrs = value
            if key == "board":
                self.board = value

                # Checks if a new piece has been added, if so add to available pieces dictionary.
                for row in self.board:
                    for piece in row:
                        if (
                            piece.name_colour not in self.available_pieces
                            and piece.name != "Empty"
                        ):
                            self.available_pieces[piece.name_colour] = get_piece(
                                piece.name_colour
                            )

        self.sqr_size = self.get_sqr_size()
        self.width = self.sqr_size * self.sqrs

        # Check if there are still a black and white king on the board, if not add it back.
        has_king = {"white": False, "black": False}
        for row in self.board:
            for piece in row:
                if piece.name_colour == "bKing" or piece.name_colour == "wKing":
                    has_king[piece.colour] = True

        # Tries to place the kings on opposite sides if those tiles are empty, otherwise place it in any empty tile, otherwise place it anywhere.
        for colour, value in has_king.items():
            if not value:
                placed = False
                if self.board[0][0].name == "Empty" and colour == "black":
                    self.board[0][0] = King(colour)
                    placed = True
                if self.board[-1][0].name == "Empty" and colour == "white":
                    self.board[-1][0] = King(colour)
                    placed = True
                if not placed:
                    for y, row in enumerate(self.board):
                        for x, piece in enumerate(row):
                            if piece.name == "Empty" and not placed:
                                self.board[y][x] = King(colour)
                                placed = True
                if not placed:
                    if self.board[0][0].name != "King":
                        self.board[0][0] = King(colour)
                    else:
                        self.board[-1][0] = King(colour)

    def set_default(self):
        """Resets all attributes to their default values."""
        self.width = self.def_width
        self.sqrs = self.def_sqrs
        self.sqr_size = self.get_sqr_size()
        self.board = get_board(self.def_board)
        self.gs_pos = [coord for coord in self.def_gs_pos]

    def get_sqr_size(self):
        """Returns the square size."""
        # The code will always try to round up first if it can fit in its allocated space.
        # This prevents the board from shrinking over time.
        rounded_up = self.width // self.sqrs + 1
        rounded_down = self.width // self.sqrs
        if rounded_up * self.sqrs <= self.def_width:
            return rounded_up
        else:
            return rounded_down
