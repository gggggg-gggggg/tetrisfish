import pygame
from TetrisUtility import *
from PieceMasks import *
import config as c
from colors import *

MINO_OFFSET = 32 # Pixel offset between each mino

EMPTY = 0
WHITE_MINO = 1
WHITE_MINO_2 = 4
RED_MINO = 2
BLUE_MINO = 3
BOARD = "board"
NEXT = "next"
LEFTARROW = "leftarrow"
RIGHTARROW = "rightarrow"
PANEL = "panel"
IMAGE_NAMES = [WHITE_MINO, WHITE_MINO_2, RED_MINO, BLUE_MINO, BOARD, NEXT, PANEL, LEFTARROW, RIGHTARROW]

# Return surface with tetris board. 0 = empty, 1/-1 =  white, 2/-2 = red, 3/-3 = blue, negative = transparent
def drawGeneralBoard(images, board, image, B_SCALE, hscale, LEFT_MARGIN, TOP_MARGIN, hover = None):

    b_width = image.get_width() * B_SCALE
    b_height = image.get_height() * B_SCALE*hscale
    b = pygame.transform.scale(image, [b_width , b_height])

    surf = pygame.Surface([b_width,b_height])
    
    surf.blit(b, [0,0])

    y = TOP_MARGIN
    r = 0
    for row in board:
        x = LEFT_MARGIN
        y += MINO_OFFSET
        c = 0
        for mino in row:
            if mino != EMPTY:
                surf.blit(images[mino], [x,y])
            if (type(hover) != np.ndarray and mino != EMPTY and hover == True) or (type(hover) == np.ndarray and hover[r][c] == 1):
                s = pygame.Surface([MINO_OFFSET-4,MINO_OFFSET-4])
                if mino != EMPTY:    
                    s.fill(BLACK)
                else:
                    s.fill([100,100,100])
                s.set_alpha(90)
                surf.blit(s, [x, y])
                
            x += MINO_OFFSET
            c += 1
        r += 1
            
    return surf

def colorMinos(minos, piece, white2 = False):

    num = 1

    if piece == L_PIECE or piece == Z_PIECE:
        # Red tetronimo
        num = RED_MINO
    
    elif piece == J_PIECE or piece == S_PIECE:
        #Blue tetronimo
        num = BLUE_MINO

    elif white2:
        num = WHITE_MINO_2

    return [[i*num for i in row] for row in minos]

def colorOfPiece(piece):

    if piece == L_PIECE or piece == Z_PIECE:
        return RED_MINO
    
    elif piece == J_PIECE or piece == S_PIECE:
        return BLUE_MINO
    else:
        return WHITE_MINO
    


# Get the sum of the number of leading zeros in each column
def getHoles(array):
    countA = 0
    for col in range(c.NUM_HORIZONTAL_CELLS):
        for row in range(c.NUM_VERTICAL_CELLS):
            if array[row][col] == 1:
                break
            countA += 1

    countB = 0
    for col in range(c.NUM_HORIZONTAL_CELLS-1,-1,-1):
        for row in range(c.NUM_VERTICAL_CELLS-1,-1,-1):
            if array[row][col] == 0:
                break
            countB += 1
    
    return countA + countB


