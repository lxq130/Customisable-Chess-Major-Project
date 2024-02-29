import pygame as p
from constants import *
from button import Button
from helper import *
import sys

set_working_dir()

p.init()


def paused(game, sounds, screen):
    pause_screen = (
        WIDTH // 2 - WIDTH_1 // 2,
        HEIGHT // 2 - HEIGHT_1 // 2,
        WIDTH_1,
        HEIGHT_1,
    )

    while True:
        mouse_pos = p.mouse.get_pos()
        # Draws background
        p.draw.rect(screen, BG_2, pause_screen, 0, 10)
        # Draws border
        p.draw.rect(screen, BORDER, pause_screen, 5, 5)

        # Pause title
        draw_text(
            screen,
            size=35,
            text="PAUSED",
            pos=(WIDTH // 2, (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 4 // 20),
            colour=L_GREEN,
        )

        # Sound Effects
        x_left = (WIDTH - WIDTH_1) // 2 + margin(WIDTH_1)
        y = (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 7 // 20
        draw_text(screen, size=12, text="Sound Effects", pos=(x_left, y), alignment="topleft")

        x_right = WIDTH - x_left
        y_up = y - HEIGHT // 200
        if sounds.sfx_on:
            text_input = "ON"
            colour = GREEN
        else:
            text_input = "OFF"
            colour = RED_1

        sfx_toggle = Button(
            pos=(x_right, y_up),
            alignment="topright",
            width=WIDTH_1 // 5,
            height=HEIGHT_1 // 20 + 2 * HEIGHT // 200,
            text_input=text_input,
            font=get_font(12),
            base_colour=WHITE,
            hovering_colour=WHITE,
            button_colour=colour,
        )
        sfx_toggle.draw(screen)

        # Timer Toggle
        # x_left = (WIDTH - WIDTH_1) // 2 + margin(WIDTH_1)
        # y = (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 9 // 20
        # draw_text(screen, size=12, text="Timer", alignment="topleft", pos=(x_left, y))

        # x_right = WIDTH - x_left
        # y_up = y - HEIGHT // 200
        # if game.timer_on:
        #     text_input = "ON"
        #     colour = GREEN
        # else:
        #     text_input = "OFF"
        #     colour = RED_1

        # timer_toggle = Button(
        #     pos=(x_right, y_up),
        #     alignment="topright",
        #     width=WIDTH_1 // 5,
        #     height=HEIGHT_1 // 20 + 2 * HEIGHT // 200,
        #     text_input=text_input,
        #     font=get_font(12),
        #     base_colour=WHITE,
        #     hovering_colour=WHITE,
        #     button_colour=colour,
        # )
        # timer_toggle.draw(screen)

        # Quit
        y = (HEIGHT - HEIGHT_1) // 2 + HEIGHT_1 * 18 // 20 - 20
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

        # Resume
        resume = Button(
            pos=(x_right, y),
            alignment="topright",
            width=WIDTH_1 // 4 + 50,
            height=HEIGHT_1 // 20 + 5 * HEIGHT // 200,
            text_input="RESUME",
            font=get_font(20),
            base_colour=WHITE,
            hovering_colour=WHITE,
            button_colour=GREEN,
        )
        resume.draw(screen)

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            if event.type == p.MOUSEBUTTONDOWN:
                if sfx_toggle.check_input(mouse_pos):
                    sounds.click.play(not sounds.sfx_on)
                    sounds.sfx_on = not sounds.sfx_on
                # if timer_toggle.check_input(mouse_pos):
                #     sounds.click.play(sounds.sfx_on)
                #     game.timer_on = False if game.timer_on else False
                if quit.check_input(mouse_pos):
                    sounds.click.play(sounds.sfx_on)
                    return "quit"
                if resume.check_input(mouse_pos):
                    sounds.click.play(sounds.sfx_on)
                    return

        p.display.update()
