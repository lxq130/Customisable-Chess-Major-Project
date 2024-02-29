import pygame as p
from constants import *
from piece import *


class Dragger:
    def __init__(self):
        self.mouse_pos = [0, 0]
        self.initial_pos = [0, 0]
        self.piece = Empty()
        self.dragging = False

    def update_blit(self, screen, images):
        image = images[self.piece.name_colour]
        width = image.get_rect().width
        height = image.get_rect().height
        image = p.transform.scale(image, (width * 1.25, height * 1.25))

        image_centre = tuple(self.mouse_pos)
        screen.blit(image, image.get_rect(center=image_centre))

    def update_mouse(self, position):
        """Note that position is in the form (x, y)"""
        self.mouse_pos = list(position)

    def save_initial(self, position):
        self.initial_pos = position

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = Empty()
        self.dragging = False
