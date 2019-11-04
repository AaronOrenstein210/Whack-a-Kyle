# Created on 18 October 2019

import pygame
from pygame.locals import MOUSEBUTTONUP, BUTTON_LEFT, QUIT, BUTTON_WHEELUP, BUTTON_WHEELDOWN
from random import randint
from hole import Hole, DONE, UP, HIT
from math import log, ceil

BKGRND = (0, 64, 0)
STAR = pygame.image.load("star.png")


class GameDriver:
    def __init__(self, display, levels):
        self.duration, self.time, self.points = 0, 0, 0
        self.done = False
        self.levels, self.current = levels, 0
        # Get dimensions
        self.dim = display.get_size()
        # Set rectangles
        self.top_rect = pygame.Rect(0, 0, self.dim[0], int(self.dim[1] / 10))
        self.screen = pygame.Rect(0, self.top_rect.bottom, self.dim[0], int(self.dim[1] * 9 / 10))
        pygame.draw.rect(display, (100, 100, 100), self.top_rect)
        # Set various variables
        self.hole_w = self.top_rect.h
        self.num_holes, self.num_gophers = 0, 1
        self.holes = []
        self.choose_level, self.scroll = None, 0
        self.choose_rect = pygame.Rect(0, 0, int(self.screen.w / 2), self.screen.h)
        self.choose_rect.center = self.screen.center

        self.show_levels()
        self.relocate_holes()
        self.update_top(display)

    def run(self, events, display, dt):
        self.time = max(0, self.time - dt)
        # If we ran out of time, end level
        if self.time == 0 and not self.done:
            self.done = True
            # Update screen one more time
            self.draw_display(display)
            self.update_top(display)
            # Display playable levels
            s = pygame.Surface(self.choose_rect.size)
            s.blit(self.choose_level, (0, self.scroll))
            display.blit(s, self.choose_rect)

        for h in self.holes:
            h.tick(dt, self.duration)

        for e in events:
            if e.type == QUIT:
                return False
            elif e.type == MOUSEBUTTONUP:
                if e.button == BUTTON_LEFT:
                    pos = pygame.mouse.get_pos()
                    if not self.done:
                        # If we are playing and left clicked, try to click each hole
                        for h1 in self.holes:
                            self.points += h1.on_click(pygame.mouse.get_pos())
                        self.duration = int(1000 / log(self.points)) if self.points > 1 else self.duration
                    elif self.choose_rect.collidepoint(pos[0], pos[1]):
                        _pos = (pos[0] - self.choose_rect.x, pos[1] - self.choose_rect.y - self.scroll)
                        item_w = int(self.choose_rect.w / 5)
                        col, row = int(_pos[0] / item_w), int(_pos[1] / item_w)
                        self.current = (row * 5) + col
                        self.load_level()
                elif self.done and e.button == BUTTON_WHEELUP or e.button == BUTTON_WHEELDOWN:
                    # Scroll level selector
                    pos = pygame.mouse.get_pos()
                    if self.choose_rect.collidepoint(pos[0], pos[1]):
                        self.scroll += 10 if e.button == BUTTON_WHEELUP else -10
                        # Can't scroll further than the excess view height
                        self.scroll = max(self.scroll, self.choose_rect.h - self.choose_level.get_size()[1])
                        # Offset can't be greater than zero
                        self.scroll = min(0, self.scroll)
                        s = pygame.Surface(self.choose_rect.size)
                        s.blit(self.choose_level, (0, self.scroll))
                        display.blit(s, self.choose_rect)

        if not self.done:
            if self.all_done():
                self.start_gopher()
            self.draw_display(display)
            self.update_top(display)

        return True

    def relocate_holes(self):
        self.holes.clear()
        for i in range(self.num_holes):
            pos = (randint(0, self.dim[1] - self.hole_w), randint(self.screen.y, self.dim[1] - self.hole_w))
            unique = False
            while not unique:
                unique = True
                for h in self.holes:
                    r = pygame.Rect(pos[0], pos[1], self.hole_w, self.hole_w)
                    if r.colliderect(h.rect.move(h.pos[0], h.pos[1])):
                        pos = (randint(0, self.dim[1] - self.hole_w),
                               randint(self.screen.y, self.dim[1] - self.hole_w))
                        unique = False
                        break
            self.holes.append(Hole(pos, (self.hole_w, self.hole_w)))

    def draw_display(self, display):
        # Draw board
        global BKGRND
        display.fill(BKGRND, self.screen)
        hit = {}
        for h in self.holes:
            surface, pos = h.get_display()
            display.blit(surface, pos)
            if h.status == HIT:
                surface, pos = h.get_spin()
                hit[surface] = pos
        for surface in hit.keys():
            display.blit(surface, hit[surface])
        hit.clear()

    def all_done(self):
        for h in self.holes:
            if h.status != DONE:
                return False
        return True

    def start_gopher(self):
        going = []
        for i in range(self.num_gophers):
            if len(going) != len(self.holes):
                idx = randint(0, len(self.holes) - 1)
                while idx in going:
                    idx = randint(0, len(self.holes) - 1)
                self.holes[idx].status = UP
                going.append(idx)

    def update_top(self, display):
        display.fill((100, 100, 100), self.top_rect)
        font_type = "Times New Roman"
        strs = [str(self.points), secs_to_string(int(self.time / 1000))]
        font = get_scaled_font(int(self.top_rect.w / 2), self.top_rect.h, get_widest_string(strs, font_type), font_type)
        for i, text in enumerate(strs):
            text = font.render(text, 1, (255, 255, 255))
            text_rect = text.get_rect(center=(int(self.dim[0] * (1 + 2 * i) / 4), self.top_rect.centery))
            display.blit(text, text_rect)

    def show_levels(self):
        global STAR
        stars = []
        for i in range(3):
            r = STAR.get_rect()
            s = pygame.Surface((r.w * 3, r.h), pygame.SRCALPHA)
            if i == 0:
                s.blit(STAR, (0, 0))

        item_w = int(self.choose_rect.w / 5)
        text_w = int(item_w * 9 / 10)
        col_w = 5
        num = len(self.levels)
        digits = len(str(num))
        fonts = []
        for i in range(digits):
            max_str = "0" * i
            fonts.append(get_scaled_font(text_w, text_w, max_str, "Times New Roman"))
        row, col = 0, 0
        self.choose_level = pygame.Surface((self.choose_rect.w, item_w * ceil(num / col_w)))
        for i in range(num):
            r = pygame.Rect(0, 0, text_w, text_w)
            r.center = (item_w * (.5 + col), item_w * (.5 + row))
            text = fonts[len(str(i)) - 1].render(str(i + 1), 1, (255, 255, 255))
            text_rect = text.get_rect(center=r.center)
            pygame.draw.rect(self.choose_level, (64, 64, 64), r)
            self.choose_level.blit(text, text_rect)

            col = (col + 1) % col_w
            if col == 0:
                row += 1

    def load_level(self):
        self.duration, self.points = 1000, 0
        self.done = False
        self.num_holes, self.time = self.levels[self.current]
        self.time *= 1000
        self.relocate_holes()


# Gets the biggest font that fits the text within max_w and max_H
def get_scaled_font(max_w, max_h, text, font_name):
    font_size = 0
    font = pygame.font.SysFont(font_name, font_size)
    w, h = font.size(text)
    while w < max_w and h < max_h:
        font_size += 1
        font = pygame.font.SysFont(font_name, font_size)
        w, h = font.size(text)
    return pygame.font.SysFont(font_name, font_size - 1)


def get_widest_string(strs, font_type):
    biggest = ""
    last_w = 0
    font = pygame.font.SysFont(font_type, 12)
    for text in strs:
        if font.size(text)[0] > last_w:
            biggest = text
            last_w = font.size(text)[0]
    return biggest


# Converts a number of seconds into a string
# Returns a the time as a string in the format hh...:mm:ss
def secs_to_string(num_secs):
    if num_secs <= 0:
        return "00:00:00"
    secs = int(num_secs % 60)
    secs_filler = ":" if secs >= 10 else ":0"
    mins = int(num_secs / 60) % 60
    mins_filler = ":" if mins >= 10 else ":0"
    hours = int(num_secs / 3600)
    return str(hours) + mins_filler + str(mins) + secs_filler + str(secs)
