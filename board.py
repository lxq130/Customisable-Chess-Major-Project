from constants import *
from piece import *


class Board:
    def __init__(self, width=512, gs_pos=None, board=CLASSIC_BOARD, sqrs=8):
        self.board = board
        self.width = width
        self.sqrs = sqrs

        # The top left coordinate of the board
        # self.gs_pos = (
        #     (
        #         int(margin(WIDTH)),
        #         int(HEIGHT / 2 - self.width / 2),
        #     )
        #     if gs_pos is None
        #     else gs_pos
        # )

        self.gs_pos = (
            (
                int(WIDTH / 2 - self.width / 2),
                int(HEIGHT / 2 - self.width / 2 - 20),
            )
            if gs_pos is None
            else gs_pos
        )

        # DEFAULT VALUES
        self.def_width = width
        self.def_gs_pos = [coord for coord in self.gs_pos]
        self.def_sqrs = sqrs
        self.def_board = get_board(self.board)

        self.sqr_size = self.get_sqr_size()

    def edit(self, **kwargs):
        """Edits the attribute specified, and updates the rest if necessary."""
        for key, value in kwargs.items():
            if key == "sqrs":
                self.sqrs = value
                # Adjusts board to match size
                while len(self.board) < self.sqrs:
                    self.add_rowcol()
                while len(self.board) > self.sqrs:
                    self.remove_rowcol()

            if key == "board":
                self.board = value

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

    def add_rowcol(self):
        """Adds a row and a column to the board"""
        # Adds an extra row
        self.board.append([Empty() for i in range(self.sqrs - 1)])
        # Iterates through each row and adds a column
        for i in range(len(self.board)):
            self.board[i].append(Empty())

    def remove_rowcol(self):
        """Removes a row and a column from the board. Any pieces on these squares are removed."""
        # Removes last row
        self.board = self.board[:-1]
        # Removes last column of each remaining row
        for i in range(len(self.board)):
            self.board[i] = self.board[i][:-1]

    def is_classic(self):
        """Returns true if the board is a classic board. (Has normal pieces and arrangements)"""
        if len(CLASSIC_BOARD) != len(self.board):
            return False
        for y, row in enumerate(CLASSIC_BOARD):
            for x, piece in enumerate(row):
                if self.board[y][x].name_colour != piece.name_colour:
                    return False
        self.classic = True
        return True

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