class AnalysisBoard:

    def __init__(self, position):

        self.x = 80
        self.y = 6
        self.xoffset = 22
        self.yoffset = -6

        self.nextx = 445
        self.nexty = 14
        
        self.updatePosition(position)
        

    def updatePosition(self, position):
        self.position = position
        self.hoverNum = 0
        self.isHoverPiece = False
        self.isAdjustCurrent = False
        self.placements = []
        self.hover = empty()
        self.ph = [-1,-1]
        self.nextHover = False
        self.showNextPanel = False

        xoffset = 0 if (position.nextPiece == O_PIECE or position.nextPiece == I_PIECE) else (0 - MINO_OFFSET/2)
        yoffset = MINO_OFFSET/2 if position.nextPiece == I_PIECE else 0
        self.xNextOffset = 32 + xoffset
        self.yNextOffset = -7 + yoffset
        self.panelPercent = 0

        self.NEXT_SCALE = 0.85

    # Toggle hover piece
    def toggle(self):
        if len(self.placements) > 0:
            self.hoverNum  += 1
            self.hover = self.placements[self.hoverNum % len(self.placements)]

    # Update next box
    def updateNext(self, mx, my, click):
        x1 = 450
        y1 = 20

        x = mx - x1 - self.xNextOffset
        y = my - y1 - self.yNextOffset
        length = 120
        
        col = int( x / length * 4)
        row = int( y / length * 4)
        if (row < 0 or row > 3 or col < 0 or col > 3):
            row = 0
            col = 0

        # Set boolean value for whether mouse is hovering over next piece
        self.nextHover = TETRONIMO_SHAPES[self.position.nextPiece][0][row][col] == 1

        # display next box choices if clicked
        if self.nextHover and click:
            self.showNextPanel = not self.showNextPanel

        if self.showNextPanel:
            self.panelPercent += (1 - self.panelPercent) * 0.15
        else:
            self.panelPercent -= self.panelPercent * 0.15

        print(self.panelPercent)
        

    # Update mouse-related events - namely, hover
    def update(self, mx, my, click):

        self.updateNext(mx, my, click)
    
        x1 = 100
        y1 = 28
        width = 320
        height = 642

        # Calculate row and col where mouse is hovering. Truncate to nearest cell
        if mx >= x1 and mx < x1 + width and my >= y1 and my <= y1 + height:
            c1 = clamp(int( (mx - x1) / width * c.NUM_HORIZONTAL_CELLS ), 0, c.NUM_HORIZONTAL_CELLS)
            r = clamp(int ( (my - y1) / height * c.NUM_VERTICAL_CELLS), 0, c.NUM_VERTICAL_CELLS)
        else:
            r = -1
            c1 = -1

        newAdjust = False
            

        # If current piece clicked, enter placement selection mode
        if click and self.touchingCurrent(r,c1) and not self.isAdjustCurrent:
            self.isAdjustCurrent = True
            newAdjust = True
        elif click and (len(self.placements) == 0 and r != -1 or (self.hover == self.position.placement).all()):
            # Reset placement selection if clicking empty square that is not piece-placeable
            self.isAdjustCurrent = False
            self.isHoverPiece = False
            newAdjust = True

        
        # If mouse is now hovering on a different tile
        if [r,c1] != self.ph or newAdjust:

            self.ph = [r,c1]
            print(self.ph)


            # Many piece placements are possible from hovering at a tile. We sort this list by relevance,
            # and hoverNum is the index of that list. When we change tile, we reset and go to best (first) placement
            if self.position.currentPiece != I_PIECE:
                self.hoverNum = 0
            self.placements = self.getHoverMask(r,c1)

            
            if not self.isAdjustCurrent or len(self.placements) == 0:
                
                # If piece selection inactive or no possible piece selections, hover over mouse selection
                self.isHoverPiece = False
                if r != -1 and rang(r,c1):
                    # In a special case that mouse is touching current piece, make current piece transparent (if clicked, activate piece selection)
                    if self.touchingCurrent(r,c1):
                        self.hover = self.position.placement
                    else:
                        self.hover = empty()
                        self.hover[r][c1] = 1
                        
                else:
                     self.hover = empty()
            else:
                # If there are hypothetical piece placements, display them
                self.isHoverPiece = True
                self.hover = self.placements[self.hoverNum % len(self.placements)]


    def touchingCurrent(self,r,c1):
        if not rang(r,c1):
            return False
        return self.position.placement[r][c1] == 1


    # From hoverR and hoverC, return a piece placement mask if applicable
    def getHoverMask(self, r, c1):
        b = self.position.board
        if r == -1 or b[r][c1] == 1:
            return []
        
        piece = self.position.currentPiece
        placements = []
        # We first generate a list of legal piece placements from the tile. Best first.

        if piece == O_PIECE:
            # Bottom-left then top-left tile
            if c1 == 9:
                return []

            print2d(b)
            for i in [c1,c1-1]:
                
                if (rang(r+1,i) and b[r+1][i] == 1) or ((rang(r+1,i+1) and b[r+1][i+1]) == 1) or r == 19:
                    placements.append(stamp(O_PIECE, r-2, i-1))
                    
                elif (rang(r+2,i) and b[r+2][i] == 1) or ((rang(r+2,i+1) and b[r+2][i+1]) == 1) or r == 18:
                    placements.append(stamp(O_PIECE, r-1, i-1))
            
        elif piece == I_PIECE:
            # Vertical placement, then mid-left horizontal
            for i in range(0,4):
                if (rang(r+i+1,c1) and b[r+i+1][c1] == 1) or r+i == 19:
                    placements.append(stamp(I_PIECE,r+i-3,c1-2,1))
                    break

            for i in [1,2,0,3]:
                cs = c1 - i # cs is start col of longbar
                if cs >=7 or cs < 0:
                    continue
                valid = False
                for cp in range(cs,cs+4):
                    if rang(r+1,cp) and b[r+1][cp] == 1 or r == 19:
                        valid = True
                if valid:
                    p = stamp(I_PIECE,r-1,cs,0)
                    if not intersection(p,b):
                        placements.append(p)
                        break
            
                
        else:
            # All orientations at both centers

            for i in range(-2,1):
                for rot in range(len(TETRONIMO_SHAPES[piece])):
                    p = stamp(piece,r+i+1,c1-2,rot)
                    if type(p) != np.ndarray:
                        continue
                    if intersection(p, b):
                        placements.append(stamp(piece,r+i,c1-2,rot))

        

        # Remove all placements that collide with board
        placements = [p for p in placements if not intersection(p, b)]

        # Sort based on least holes
        if piece != I_PIECE and piece != O_PIECE:
            placements.sort(reverse = True, key = lambda p: (getHoles(p+b)))

        return placements

    # Return surface with nextbox
    def getNextBox(self, images):

        nextPiece = self.position.nextPiece

        minos = colorMinos(TETRONIMO_SHAPES[nextPiece][0][1:], nextPiece)

        # Shift half-mino to the left for 3-wide pieces to fit into nextbox
        xoffset = 0 if (nextPiece == O_PIECE or nextPiece == I_PIECE) else (0 - MINO_OFFSET/2)
        yoffset = MINO_OFFSET/2 if nextPiece == I_PIECE else 0
        return drawGeneralBoard(images, minos, images[NEXT], self.NEXT_SCALE, 1, self.xNextOffset, self.yNextOffset, hover = self.nextHover)

    def drawNextPanel(self, screen, images):
        print("draw")

        panel = pygame.transform.scale(images[PANEL], [images[PANEL].get_width() * self.NEXT_SCALE, images[PANEL].get_height() * self.NEXT_SCALE])
        surf = pygame.Surface([panel.get_width(), int(panel.get_height() * self.panelPercent)])
        surf.blit(panel,[0,0])
        
        screen.blit(surf, [self.nextx,self.nexty + images[NEXT].get_height()*self.NEXT_SCALE - 5])
        
    
    # Draw tetris board to screen
    def draw(self, screen, images):

        curr = self.position.currentPiece

        # We add current piece to the board
        plainBoard = self.position.board.copy()
        placement = colorMinos(self.position.placement, curr, white2 = True)

        # If active selection mode, then display that. Otherwise, display original placed piece location
        board = self.position.board.copy()
        if self.isAdjustCurrent:
            if self.isHoverPiece:
                board += colorMinos(self.hover, curr, white2 = True)
        else:
            board += placement
        
        surf = drawGeneralBoard(images, board, images[BOARD], 0.647, 0.995, self.xoffset, self.yoffset, hover = self.hover)
        screen.blit(surf ,[self.x,self.y])

        if self.showNextPanel or self.panelPercent > 0.01:
            self.drawNextPanel(screen, images)

        # Next box
        screen.blit(self.getNextBox(images), [self.nextx, self.nexty])
