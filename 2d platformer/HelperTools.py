import pygame
from pygame.locals import *

class TileSet:
    def __init__(self, filename, rowimages, columnimages, alphaCheck=None, scale=1, padding=0):
        
        self.filename = filename
        self.numRow = rowimages
        self.numCol = columnimages
        
        self.image = pygame.image.load(filename)
        width = self.image.get_size()[0]
        height = self.image.get_size()[1]

        if scale != 1:
            self.image = pygame.transform.scale(self.image, ((width*scale), (height*scale)))
            padding *= 2
            if alphaCheck:
                alphaCheck = (alphaCheck[0] * scale, alphaCheck[1] * scale)

        # list containing the dimensions for each individual image in spritesheet
        self.dimList = []

        regionSize = self.image.get_size()[0] // self.numCol
        self.tileSize = regionSize - padding
        
        for r in range(self.numRow):
            for c in range(self.numCol):
                self.dimList.append( [c * regionSize, r * regionSize, self.tileSize, self.tileSize])

        self.bkgd = None
        if alphaCheck:
            bkgd_color = self.image.get_at(alphaCheck)
            if(bkgd_color[3] != 255):
                self.bkgd = pygame.Color(bkgd_color[0], bkgd_color[1], bkgd_color[2], 255)
                for x in range(width):
                    for y in range(height):
                        if(bkgd_color == self.image.get_at((x,y))):
                            self.image.set_at((x,y), self.bkgd)
            else:
                self.bkgd = bkgd_color

    def drawTile(self, screen, left, top, imageNum):
        dim = self.dimList[imageNum]
        rect = pygame.Rect(dim)
        surface = pygame.Surface(rect.size).convert()

        if self.bkgd:
            surface.set_colorkey(self.bkgd, RLEACCEL)
        else:
            surface.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        
        surface.blit(self.image, (0,0), rect)
        screen.blit(surface, (left, top))

    def getImageSurface(self, left, top, imageNum):
        dim = self.dimList[imageNum]
        rect = pygame.Rect(dim)
        surface = pygame.Surface(rect.size).convert()

        if self.bkgd_color:
            surface.set_colorkey(self.bkgd_color, RLEACCEL)
        else:
            surface.set_colorkey(self.image.get_at((0,0)), RLEACCEL)
        
        surface.blit(self.image, (0,0), rect)
        
        return surface
