import pygame, sys, math, time
import AnalysisBoard
import config as c
from Position import Position, BLUNDER_THRESHOLD
import PygameButton
from colors import *
from PieceMasks import *
import HitboxTracker as HT
from TetrisUtility import loadImages, lighten
import EvalGraph, Evaluator
import AnalysisConstants as AC

MS_PER_FRAME = 25

class EvalBar:

    def __init__(self):
        self.currentPercent = 0
        self.targetPercent = 0
        self.currentColor = WHITE

    def tick(self, target, targetColor):
        self.targetPercent = target

        # "Approach" the targetPercent with a cool slow-down animation
        self.currentPercent += math.tanh((self.targetPercent - self.currentPercent))*0.2
        self.currentColor = [(current + (target-current)*0.2) for (current, target) in zip(self.currentColor, targetColor)]

    # percent 0-1, 1 is filled
    def drawEval(self):

        
        width = 100
        height = 1365
        surf = pygame.Surface([width, height])
        surf.fill(DARK_GREY)
        

        sheight = int((1-self.currentPercent) * height)
        pygame.draw.rect(surf, self.currentColor, [0,sheight, width, height - sheight])

        return surf
    
def analyze(positionDatabase, hzInt, hzString):
    global realscreen

    print("START ANALYSIS")


    IMAGE_NAMES = [BOARD, CURRENT, NEXT, PANEL]
    IMAGE_NAMES.extend( [LEFTARROW, RIGHTARROW, LEFTARROW2, RIGHTARROW2, STRIPES ])
    IMAGE_NAMES.extend( [LEFTARROW_MAX, RIGHTARROW_MAX, LEFTARROW2_MAX, RIGHTARROW2_MAX] )

    # Load all images.
    images = loadImages(c.fp("Images/Analysis/{}.png"), IMAGE_NAMES)

    bigMinoImages = []
    # Load mino images for all levels
    for i in range(0,10):
        bigMinoImages.append(loadImages(c.fp("Images/Analysis/Minos/" + str(i) + "/{}.png"), MINO_COLORS))
    
    AnalysisBoard.init(images, bigMinoImages)

    evalBar = EvalBar()

    B_LEFT = "LeftArrow"
    B_RIGHT = "RightArrow"
    B_MAXLEFT = "LeftArrowFast"
    B_MAXRIGHT = "RightArrowFast"
    B_HYP_LEFT = "LeftArrowHypothetical"
    B_HYP_RIGHT = "RightArrowHypothetical"
    B_HYP_MAXLEFT = "MaxLeftArrowHypothetical"
    B_HYP_MAXRIGHT = "MaxRightArrowHypothetical"

    
    buttons = PygameButton.ButtonHandler()
    # Position buttons
    y = 800
    buttons.addImage(B_MAXLEFT, images[LEFTARROW_MAX], 900, y, 0.3, margin = 5, alt = images[LEFTARROW2_MAX])
    buttons.addImage(B_LEFT, images[LEFTARROW], 1100, y, 0.3, margin = 5, alt = images[LEFTARROW2])
    buttons.addImage(B_RIGHT, images[RIGHTARROW], 1250, y, 0.3, margin = 5, alt = images[RIGHTARROW2])
    buttons.addImage(B_MAXRIGHT, images[RIGHTARROW_MAX], 1400, y, 0.3, margin = 5, alt = images[RIGHTARROW2_MAX])

    # Hypothetical positon navigation buttons
    x = 910
    y = 360
    buttons.addImage(B_HYP_MAXLEFT, images[LEFTARROW_MAX], x, y, 0.16, margin = 0, alt = images[LEFTARROW2_MAX])
    buttons.addImage(B_HYP_LEFT, images[LEFTARROW], x+100, y, 0.16, margin = 0, alt = images[LEFTARROW2])
    buttons.addImage(B_HYP_RIGHT, images[RIGHTARROW], x+180, y, 0.16, margin = 0, alt = images[RIGHTARROW2])
    buttons.addImage(B_HYP_MAXRIGHT, images[RIGHTARROW_MAX], x+260, y, 0.16, margin = 0, alt = images[RIGHTARROW2_MAX])

    buttons.addPlacementButtons(5, 1600, 100, 15, 800, 100)
    

    positionNum = 0
    analysisBoard = AnalysisBoard.AnalysisBoard(positionDatabase)

    # Setup graph
    evals = [position.evaluation for position in positionDatabase]

    print("Evals: ", evals)
    
    
    levels = [position.level for position in positionDatabase]
    #TESTLEVELS = [18]*500 + [19] * 500
    #testEvals = [max(0, min(1, np.random.normal(loc = 0.5, scale = 0.2))) for i in range(len(levels))]

    # CALCULATE BRILLANCIES/BLUNDERS/ETC HERE. For now, test code
    #testFeedback = [AC.NONE] * len(levels)
    #for i in range(30):
    #    testFeedback[random.randint(0,len(levels)-1)] = random.choice(list(AC.feedbackColors))

    feedback = [p.feedback for p in positionDatabase]

    # Index of very position that is an inaccuracy, mistake, or blunder
    keyPositions = []
    for i in range(len(feedback)):
        if feedback[i] in [AC.INACCURACY, AC.MISTAKE, AC.BLUNDER]:
            keyPositions.append(i)
    keyPositions = np.array(keyPositions)
    print("Key positions:", keyPositions)

    # Calculate game summary. Get average loss for pre, post, killscreen.
    preNum, preSum = 0, 0
    postNum, postSum = 0, 0
    ksNum, ksSum = 0, 0
    pre = positionDatabase[0].level
    for p in positionDatabase:

        # Disregard unknown/invalid evaluations
        if p.feedback == AC.INVALID:
            continue

        e = max(BLUNDER_THRESHOLD, p.playerFinal - p.bestFinal) # limit difference to -50

        if p.level >= 29:
            ksNum += 1
            ksSum += e
        elif p.level >= 19 or p.level > pre:
            postNum += 1
            postSum += e
        else: # p.level == pre
            preNum += 1
            preSum += e

    print("Summary: ",preNum,preSum,postNum,postSum,ksNum,ksSum)

    def getAccuracy(num, summ):
        if num == 0:
            return "N/A"
        print(num,summ)
        avg = summ / num # probably some negative number. BLUNDER_THRESHHOLD = -50 at the moment
        # scale BLUNDER_THRESHOLD to 0 -> 0% -> 100%

         # can't get worse than 0% accuracy. Can go over 100% though... (rather rapid)
        scaled = round(100 * max(avg - BLUNDER_THRESHOLD, 0) / (0-BLUNDER_THRESHOLD))
        print(scaled)

        # scaled is now a number 0-100(+)
        return "{}%".format(scaled)

    def blitCenterText(surface, font, string, color, y):
        text = font.render(string, True, color)
        surface.blit(text, [surface.get_width()/2 - text.get_width()/2, y])

    # Generate game summary surface
    summary = pygame.Surface([300,400]).convert_alpha()
    blitCenterText(summary, c.fontbold, "Accuracy", BLACK, 0)
    blitCenterText(summary, c.fontbigbold, getAccuracy(preNum+postNum, preSum+postSum), BLACK, 50)
    blitCenterText(summary, c.fontbold, "Pre - " + getAccuracy(preNum, preSum), BLACK, 150)
    blitCenterText(summary, c.fontbold, "Post - " + getAccuracy(postNum, postSum), BLACK, 200)
    blitCenterText(summary, c.fontbold, "KS - " + getAccuracy(ksNum, ksSum), BLACK, 250)
    
    
        
    smallSize = 70
    bigResolution = 4
    width = 1300

    # Graph only accepts a minimum of 4 positions, otherwise interpolation doesn't work
    showGraphs = (len(levels) >= 4)
    if showGraphs:
        smallGraph = EvalGraph.Graph(True, evals, levels, feedback, 950, 970, width, 200, 1, smallSize, bigRes = bigResolution)
        bigWidth = width if len(levels) >= 200 else (width // 2) # Cut the big graph in half if there are under 200 positions
        showBig = len(levels) >= 50 # If there are under 50 positions, don't show the big graph at all
        if showBig:
            bigGraph = EvalGraph.Graph(False, evals, levels, feedback, 950, 1220, bigWidth, 200, bigResolution, smallSize)
    greysurface = pygame.Surface([width, 200])
    greysurface.blit(images[STRIPES],[0,0])
    


    updatePosIndex = None

    key = None
    
    startPressed = False
    click = False


    while True:

        startTime = time.time()

        # --- [ CALCULATIONS ] ---

        # Mouse position
        mx,my = c.getScaledPos(*pygame.mouse.get_pos())
        pressed = pygame.mouse.get_pressed()[0]



        # Update with mouse event information        
        buttons.updatePressed(mx, my, click)
        analysisBoard.update(mx, my, click, key == pygame.K_SPACE)
        
        c.realscreen.fill(MID_GREY)
        c.screen.fill(MID_GREY)

        # Hypothetical buttons
        if (buttons.get(B_HYP_LEFT).clicked or key == pygame.K_z) and analysisBoard.hasHypoLeft():
            analysisBoard.hypoLeft()
        elif (buttons.get(B_HYP_RIGHT).clicked or key == pygame.K_x) and analysisBoard.hasHypoRight():
            analysisBoard.hypoRight()
        elif buttons.get(B_HYP_MAXLEFT).clicked:
            while analysisBoard.hasHypoLeft():
                analysisBoard.hypoLeft()
        elif buttons.get(B_HYP_MAXRIGHT).clicked:
            while analysisBoard.hasHypoRight():
                analysisBoard.hypoRight()

        # Left/Right Buttons
        if (buttons.get(B_LEFT).clicked or key == pygame.K_LEFT) and analysisBoard.positionNum > 0:
            analysisBoard.updatePosition(analysisBoard.positionNum-1)
            positionNum -= 1
            
        elif (buttons.get(B_RIGHT).clicked or key == pygame.K_RIGHT) and analysisBoard.positionNum < len(positionDatabase) - 1:
            analysisBoard.updatePosition(analysisBoard.positionNum+1)
            positionNum += 1

        elif (buttons.get(B_MAXLEFT).clicked or key == pygame.K_COMMA) and len(keyPositions[keyPositions < positionNum]) > 0:
            # Go to previous key position
            positionNum = keyPositions[keyPositions < positionNum].max()
            analysisBoard.updatePosition(positionNum)

        elif (buttons.get(B_MAXRIGHT).clicked or key == pygame.K_PERIOD) and len(keyPositions[keyPositions > positionNum]) > 0:
            # Go to next key position
            positionNum = keyPositions[keyPositions > positionNum].min()
            analysisBoard.updatePosition(positionNum)


        # Update Graphs
        if showGraphs:
            o = smallGraph.update(positionNum, mx,my, pressed, startPressed, click)
            if o != None:
                positionNum = o
                analysisBoard.updatePosition(positionNum)
            if showBig:
                o = bigGraph.update(positionNum, mx, my, pressed, startPressed, click)
                if o != None:
                    positionNum = o
                    analysisBoard.updatePosition(positionNum)
        
        
            
        buttons.get(B_LEFT).isAlt = analysisBoard.positionNum == 0
        buttons.get(B_RIGHT).isAlt = analysisBoard.positionNum == len(positionDatabase) - 1
        buttons.get(B_MAXLEFT).isAlt = len(keyPositions[keyPositions < positionNum]) == 0
        buttons.get(B_MAXRIGHT).isAlt = len(keyPositions[keyPositions > positionNum]) == 0

        buttons.get(B_HYP_LEFT).isAlt = not analysisBoard.hasHypoLeft()
        buttons.get(B_HYP_MAXLEFT).isAlt = not analysisBoard.hasHypoLeft()
        buttons.get(B_HYP_RIGHT).isAlt = not analysisBoard.hasHypoRight()
        buttons.get(B_HYP_MAXRIGHT).isAlt = not analysisBoard.hasHypoRight()


        # For purposes of displaying eval, use the previous position if current position has not placed piece yet
        pos = analysisBoard.position
        if type(pos.placement) != np.ndarray and pos.prev != None:
            #print("back one")
            pos = pos.prev

        if not pos.evaluated and type(pos.placement) == np.ndarray:
            print("ask API new position")
            Evaluator.evaluate(pos, hzString)

        # Update possible moves
        bs = buttons.placementButtons
        for i in range(len(bs)):
            if i > len(pos.possible) - 1:
                bs[i].show = False
            else:
                bs[i].show = True
                pm = pos.possible[i]
                bs[i].update(str(pm.evaluation), pm.move1Str, pm.move2Str, (pos.placement == pm.move1).all())

        # Check mouse hovering over possible moves
        hoveredPlacement = None # stores the PossibleMove object the mouse is hovering on
        for pb in bs:
            if pb.pressed and pb.show:
                hoveredPlacement = pos.possible[pb.i]
                break

        # If a possible placement is clicked, make that move
        if hoveredPlacement != None and click:
            analysisBoard.placeSelectedPiece(hoveredPlacement.move1)
        

        # --- [ DISPLAY ] ---

        # Now that we're about to display things, reset hitbox data so that new graphics components can be appended
        #HT.log()
        #print(HT.at(mx,my),mx,my)
        HT.reset()

        # Buttons
        buttons.display(c.screen)
        
        # Tetris board
        analysisBoard.draw(hoveredPlacement)

        # Evaluation Graph
        c.screen.blit(greysurface, [950, 970])
        c.screen.blit(greysurface, [950, 1220])
        if showGraphs:
            smallGraph.display(mx,my, positionNum)
            if showBig:
                bigGraph.display(mx, my, positionNum)
        

        # Eval bar
        feedbackColor = AC.feedbackColors[pos.feedback]
        evalBar.tick(pos.evaluation, feedbackColor)
        HT.blit("eval", evalBar.drawEval(), [20,20])

        # Text for level / lines / score
        x1 = 1270
        x = 900
        c.screen.blit(c.font.render("Level: {}".format(pos.level), True, BLACK), [x1, 20])
        c.screen.blit(c.font.render("Lines: {}".format(pos.lines), True, BLACK), [x1, 100])
        c.screen.blit(c.font.render("Score: {}".format(pos.score), True, BLACK), [x1, 180])
        c.screen.blit(c.font.render("playerNNB: {}".format(pos.playerNNB), True, BLACK), [x, 460])
        c.screen.blit(c.font.render("bestNNB: {}".format(pos.bestNNB), True, BLACK), [x, 520])
        c.screen.blit(c.font.render("playerFinal: {}".format(pos.playerFinal), True, BLACK), [x, 580])
        c.screen.blit(c.font.render("bestFinal: {}".format(pos.bestFinal), True, BLACK), [x, 620])
        c.screen.blit(c.font.render("RatherRapid: {}".format(pos.ratherRapid), True, BLACK), [x, 680])
        
        x3 = 2000
        c.screen.blit(c.font.render("{} Hz Analysis".format(hzInt), True, BLACK), [1600, 860])
        if pos.feedback == AC.NONE:
            feedbackColor = DARK_GREY
        else:
            feedbackColor = lighten(feedbackColor,0.7)
        c.screen.blit(c.fontbold.render(AC.feedbackString[pos.feedback], True, feedbackColor), [x3, 760])
        c.screen.blit(c.fontbold.render(AC.adjustmentString[pos.adjustment], True, feedbackColor), [x3, 860])
        c.screen.blit(c.font.render("e: {}".format(pos.e), True, BLACK), [1300, 300])

        # Text for position number
        text = c.font.render("Position: {}".format(analysisBoard.positionNum + 1), True, BLACK)
        c.screen.blit(text, [1650,760])

        # Draw timestamp
        frameNum = analysisBoard.positionDatabase[analysisBoard.positionNum].frame
        if frameNum != None:
            text = c.font.render(c.timestamp(frameNum), True, BLACK)
            c.screen.blit(text, [1340,730] )

        # Game summary
        c.screen.blit(summary, [1240, 400])

        key = None
        startPressed = False
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.display.quit()
                sys.exit()
                return True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                startPressed = True

            elif event.type == pygame.MOUSEBUTTONUP:
                click = True

            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_t:
                    analysisBoard.toggle()

                key = event.key    
                
            elif event.type == pygame.VIDEORESIZE:

                c.realscreen = pygame.display.set_mode(event.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
            
        c.handleWindowResize()
        pygame.display.update()

        dt = (time.time() - startTime)*1000
        pygame.time.wait(int(max(0, MS_PER_FRAME - dt)))
