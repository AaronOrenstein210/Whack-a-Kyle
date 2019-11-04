# Created on 15 October 2019

import pygame
from pygame.locals import *
from sys import exit
from math import log
from gameDriver import GameDriver, BKGRND

open("levels.txt", "r+").close()

levels = []
for line in open("levels.txt", "r").readlines():
    # Each line contains: # holes, time, 1 star, 2 stars, 3 stars, best
    if line.endswith("\n"):
        line = line[:-1]
    info = []
    while "," in line:
        info.append(int(line[:line.index(",")]))
        line = line[line.index(",") + 1:]
    info.append(int(line))
    levels.append(info)

if len(levels) == 0:
    quit(1)

pygame.init()

w, h = 500, 500

display = pygame.display.set_mode((w, h))
display.fill(BKGRND)
driver = GameDriver(display, levels)

time = pygame.time.get_ticks()
while True:
    dt = pygame.time.get_ticks() - time
    time = pygame.time.get_ticks()

    if not driver.run(pygame.event.get(), display, dt):
        pygame.quit()
        exit(0)

    pygame.display.update()
