import string


class Move:
    def __init__(self, coords_i, coords_f, board):
        self.coords_i = tuple(coords_i)
        self.coords_f = tuple(coords_f)
        self.piece_moved = board[coords_i[1]][coords_i[0]]
        self.piece_captured = board[coords_f[1]][coords_f[0]]

    def __str__(self):
        return f"\nInitial coords: {self.coords_i}\nFinal coords: {self.coords_f}\nPiece moved: {self.piece_moved}\nPiece captured: {self.piece_captured}"

    def __eq__(self, other):
        """If two move objects have the same initial and final coordinates, they are the same move."""
        if isinstance(other, Move):
            return self.coords_i == other.coords_i and self.coords_f == other.coords_f

    def chess_notation(self):
        return f"{self.converter(self.coords_i)} {self.converter(self.coords_f)}"

    def converter(self, coords):
        """Converts column row notation (where 0,0 is top left) into chess notation"""
        new_col = string.ascii_letters[coords[0]]
        new_row = 8 - coords[1]
        return f"{new_col}{new_row}"
