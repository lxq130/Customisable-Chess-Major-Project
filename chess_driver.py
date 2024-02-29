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

set_working_dir()


class Chess:
    def __init__(self, sounds, board_config):
        """Initialise"""
        p.init()  # Initialises pygame
        p.display.set_caption("Chess")
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        self.board_scn = p.Surface(
            (board_config.width, board_config.width)
        )  # Board surface
        self.renderer = Renderer(self.board_scn, board_config)
        self.board_config = board_config
        self.dragger = Dragger()
        self.game = Game(board_config.board)
        self.sounds = sounds
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

        while True:
            screen.blit(self.bg, (0, 0))

            # Draw the board
            screen.blit(board_scn, board_config.gs_pos)

            # Pause button
            pause_button = Button(
                pos=(WIDTH - 20, 20),
                alignment="topright",
                image=p.image.load(os.path.join("assets", "icons", "pause.png")),
                scale=0.15,
            )
            pause_button.draw(screen)

            renderer.draw_all(game, dragger.piece)

            if game.check_checkmate():
                return game.turn

            clicked_coords = get_board_coords(dragger.initial_pos, board_config)
            if dragger.dragging:
                dragger.update_blit(screen, renderer.images)
                renderer.draw_moves(piece, game, clicked_coords, display_all=review)

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
                            renderer.draw_check(game)

                            renderer.draw_moves(
                                piece, game, clicked_coords, display_all=review
                            )
                            renderer.draw_pieces(board, dragger.piece)

                # Moving Mouse
                elif event.type == p.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        renderer.draw_board(board)
                        renderer.draw_check(game)
                        renderer.draw_moves(
                            piece, game, clicked_coords, display_all=review
                        )
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
                            renderer.draw_all(game, dragger.piece)
                            if game.can_pawn_promote(move):
                                promoted_piece = renderer.get_promoted_piece(
                                    move, sounds, screen, board_config.gs_pos
                                )
                                game.pawn_promote(move, promoted_piece)
                                game.switch_turn()

                # Handles key pressing
                if event.type == p.KEYDOWN:
                    # Undo a move if z is pressed
                    if event.key == p.K_z:
                        if len(game.move_log) > 0:
                            sounds.move.play(sounds.sfx_on)
                            game.undo_move()

                    # Redo a move if x is pressed
                    if event.key == p.K_x:
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

            clock.tick(FPS)  # Ensures the program does not run faster than the set FPS.
            p.display.update()


# from sound import Sounds

# sounds = Sounds()
# chess = Chess(sounds)
# chess.run_and_get_winner()
