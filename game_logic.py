from constants import *
from helper import *
from move import Move
from piece import *

# Note that all coordinates are in (x, y) notation BUT the board is indexed with [y][x] notation


class Game:
    def __init__(self, board, is_main=True):
        self.board = board
        self.turn = "white"
        self.opponent = "black"
        self.move_log = []
        self.undo_log = []
        self.is_main = is_main  # The instance used for the actual game

    def switch_turn(self):
        """Switches turn."""
        self.turn = "black" if self.turn == "white" else "white"
        self.opponent = "black" if self.opponent == "white" else "white"

    def in_board(self, coords):
        """Returns true if the coords are in the board"""
        if coords[0] >= 0 and coords[0] < len(self.board) and coords[1] >= 0 and coords[1] < len(self.board):
            return True
        return False

    def move_piece(self, move, redo=False):
        """Moves piece from move.coords_i to move.coords_f on the list representing the board."""

        promoting = False

        # If the move is done by a player rather than a redo, clear the undo_move log
        if not redo:
            self.undo_log = []

        # If a promotion is being redone, replace piece with the piece in the transform into attribute
        elif move.piece_moved.name == "Pawn":
            if move.piece_moved.transform_into is not None and self.can_pawn_promote(move):
                self.board[move.coords_f[1]][move.coords_f[0]] = get_piece(move.piece_moved.transform_into)
                promoting = True

        # Set initial coordinates to empty
        self.board[move.coords_i[1]][move.coords_i[0]] = Empty()

        # Witch
        if move.piece_moved.name == "Witch" and move.piece_captured.name != "Empty":
            self.board[move.coords_f[1]][move.coords_f[0]] = get_piece(f"{self.turn[0]}{move.piece_captured.name}")

        # Every normal piece
        elif not promoting:
            self.board[move.coords_f[1]][move.coords_f[0]] = move.piece_moved

        # EN PASSANT

        # Set all your own pieces to has double move = False
        # This is because en passant can only be done if the opponent just double moved their pawn.
        for row in self.board:
            for piece in row:
                if piece.colour == self.turn and piece.name == "Pawn":
                    piece.has_double_move = False

        # If the player just moved a pawn two up, set its has double move value to True
        if move.piece_moved.name == "Pawn" and abs(move.coords_f[1] - move.coords_i[1]) == 2:
            move.piece_moved.has_double_move = True

        # If En Passant, delete opponent's pawn as well
        if self.check_en_passant(move):
            self.board[move.coords_f[1] - move.piece_moved.direction][move.coords_f[0]] = Empty()

        # CASTLING

        if move.piece_moved.name == "King":
            # Right side castle
            if move.coords_f[0] - move.coords_i[0] == 2:
                self.board[move.coords_f[1]][-1] = Empty()
                self.board[move.coords_f[1]][move.coords_f[0] - 1] = Rook(self.turn)
            # Left side castle
            if move.coords_f[0] - move.coords_i[0] == -2:
                self.board[move.coords_f[1]][0] = Empty()
                self.board[move.coords_f[1]][move.coords_f[0] + 1] = Rook(self.turn)

        self.switch_turn()
        self.move_log.append(move)

    def redo_move(self):
        move = self.undo_log.pop()
        self.move_piece(move, redo=True)

    def undo_move(self):
        """Undoes the previous move."""
        # Previous move is assigned and removed from move_log
        p_move = self.move_log.pop()
        self.undo_log.append(p_move)
        self.board[p_move.coords_f[1]][p_move.coords_f[0]] = p_move.piece_captured
        self.board[p_move.coords_i[1]][p_move.coords_i[0]] = p_move.piece_moved

        # Check if previous move is an en-passant. If so restore the pawn as well.
        if self.check_en_passant(p_move):
            y = p_move.coords_f[1] - p_move.piece_moved.direction
            x = p_move.coords_f[0]
            self.board[y][x] = Pawn(self.turn)
            self.board[y][x].has_double_move = True

        self.switch_turn()

        # Check if the previous move is a castle. If so restore the rook to its position.
        if p_move.piece_moved.name == "King":
            # Right side castle
            if p_move.coords_f[0] - p_move.coords_i[0] == 2:
                self.board[p_move.coords_f[1]][-1] = Rook(self.turn)
                self.board[p_move.coords_f[1]][p_move.coords_f[0] - 1] = Empty()
            # Left side castle
            if p_move.coords_f[0] - p_move.coords_i[0] == -2:
                self.board[p_move.coords_f[1]][0] = Rook(self.turn)
                self.board[p_move.coords_f[1]][p_move.coords_f[0] + 1] = Empty()

    def check_en_passant(self, move):
        """Checks if the move is an En Passant move."""
        # If the pawn moved diagonally onto an empty tile, this is an en passant.
        return (
            move.piece_moved.name == "Pawn"
            and move.piece_captured.name == "Empty"
            and move.coords_f[0] != move.coords_i[0]
        )

    def can_pawn_promote(self, move):
        """Returns true if the move can pawn promote."""
        # A pawn can promote if it is at the furthest row away from its start.
        if move.piece_moved.name == "Pawn":
            pawn = move.piece_moved
            final_y = move.coords_f[1]
            # Note that only the board currently being played can have pawn promotions
            # (Boards being created for calculating checks and checkmates cannot have pawn promotions)
            if (
                (pawn.colour == "white" and final_y == 0)
                or (pawn.colour == "black" and final_y == len(self.board) - 1)
                and self.is_main
            ):
                return True
        return False

    def pawn_promote(self, move, promoted_piece):
        """Promotes the pawn to promoted_piece."""
        self.switch_turn()
        # Promotes the pawn into the promoted piece
        self.board[move.coords_f[1]][move.coords_f[0]] = get_piece(promoted_piece)

    def create_temp_game(self):
        """Creates a temporary game to simulate the outcome of various moves."""
        # Assigns temporary_game's board, turn and log to be the same as the current game.
        temp_board = get_board(self.board)
        temporary_game = Game(temp_board, is_main=False)
        temporary_game.turn = self.turn
        temporary_game.move_log = [move for move in self.move_log]
        return temporary_game

    def create_temp_move(self, move, temp_game):
        temp_board = get_board(temp_game.board)
        temporary_move = Move(move.coords_i, move.coords_f, temp_board)
        return temporary_move

    def under_attack(self, coords, colour):
        """Returns true if the given coordinates can be taken by the opponent."""
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.opponent_colour == colour:
                    moves = piece.get_all_moves(self, (x, y))
                    for move in moves:
                        if move.coords_f == coords:
                            return True
        return False

    def in_check(self, colour):
        """Returns true if the given colour's king can be taken in one move, or does not exist."""
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.name_colour == f"{colour[0]}King":
                    return self.under_attack((x, y), colour)
        return True

    def check_gameover(self):
        # """Checks if the current player is checkmated."""
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.colour == self.turn:
                    moves = piece.get_all_moves(self, (x, y))
                    for move in moves:
                        temporary_game = self.create_temp_game()
                        temporary_move = self.create_temp_move(move, temporary_game)
                        temporary_game.move_piece(temporary_move)
                        if not temporary_game.in_check(self.turn):
                            return "Neither"
        # If there are no possible moves but in check, checkmate, else stalemate
        has_king = False
        for row in self.board:
            for piece in row:
                if piece.name_colour == f"{self.opponent[0]}King":
                    has_king = True
        if self.in_check(self.turn) or not has_king:
            self.switch_turn()
            return "Checkmate"
        return "Draw"

    # def check_gameover(self):
    #     """Stub"""
    #     return False

    def validate_move(self, move):
        """Returns true if the move is a valid one."""
        piece = move.piece_moved
        if self.board[move.coords_i[1]][move.coords_i[0]].name != "Empty":
            if move in piece.get_all_moves(self, move.coords_i) and self.turn == piece.colour:
                # Make the move in a temporary game and check if the king can still be taken
                temporary_game = self.create_temp_game()
                temporary_move = self.create_temp_move(move, temporary_game)
                temporary_game.move_piece(temporary_move)
                if temporary_game.in_check(self.turn):
                    return False
                return True
        return False
