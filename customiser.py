import pygame as p
import sys
from constants import *
from button import Button
from helper import *
from renderer import Renderer
from dragger import Dragger
from piece import *
from pause import *
from board import Board

set_working_dir()


class Customiser:
    def __init__(self, screen, sounds, board_config):
        p.init()
        self.bg = p.image.load("assets/icons/Background.png")
        self.screen = screen
        self.sounds = sounds
        self.board_config = board_config
        self.dragger = Dragger()
        board = [[Empty() for e in range(8)] for i in range(8)]
        board[0][0] = King("black")
        board[-1][0] = King("white")
        self.custom_config = Board(width=416, gs_pos=(WIDTH // 20, HEIGHT * 16 // 30 - 416 // 2), board=board)
        self.timer_on = False

    def run(self):
        screen = self.screen
        sounds = self.sounds
        dragger = self.dragger
        custom_config = self.custom_config
        active = False  # True if textbox is selected
        board_config = self.board_config
        text = "Enter a number between 4 and 16 inclusive"
        right_click = False

        while True:
            screen.blit(self.bg, (0, 0))
            mouse_pos = p.mouse.get_pos()

            # Draws the title
            draw_text(
                screen,
                size=20,
                text="CUSTOMISER",
                pos=(
                    WIDTH // 2,
                    HEIGHT * 1 // 15,
                ),
                colour=L_GREEN,
            )

            # p_sqr_size is the square size for palette
            p_sqr_size = 52

            # Creates board as a surface
            board_scn = p.Surface((custom_config.width, custom_config.width))

            # GAMERULE SECTION

            # Panel background
            panel_size = (
                self.screen.get_width() - board_scn.get_width(),
                416,
            )
            panel = p.Surface(panel_size)
            # panel_pos's x value used to be board_config.width * 21 // 20 + WIDTH // 20
            panel_pos = (
                476,
                custom_config.gs_pos[1],
            )
            panel.blit(self.bg, (0, 0))

            draw_text(panel, size=15, text="Dimensions:", alignment="topleft", pos=(10, 10))

            screen.blit(panel, panel_pos)

            # TEXT BOX
            font = p.font.SysFont("arial", 15)

            input_rect = p.Rect(panel_pos[0] + 10, panel_pos[1] + 40, 255, 30)
            colour_on = GREEN
            colour_off = GREY
            colour = colour_on if active else colour_off
            p.draw.rect(screen, colour, input_rect, 3)
            text_surface = font.render(text, True, GREY)
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            input_rect.w = max(255, text_surface.get_width() + 10)

            # BIN
            bin_button = Button(
                pos=(panel_pos[0] + 10, panel_pos[1] + panel_size[1] - 25),
                alignment="bottomleft",
                image=p.image.load(os.path.join("assets", "icons", "bin.png")),
                scale=0.15,
            )
            bin_button.draw(screen)

            # RESET
            reset_button = Button(
                pos=(WIDTH - 20, panel_pos[1] + panel_size[1] - 25),
                alignment="bottomright",
                image=p.image.load(os.path.join("assets", "icons", "reset.png")),
                scale=1.2,
            )
            reset_button.draw(screen)

            # Draws board
            board_renderer = Renderer(board_scn, custom_config, classic=False)
            board_renderer.draw_board(custom_config.board)

            # Draws the pieces
            if right_click and dragger.piece.name != "King":
                board_renderer.draw_pieces(custom_config.board, None)
            else:
                board_renderer.draw_pieces(custom_config.board, dragger.piece)
            screen.blit(board_scn, custom_config.gs_pos)

            # Draw palettes
            # pos_w is the position of the white pallete, similarly for pos_b
            pos_w = (
                WIDTH // 20,
                custom_config.gs_pos[1] + board_scn.get_height() + HEIGHT // 50,
            )
            pos_b = (WIDTH // 20, custom_config.gs_pos[1] - p_sqr_size - HEIGHT // 50)
            palette_renderer = Renderer(screen, board_config, sqr_size=p_sqr_size, classic=False)
            palette_buttons = palette_renderer.draw_and_get_palettes(pos_w, pos_b)

            # Draw play button
            play_button = Button(
                image=p.image.load(os.path.join("assets", "icons", "play_bg.png")),
                pos=(WIDTH - 25, HEIGHT - 25),
                alignment="bottomright",
                text_input="PLAY",
                font=get_font(30),
                base_colour=RED_1,
                hovering_colour="White",
                scale=0.6,
            )
            play_button.change_colour(mouse_pos)
            play_button.draw(screen)

            # Pause button
            pause_button = Button(
                pos=((WIDTH - 20, 20)),
                alignment="topright",
                image=p.image.load(os.path.join("assets", "icons", "pause.png")),
                scale=0.12,
            )
            pause_button.draw(screen)

            # Draws the hovering piece
            if dragger.dragging:
                dragger.update_blit(screen, board_renderer.images)

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()

                # Click
                if event.type == p.MOUSEBUTTONDOWN:
                    # PAUSES
                    if pause_button.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        output = paused(self, sounds, screen)
                        if output == "quit":
                            return False

                    # PLAY BUTTON
                    if play_button.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        board_config.edit(board=custom_config.board, sqrs=custom_config.sqrs)
                        board_config.available_pieces = ALL_PIECES
                        return True

                    # RESET BUTTON
                    if reset_button.check_input(mouse_pos):
                        active = False
                        sounds.click.play(sounds.sfx_on)
                        custom_config.set_default()
                        text = "Enter a number between 4 and 16 inclusive"

                    # TEXT BOX
                    # Currently selected
                    if active and not input_rect.collidepoint(event.pos):
                        if valid_size(text):
                            custom_config.edit(sqrs=int(text))
                            prev_text = text
                        else:
                            text = prev_text
                        active = False
                        break
                    # Just clicked on it
                    if input_rect.collidepoint(event.pos):
                        prev_text = text
                        text = ""
                        active = True

                    # HANDLES PIECES
                    dragger.update_mouse(event.pos)
                    clicked_coords = get_board_coords(dragger.mouse_pos, custom_config)
                    selected_piece = Empty()

                    # If click is on the board and is a piece
                    if in_board(custom_config, pos=event.pos):
                        if custom_config.board[clicked_coords[1]][clicked_coords[0]].name != "Empty":
                            selected_piece = custom_config.board[clicked_coords[1]][clicked_coords[0]]

                    # Checks if a button on the palette is clicked
                    for piece, button in palette_buttons.items():
                        if button.check_input(mouse_pos):
                            sounds.click.play(sounds.sfx_on)
                            selected_piece = piece

                    # If the user clicked on a piece or palette button
                    if selected_piece.name != "Empty":
                        right_click = True if event.button == 3 else False
                        sounds.click.play(sounds.sfx_on)
                        dragger.save_initial(event.pos)
                        dragger.drag_piece(selected_piece)
                        board_renderer.draw_board(custom_config.board)
                        if right_click and dragger.piece != "King":
                            board_renderer.draw_pieces(custom_config.board, None)
                        else:
                            board_renderer.draw_pieces(custom_config.board, dragger.piece)

                # Mouse moving
                elif event.type == p.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        board_renderer.draw_board(custom_config.board)
                        if right_click and dragger.piece.name != "King":
                            board_renderer.draw_pieces(custom_config.board, None)
                        else:
                            board_renderer.draw_pieces(custom_config.board, dragger.piece)
                        dragger.update_blit(screen, board_renderer.images)

                # Release
                elif event.type == p.MOUSEBUTTONUP:
                    dragger.undrag_piece()

                    coords_f = get_board_coords(dragger.mouse_pos, custom_config)
                    coords_i = get_board_coords(dragger.initial_pos, custom_config)

                    # Releasing a piece over the bin
                    if in_board(custom_config, pos=dragger.initial_pos):
                        if bin_button.check_input(dragger.mouse_pos):
                            sounds.move.play(sounds.sfx_on)
                            if selected_piece.name != "Empty":
                                if selected_piece.name != "King":
                                    custom_config.board[coords_i[1]][coords_i[0]] = Empty()

                    # Releasing a piece on the board
                    if in_board(custom_config, pos=dragger.mouse_pos):
                        if (
                            selected_piece.name != "Empty"
                            and custom_config.board[coords_f[1]][coords_f[0]].name != "King"
                        ):
                            # If dragging from palette to board
                            if not in_board(custom_config, pos=dragger.initial_pos):
                                custom_config.board[coords_f[1]][coords_f[0]] = get_piece(selected_piece.name_colour)
                                sounds.move.play(sounds.sfx_on)
                            # If rearranging the order of pieces on the board
                            else:
                                # Repositioning pieces, note that king cannot be duplicated
                                if not right_click or selected_piece.name == "King":
                                    custom_config.board[coords_i[1]][coords_i[0]] = Empty()
                                custom_config.board[coords_f[1]][coords_f[0]] = get_piece(selected_piece.name_colour)
                                sounds.move.play(sounds.sfx_on)
                            board_renderer.draw_board(custom_config.board)
                            board_renderer.draw_pieces(custom_config.board, dragger.piece)

                # Keyboard presses
                elif event.type == p.KEYDOWN:
                    if active:
                        if event.key == p.K_BACKSPACE:
                            text = text[:-1]
                        elif event.key == p.K_RETURN:
                            if valid_size(text):
                                custom_config.edit(sqrs=int(text))
                                prev_text = text
                            else:
                                text = prev_text
                        # Typing
                        else:
                            # Clear the text box if this is the first thing being typed
                            if text == prev_text:
                                text = ""
                            text = "".join([char for char in text if char.isnumeric()])
                            text += event.unicode

            p.display.update()


def valid_size(text):
    if text.isnumeric():
        if int(text) in range(4, 17):
            return True
    return False
