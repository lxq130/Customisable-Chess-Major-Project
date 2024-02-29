import pygame as p
from constants import *


class Button:
    def __init__(
        self,
        pos,
        alignment="center",
        width=-1,
        height=-1,
        text_input="",
        image=None,
        scale=1,
        font=None,
        base_colour="black",
        hovering_colour="white",
        button_colour=None,
    ):
        """Initialises the button. Image is optional."""
        self.pos = pos
        self.font = font if font is not None else p.font.SysFont("arial", 15)
        self.base_color = base_colour
        self.hovering_color = hovering_colour
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.image = self.text if image is None else image
        self.button_colour = button_colour

        # Scale the image
        image_width = self.image.get_width()
        image_height = self.image.get_height()
        if width != -1:
            image_width = width
        if height != -1:
            image_height = height
        self.image = p.transform.scale(self.image, (int(image_width * scale), int(image_height * scale)))

        # Create the rectangle holding the image and text
        if alignment == "center":
            self.rect = self.image.get_rect(center=(self.pos[0], self.pos[1]))
            self.text_rect = self.text.get_rect(center=self.rect.center)
        elif alignment == "topleft":
            self.rect = self.image.get_rect(topleft=(self.pos[0], self.pos[1]))
            self.text_rect = self.text.get_rect(center=self.rect.center)
        elif alignment == "topright":
            self.rect = self.image.get_rect(topright=(self.pos[0], self.pos[1]))
            self.text_rect = self.text.get_rect(center=self.rect.center)
        elif alignment == "bottomright":
            self.rect = self.image.get_rect(bottomright=(self.pos[0], self.pos[1]))
            self.text_rect = self.text.get_rect(center=self.rect.center)
        elif alignment == "bottomleft":
            self.rect = self.image.get_rect(bottomleft=(self.pos[0], self.pos[1]))
            self.text_rect = self.text.get_rect(center=self.rect.center)

        if image is None:
            self.image.fill(button_colour)

    def draw(self, screen):
        """Draws the button on screen."""
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_input(self, position):
        """Check that position is in the button."""
        return position[0] in range(self.rect.left, self.rect.right) and position[1] in range(
            self.rect.top, self.rect.bottom
        )

    def change_colour(self, position):
        """If position is in the button, change the colour of the button."""
        if self.font is not None:
            if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(
                self.rect.top, self.rect.bottom
            ):
                self.text = self.font.render(self.text_input, True, self.hovering_color)
            else:
                self.text = self.font.render(self.text_input, True, self.base_color)
