from helper import *
from move import Move

set_working_dir()


class Piece:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.name_colour = colour[0] + name
        if self.colour == "white":
            self.opponent_colour = "black"
        elif self.colour == "black":
            self.opponent_colour = "white"
        else:
            self.opponent_colour = "none"

    def __str__(self):
        if self.name == "Pawn":
            return f"{self.name_colour}, Can double move: {self.has_double_move}"
        return self.name_colour

    def has_moved(self, move_log):
        """Returns true if the piece has already moved before"""
        for move in move_log:
            if move.piece_moved == self:
                return True
        return False

    def get_all_moves(self):
        """Method overriden in subclasses."""
        return []

    def get_valid_moves(self, game, coords):
        """Returns valid moves. Accounts for checks."""
        moves = self.get_all_moves(game, coords)
        valid_moves = []
        for move in moves:
            if game.validate_move(move):
                valid_moves.append(move)
        return valid_moves

    def get_linear_moves(self, directions, game, coords):
        """Since the rook, bishop and queen have similar movement patterns, only one method is required for all three."""
        board = game.board
        possible_moves = []
        for direction in directions:
            i = 0
            while True:
                i += 1
                final_coords = (
                    coords[0] + direction[0] * i,
                    coords[1] + direction[1] * i,
                )
                if game.in_board(final_coords):
                    final_piece = board[final_coords[1]][final_coords[0]]
                    if final_piece.name != "Empty":
                        if final_piece.colour == self.opponent_colour:
                            possible_moves.append(Move(coords, final_coords, board))
                        break
                    else:
                        possible_moves.append(Move(coords, final_coords, board))
                else:
                    break
        return possible_moves


class Empty(Piece):
    def __init__(self):
        super().__init__("Empty", "none")


class Pawn(Piece):
    def __init__(self, colour):
        # Direction represents the direction the pawn moves in.
        self.direction = -1 if colour == "white" else 1
        self.has_double_move = False  # Is true when the pawn has just moved twice up.
        super().__init__("Pawn", colour)

    def get_en_passant(self, game, coords):
        """Returns an en passant move if that is possible."""
        board = game.board
        for i in range(-1, 2, 2):
            if game.in_board((coords[0] + i, coords[1])):
                opponent_pawn = board[coords[1]][coords[0] + i]
                if (
                    opponent_pawn.name_colour == f"{self.opponent_colour[0]}Pawn"
                    and opponent_pawn.has_double_move == True
                ):
                    final_coords = (coords[0] + i, coords[1] + self.direction)
                    return [Move(coords, final_coords, board)]
        return []

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        board = game.board
        possible_moves = []

        # Moving a pawn 1 up.
        final_coords = (coords[0], coords[1] + self.direction)
        if game.in_board(final_coords):
            final_piece = board[final_coords[1]][final_coords[0]]
            if final_piece.name == "Empty":
                possible_moves.append(Move(coords, final_coords, board))

                # Moving a pawn two spaces up for the first time.
                final_coords = (coords[0], coords[1] + self.direction * 2)
                if game.in_board(final_coords):
                    final_piece = board[final_coords[1]][final_coords[0]]
                    if (
                        not self.has_moved(game.move_log)
                        and final_piece.name == "Empty"
                    ):
                        possible_moves.append(Move(coords, final_coords, board))

        # Moving a pawn diagonally to capture
        final_coord_ls = [
            (coords[0] + 1, coords[1] + self.direction),
            (coords[0] - 1, coords[1] + self.direction),
        ]
        for final_coords in final_coord_ls:
            if game.in_board(final_coords):
                final_piece = board[final_coords[1]][final_coords[0]]
                if final_piece.colour == self.opponent_colour:
                    possible_moves.append(Move(coords, final_coords, board))

        possible_moves += self.get_en_passant(game, coords)

        return possible_moves


class Knight(Piece):
    def __init__(self, colour):
        super().__init__("Knight", colour)

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        board = game.board
        jumps = [(-1, 2), (-1, -2), (1, 2), (1, -2), (-2, 1), (-2, -1), (2, 1), (2, -1)]
        possible_moves = []
        for jump in jumps:
            final_coords = (coords[0] + jump[0], coords[1] + jump[1])
            if game.in_board(final_coords):
                final_piece = board[final_coords[1]][final_coords[0]]
                if final_piece.colour != self.colour:
                    possible_moves.append(Move(coords, final_coords, board))
        return possible_moves


class Bishop(Piece):
    def __init__(self, colour):
        super().__init__("Bishop", colour)

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return self.get_linear_moves(directions, game, coords)


class Rook(Piece):
    def __init__(self, colour):
        super().__init__("Rook", colour)

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        return self.get_linear_moves(directions, game, coords)


class Queen(Piece):
    def __init__(self, colour):
        super().__init__("Queen", colour)

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        directions = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        return self.get_linear_moves(directions, game, coords)


class King(Piece):
    def __init__(self, colour):
        super().__init__("King", colour)
        self.called = False
        # This flag helps prevent unintentional recursion from happening
        # where get castle moves -> under attack -> get all moves -> get castle moves

    def get_castle_moves(self, game, coords):
        self.called = True
        board = game.board
        possible_moves = []
        # Check if the King has moved before.
        if not self.has_moved(game.move_log):
            for direction in range(-1, 2, 2):  # (direction = -1 then 1)
                current_x = coords[0]
                y = coords[1]
                # Keep moving to the left/right until out of board
                while game.in_board((current_x, y)):
                    piece = board[y][current_x]
                    # If the square is not empty, check if it is a rook that can be castled.
                    if piece.name != "Empty" and piece.name != "King":
                        if (
                            piece.name_colour == f"{self.colour[0]}Rook"
                            and not game.in_board((current_x + direction, y))
                            and not piece.has_moved(game.move_log)
                            and not game.under_attack((current_x, y), self.colour)
                        ):
                            final_coords = (coords[0] + 2 * direction, coords[1])
                            if game.in_board(final_coords):
                                possible_moves.append(Move(coords, final_coords, board))
                        # If it is not a rook that can be castled, break.
                        else:
                            break
                    elif game.under_attack((current_x, y), self.colour):
                        break
                    current_x += direction
        return possible_moves

    def get_all_moves(self, game, coords):
        """Returns a list of moves"""
        board = game.board
        directions = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
            (-1, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
        ]
        possible_moves = []
        for direction in directions:
            final_coords = (coords[0] + direction[0], coords[1] + direction[1])
            if game.in_board(final_coords):
                final_piece = board[final_coords[1]][final_coords[0]]
                if final_piece.colour != self.colour:
                    possible_moves.append(Move(coords, final_coords, board))
        if not self.called:
            possible_moves += self.get_castle_moves(game, coords)
            self.called = False
        return possible_moves


ALL_PIECES = {
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


def get_piece(name_colour):
    """Returns the piece object"""
    if name_colour == "bQueen":
        return Queen("black")
    if name_colour == "bKing":
        return King("black")
    if name_colour == "bKnight":
        return Knight("black")
    if name_colour == "bRook":
        return Rook("black")
    if name_colour == "bBishop":
        return Bishop("black")
    if name_colour == "bPawn":
        return Pawn("black")
    if name_colour == "wQueen":
        return Queen("white")
    if name_colour == "wKing":
        return King("white")
    if name_colour == "wKnight":
        return Knight("white")
    if name_colour == "wRook":
        return Rook("white")
    if name_colour == "wBishop":
        return Bishop("white")
    if name_colour == "wPawn":
        return Pawn("white")
