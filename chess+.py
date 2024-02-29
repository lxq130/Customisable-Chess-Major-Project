from helper import *
import pygame as p
import sys
from constants import *
from chess_driver import Chess
from button import Button
from sound import Sounds
from customiser import Customiser
from piece import *
from board import Board

# Note that pos denotes the position on the screen (e.g. (100, 100)) and coords denotes the coordinate on the chessboard (0, 1)
set_working_dir()


class Main:
    def __init__(self):
        p.init()
        p.display.set_caption("Chess +")
        self.bg = p.image.load("assets/icons/Background.png")
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        self.sounds = Sounds()
        self.board_config = Board()

    def title_screen(self):
        """Draws title screen and buttons."""
        screen = self.screen
        sounds = self.sounds
        bg = self.bg

        while True:
            screen.blit(bg, (0, 0))
            mouse_pos = p.mouse.get_pos()
            draw_text(screen, size=50, text="CHESS+", pos=(WIDTH // 2, HEIGHT * 3 // 8))

            play_button = Button(
                image=p.image.load(os.path.join("assets", "icons", "Play Button.png")),
                pos=(WIDTH // 2, HEIGHT * 2 // 3),
                text_input="PLAY",
                font=get_font(40),
                base_colour=RED_1,
                hovering_colour="White",
                scale=0.7,
            )

            play_button.change_colour(mouse_pos)
            play_button.draw(screen)

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.MOUSEBUTTONDOWN:
                    if play_button.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        self.menu()

            p.display.update()

    def menu(self):
        """Draws main menu and buttons."""
        screen = self.screen
        sounds = self.sounds
        bg = self.bg

        while True:
            screen.blit(bg, (0, 0))
            mouse_pos = p.mouse.get_pos()
            draw_text(screen, size=50, text="MENU")

            menu_length = (WIDTH - 2.5 * margin(WIDTH)) // 2
            chess_button = Button(
                pos=(margin(WIDTH), HEIGHT * 2 // 8),
                alignment="topleft",
                width=menu_length,
                height=menu_length,
                image=p.image.load(os.path.join("assets", "icons", "chessboard.png")),
            )
            chess_button_2 = Button(
                image=p.image.load(os.path.join("assets", "icons", "Play Button.png")),
                pos=(margin(WIDTH), menu_length * 2 // 8 + 460),
                text_input="CLASSIC",
                alignment="topleft",
                font=get_font(30),
                base_colour=RED_1,
                hovering_colour="White",
                scale=0.7,
            )

            customiser_button = Button(
                pos=(WIDTH - margin(WIDTH), HEIGHT * 2 // 8),
                alignment="topright",
                width=menu_length,
                height=menu_length,
                image=p.image.load(os.path.join("assets", "icons", "custom.webp")),
            )

            custom_button_2 = Button(
                image=p.image.load(os.path.join("assets", "icons", "Play Button.png")),
                pos=(1.5 * margin(WIDTH) + menu_length, menu_length * 2 // 8 + 460),
                text_input="CUSTOM",
                alignment="topleft",
                font=get_font(30),
                base_colour=RED_1,
                hovering_colour="White",
                scale=0.7,
            )

            for button in [
                chess_button,
                customiser_button,
                chess_button_2,
                custom_button_2,
            ]:
                button.draw(screen)

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.MOUSEBUTTONDOWN:
                    if chess_button.check_input(
                        mouse_pos
                    ) or chess_button_2.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        self.chess(mode="classic")
                    if customiser_button.check_input(
                        mouse_pos
                    ) or custom_button_2.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        self.customiser()

            p.display.update()

    def chess(self, mode):
        if mode == "classic":
            self.board_config.set_default()
        chess = Chess(self.sounds, self.board_config)
        winner = chess.run_and_get_winner()
        if winner != "quit":
            output = self.game_over(winner)
            if output == "review":
                chess.run_and_get_winner(review=True)

    def customiser(self):
        customiser = Customiser(self.screen, self.sounds, self.board_config)
        play = customiser.run()
        if play:
            self.chess(mode="custom")

    def game_over(self, winner):
        sounds = self.sounds
        screen = self.screen

        win_screen = (
            WIDTH // 2 - WIDTH_1 // 2,
            HEIGHT // 2 - HEIGHT_1 // 2,
            WIDTH_1,
            HEIGHT_1,
        )

        x_left = (WIDTH - WIDTH_1) // 2 + margin(WIDTH_1)
        x_right = WIDTH - x_left
        y = (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 18 // 20 - 20

        while True:
            mouse_pos = p.mouse.get_pos()
            # Draws background
            p.draw.rect(screen, BG_2, win_screen, 0, 10)
            # Draws border
            p.draw.rect(screen, BORDER, win_screen, 5, 5)

            # Title
            draw_text(
                screen,
                size=35,
                text="GAME OVER",
                pos=(WIDTH // 2, (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 4 // 20),
                colour=YELLOW,
            )

            # Victory Message
            draw_text(
                screen,
                size=30,
                text="Victory:",
                pos=(WIDTH // 2, (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 8 // 20),
            )

            draw_text(
                screen,
                size=30,
                text=winner.capitalize(),
                pos=(WIDTH // 2, (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 11 // 20),
            )

            # Quit
            quit = Button(
                pos=(x_left, y),
                alignment="topleft",
                width=WIDTH_1 // 4,
                height=HEIGHT_1 // 20 + 5 * HEIGHT // 200,
                text_input="QUIT",
                font=get_font(20),
                base_colour=WHITE,
                hovering_colour=WHITE,
                button_colour=RED_1,
            )
            quit.draw(screen)

            # Review
            review = Button(
                pos=(x_right, y),
                alignment="topright",
                width=WIDTH_1 // 4 + 50,
                height=HEIGHT_1 // 20 + 5 * HEIGHT // 200,
                text_input="REVIEW",
                font=get_font(20),
                base_colour=WHITE,
                hovering_colour=WHITE,
                button_colour=GREEN,
            )
            review.draw(screen)

            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.MOUSEBUTTONDOWN:
                    if quit.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        return "quit"
                    if review.check_input(mouse_pos):
                        sounds.click.play(sounds.sfx_on)
                        return "review"

            p.display.update()


if __name__ == "__main__":
    main = Main()
    # main.game_over("white")
    main.title_screen()
