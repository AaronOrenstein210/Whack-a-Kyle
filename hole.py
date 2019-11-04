# Created on 15 October 2019

from pygame import Rect, Surface, SRCALPHA
from pygame.draw import circle
from pygame.transform import scale, rotate
from pygame.image import load
from pygame.mixer import music

UP, WAIT, DOWN, DONE, HIT = 0, 1, 2, 3, 4


class Hole:
    def __init__(self, pos, dim):
        self.pos = pos
        self.rect = Rect(0, 0, dim[0], dim[1])
        self.time = 0
        self.sprite_rect = Rect(int(dim[0] / 4), int(dim[1] / 2), int(dim[0] / 2), 0)
        self.hole, self.sprite = None, None
        global DONE
        self.status = DONE
        self.create_surfaces()

    def create_surfaces(self):
        self.hole = Surface((self.rect.w, self.rect.h), SRCALPHA)
        circle(self.hole, (0, 0, 0), self.rect.center, self.rect.centerx)
        circle(self.hole, (150, 75, 0), self.rect.center, self.rect.centerx, 3)
        self.sprite = Surface.convert_alpha(scale(load("face.jpg"), (self.sprite_rect.w, self.sprite_rect.w)))

    def get_display(self):
        global HIT
        if self.sprite_rect.h == 0 or self.status == HIT:
            return self.hole, self.pos
        else:
            s = Surface((self.hole.get_size()))
            s.fill((0, 64, 0))
            s.blit(self.hole, (0, 0))
            temp = Surface((self.sprite_rect.w, self.sprite_rect.h))
            temp.blit(self.sprite, (0, 0))
            s.blit(temp, self.sprite_rect)
            return s, self.pos

    def get_spin(self):
        time_frac = self.time / 1000
        rotation = int(time_frac * 360)
        max_d = self.sprite_rect.w
        dx = int(max_d * time_frac)
        dy = int((4 * dx / max_d) * (dx - max_d))
        return rotate(self.sprite, rotation), (self.pos[0] - dx, self.pos[1] + dy)

    def tick(self, dt, wait_duration):
        global UP, WAIT, DOWN, DONE, HIT
        if self.status != DONE:
            self.time += dt
            if self.status == UP and self.time >= 25:
                self.sprite_rect.y = max(0, self.sprite_rect.y - 2)
                self.sprite_rect.h = min(self.sprite_rect.w, self.sprite_rect.h + 2)
                if self.sprite_rect.y == 0:
                    self.status = WAIT
                self.time = 0
            elif self.status == DOWN and self.time >= 25:
                self.sprite_rect.y = min(self.rect.centery, self.sprite_rect.y + 2)
                self.sprite_rect.h = max(0, self.sprite_rect.h - 2)
                if self.sprite_rect.h == 0:
                    self.status = DONE
                self.time = 0
            elif self.status == WAIT and self.time >= wait_duration:
                self.status = DOWN
                self.time = 0
            elif self.status == HIT and self.time >= 1000:
                self.status = DONE
                self.time = 0

    def on_click(self, pos):
        pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
        if self.sprite_rect.h != 0 and self.sprite_rect.collidepoint(pos[0], pos[1]):
            global HIT
            self.status = HIT
            self.time = 0
            self.sprite_rect.h, self.sprite_rect.y = 0, int(self.rect.centery)
            music.load("ow.mp3")
            music.play(0, 0)
            return 1
        return 0
