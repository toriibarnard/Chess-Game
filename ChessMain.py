# This project is inspired by Eddie Sharick
# This is the main driver file. It is responsible for handling user input and displaying the current GameState object

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8 #dimensions 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images
'''
def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #Note: we can access an image by using 'IMAGES["wP"]'

'''
This is the main driver, this handles user input and updating graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    print(gs.board)
    loadImages() #only do this once, and before the loop
    running = True
    sqSelected = () #no square selected initially, keep track of the last click of the user (tuple: (row,col)
    playerClicks = [] #keep track of player clicks (two tuples: [(6,4), (4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) position of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col): #user clicked the same square twice
                    sqSelected = () #deselect
                    playerClicks = [] #clear player clicks
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected) #append for both first and second clicks
                #was that the users second click?
                if len(playerClicks) == 2: #after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = () #reset user clicks
                        playerClicks = [] #clear playerclicks
                    else:
                        playerClicks = [sqSelected]
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Responsible for all graphics within current gamestate
'''
def drawGameState(screen, gs):
    drawBoard(screen) #draw squares on the board
    drawPieces(screen, gs) #draw pieces onto squares

'''
Draw the squares on the board, top left square is always white
'''
def drawBoard(screen):
    colors = [p.Color("wheat"), p.Color("darkgoldenrod")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board.getPiece(r, c)
            if piece != "--": #Not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


main()
    
