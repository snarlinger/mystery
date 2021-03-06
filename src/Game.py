# Game
# Main game class - everything is centralised here.
# By snarlinger (@gmail.com)
# Released under an MIT license

from pygame import K_RETURN, K_SPACE
import pygame.freetype
from os import path, remove, rename

from src.Mouse import MouseState
from src.DialogueState import *

pygame.init()


class Game:
    """ Main game class. """
    FPS = 60
    WH = (640, 480)
    BG_COLOUR = (0, 0, 0)
    # game box
    X_OFFSET = 0
    Y_OFFSET = 5
    X1 = WH[0] / 4 - X_OFFSET
    X2 = WH[0] / 2 + WH[0] / 4 - X_OFFSET
    Y1 = Y_OFFSET
    Y2 = WH[1] - Y_OFFSET
    POINTLIST = [(X1, Y1), (X2, Y1), (X2, Y2), (X1, Y2)]
    BOXWIDTH = 1

    def __init__(self):
        """ Initialises everything for the first time. """
        self.savefile = self.load()
        # display
        self.display = pygame.display.set_mode(self.WH)
        self.clock = pygame.time.Clock()
        # dialogue state
        self.state = DialogueState(self.savefile, self.X1, self.X2, self.Y1, self.display)

    def create_file(self):
        pass

    def load(self) -> dict:
        """ Loading attributes from save file. """
        # opening save file
        try:
            file = open(path.join('save', 'save.txt'))
        except FileNotFoundError:
            file = self.create_file()  # TODO - create file
        # trying to read and split lines
        try:
            lines = file.read().splitlines()
        except OSError:
            file = self.create_file()  # TODO - create file
            lines = file.read().splitlines()
        file.close()
        # storing attributes
        save = {}
        for line in lines:
            # trying to find equals separator
            try:
                sep = line.index('=')
            except ValueError:
                raise ValueError('Save malformed.')
            # store attribute
            save[line[:sep]] = line[sep + 1:]

        return save

    def save(self):
        """ Writes self.save to a new save file. """
        # generate lines
        lines = []
        for item in self.savefile.items():
            lines.append(item[0] + '=' + item[1] + '\n')
        # write to new save
        new_save = open(path.join('save', 'savetemp.txt'), 'w+')
        new_save.writelines(lines)
        new_save.close()
        # delete old and rename new
        remove(path.join('save', 'save.txt'))
        rename(path.join('save', 'savetemp.txt'), path.join('save', 'save.txt'))

    def main(self):
        """ Initiates the main game loop. """
        self.state.update_millis_since()
        while True:
            self.event_handling()
            self.update()
            self.blit()
            # enforce FPS and flip display
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def mouse_events(self, mousestate: MouseState):
        coord = pygame.mouse.get_pos()
        self.state.mouse_events(coord, mousestate)

    def dialogue_progression(self):
        """ Handles dialogue progression. """
        if self.state.animating:
            # if we're still animating, skip animation
            self.state.para_groups[self.state.p].max_index()
        else:
            self.state.next_paragraph()

    def event_handling(self):
        """ Main event handling function. Handles top-level events and calls to other event functions. """
        mouse_click = False
        for e in pygame.event.get():
            # quit
            if e.type == pygame.QUIT:
                sys.exit()
            # keys
            elif e.type == pygame.KEYUP:
                if e.key == K_RETURN or e.key == K_SPACE:
                    self.dialogue_progression()
                if e.key == pygame.K_s:
                    self.save()
            # mouse
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.mouse_events(MouseState.DOWN)
                mouse_click = True
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.mouse_events(MouseState.UP)
                if not self.state.xml_changed:
                    self.dialogue_progression()
                else:
                    self.state.xml_changed = False
                mouse_click = True
        # button held after MOUSEBUTTONDOWN or not held at all
        if not mouse_click:
            if pygame.mouse.get_pressed()[0]:
                self.mouse_events(MouseState.HELD)
            else:
                self.mouse_events(MouseState.NONE)

    def update(self):
        """ Updates the states of everything. """
        # background
        # everything else
        self.state.update()

    def blit(self):
        """ Blits everything to the display. """
        # background
        self.display.fill(self.BG_COLOUR)
        # dialogue
        self.state.blit()
        # dialogue box
        pygame.draw.lines(self.display, (255, 255, 255), True, self.POINTLIST, self.BOXWIDTH)
        # buttons?
        # inventory items
        # menu button


if __name__ == "__main__":
    game = Game()
    # for spr in game.state.para_groups[0]:
    #     print(spr.char, end="", flush=True)
    # print()
    # for spr in game.state.para_groups[0]:
    #     print(spr.char + ": " + str(spr.should_anim))
    # game.state.next_paragraph()
    # for spr in game.state.para_groups[0]:
    #     print(spr.char, end="", flush=True)
    game.main()
