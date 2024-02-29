import pygame as p
import os

p.init()


class Sound:
    def __init__(self, path):
        self.sound = p.mixer.Sound(path)

    def play(self, sfx_on):
        if sfx_on:
            p.mixer.Sound.play(self.sound)


class Sounds:
    def __init__(self):
        self.click = Sound(os.path.join("assets", "sounds", "click.wav"))
        self.move = Sound(os.path.join("assets", "sounds", "move.wav"))
        self.capture = Sound(os.path.join("assets", "sounds", "capture.wav"))
        self.sfx_on = True
