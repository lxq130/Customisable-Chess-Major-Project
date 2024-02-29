import pygame as p
import sys
from game_logic import Game
from constants import *
from dragger import Dragger
from renderer import Renderer
from helper import *
from pause import paused
from button import Button
from pause import *
from move import Move
from piece import *

set_working_dir()


class Chess:
    def __init__(self, sounds, board_config, classic):
        """Initialise"""
        p.init()  # Initialises pygame
        p.display.set_caption("Chess")
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        self.board_scn = p.Surface((board_config.width, board_config.width))  # Board surface
        self.renderer = Renderer(self.board_scn, board_config, classic)
        self.board_config = board_config
        self.dragger = Dragger()
        self.game = Game(board_config.board)
        self.sounds = sounds
        self.classic = board_config.is_classic()
        self.timer_on = True

    def run_and_get_winner(self, review=False):
        """Main game loop"""
        screen = self.screen
        game = self.game
        dragger = self.dragger
        renderer = self.renderer
        board = game.board
        sounds = self.sounds
        board_scn = self.board_scn
        board_config = self.board_config

        self.bg = p.image.load("assets/icons/Background.png")

        clock = p.time.Clock()  # Creates a clock.

        # This flag is set to true when the first move is made.
        begun = False

        while True:
            screen.blit(self.bg, (0, 0))

            # Display a title if review mode is on
            if review:
                draw_text(
                    screen,
                    size=20,
                    text="GAME REVIEW",
                    pos=(
                        WIDTH // 2,
                        HEIGHT * 1 // 19,
                    ),
                    colour=L_GREEN,
                )

            # Draw the board
            screen.blit(board_scn, board_config.gs_pos)

            # Pause button
            pause_button = Button(
                pos=(WIDTH - 20, 20),
                alignment="topright",
                image=p.image.load(os.path.join("assets", "icons", "pause.png")),
                scale=0.12,
            )
            pause_button.draw(screen)

            if not review:
                if game.check_gameover() == "Checkmate":
                    # Note that the turn has already been switched inside check_gameover().
                    # If both players are checkmated (can only happen in custom games), draw
                    if game.check_gameover() == "Checkmate":
                        return "Draw"
                    return game.turn
                elif game.check_gameover() == "Draw":
                    return "Draw"

            renderer.draw_all(game, dragger.piece, review)

            # Draws redo button
            redo_icon = p.image.load(os.path.join("assets", "icons", "redo.png"))
            redo_button = Button(
                pos=(WIDTH // 2 + 10, 600),
                alignment="topleft",
                image=redo_icon,
                scale=1,
            )
            redo_button.draw(screen)

            # Draws undo button
            undo_icon = p.transform.flip(redo_icon, True, False)
            undo_button = Button(
                pos=(WIDTH // 2 - 10, 600),
                alignment="topright",
                image=undo_icon,
                scale=1,
            )
            undo_button.draw(screen)

            clicked_coords = get_board_coords(dragger.initial_pos, board_config)
            if dragger.dragging:
                dragger.update_blit(screen, renderer.images)
                renderer.draw_moves(piece, game, clicked_coords, display_all=review)

            # Only check for instant game promotions at the start of a custom game
            if not begun and not review and not self.classic:
                self.check_instant_promo()

            # This loop is used for keyboard presses, mouse presses etc.
            for event in p.event.get():
                mouse_pos = p.mouse.get_pos()

                # Quit
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()

                # Dragging

                # Click
                if event.type == p.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_coords = get_board_coords(dragger.mouse_pos, board_config)

                    if in_board(board_config, pos=dragger.mouse_pos):
                        # Check that the clicked coordinate has a piece
                        if board[clicked_coords[1]][clicked_coords[0]].name != "Empty":
                            sounds.click.play(sounds.sfx_on)
                            piece = board[clicked_coords[1]][clicked_coords[0]]
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                            renderer.draw_board(board)
                            renderer.draw_check(game, review)

                            renderer.draw_moves(piece, game, clicked_coords, display_all=review)
                            renderer.draw_pieces(board, dragger.piece)

                # Moving Mouse
                elif event.type == p.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        renderer.draw_board(board)
                        renderer.draw_check(game, review)
                        renderer.draw_moves(piece, game, clicked_coords, display_all=review)
                        renderer.draw_pieces(board, dragger.piece)
                        dragger.update_blit(screen, renderer.images)

                # Release
                elif event.type == p.MOUSEBUTTONUP:
                    dragger.undrag_piece()

                    coords_f = get_board_coords(dragger.mouse_pos, board_config)

                    if in_board(board_config, pos=dragger.mouse_pos) and not review:
                        move = Move(
                            get_board_coords(dragger.initial_pos, board_config),
                            coords_f,
                            board,
                        )

                        if game.validate_move(move):
                            # Check if a piece was captured
                            if move.piece_captured.opponent_colour == game.turn:
                                sounds.capture.play(sounds.sfx_on)
                            else:
                                sounds.move.play(sounds.sfx_on)
                            game.move_piece(move)
                            begun = True
                            renderer.draw_all(game, dragger.piece, review)
                            if game.can_pawn_promote(move):
                                promoted_piece = self.renderer.get_promoted_piece(
                                    move,
                                    self.sounds,
                                    self.screen,
                                    self.board_config.gs_pos,
                                    self.board_config.width,
                                    self.game.board,
                                    self.dragger.piece,
                                )
                                move.piece_moved.transform_into = promoted_piece
                                game.pawn_promote(move, promoted_piece)
                                game.switch_turn()

                # Handles key pressing
                if event.type == p.KEYDOWN:
                    # Undo a move if z is pressed
                    if event.key == p.K_LEFT:
                        if len(game.move_log) > 0:
                            sounds.move.play(sounds.sfx_on)
                            game.undo_move()

                    # Redo a move if x is pressed
                    if event.key == p.K_RIGHT:
                        if len(game.undo_log) > 0:
                            sounds.move.play(sounds.sfx_on)
                            game.redo_move()

                # Button presses
                if event.type == p.MOUSEBUTTONDOWN:
                    if pause_button.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        output = paused(self, sounds, screen)
                        if output == "quit":
                            return "quit"

                    if redo_button.check_input(mouse_pos):
                        if len(game.undo_log) > 0:
                            sounds.move.play(sounds.sfx_on)
                            game.redo_move()

                    if undo_button.check_input(mouse_pos):
                        if len(game.move_log) > 0:
                            sounds.move.play(sounds.sfx_on)
                            game.undo_move()

            clock.tick(FPS)  # Ensures the program does not run faster than the set FPS.
            p.display.update()

    def check_instant_promo(self):
        # Check if any pawns are promotable. If so force the player to promote the pawn first.
        y = -1
        # Only the top and bottom rows need to be checked for promotable pawns
        top_and_bottom_rows = [self.game.board[0]] + [self.game.board[-1]]
        for row in top_and_bottom_rows:
            y = 0 if y == -1 else len(self.game.board) - 1  # Sets the y coordinate to be searched.
            for x, piece in enumerate(row):
                move = Move((1, 1), (x, y), self.game.board)
                move.piece_moved = piece
                if self.game.can_pawn_promote(move):
                    promoted_piece = self.renderer.get_promoted_piece(
                        move,
                        self.sounds,
                        self.screen,
                        self.board_config.gs_pos,
                        self.board_config.width,
                        self.game.board,
                        self.dragger.piece,
                    )
                    move.piece_moved.transform_into = promoted_piece
                    self.game.pawn_promote(move, promoted_piece)
                    self.game.switch_turn()
