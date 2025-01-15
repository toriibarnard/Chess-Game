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
    # load chess piece images and store them in the IMAGES dictionary
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # note: we can access an image by using 'IMAGES["wP"]'

'''
This is the main driver, this handles user input and updating graphics
'''
def main():
    # main function for the chess game
    # this function initializes the game, sets up the GUI, and enters the game loop to handle user input and update
    # the display
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    # Show the start screen
    if not start_screen(screen):
        return  # Exit if the player quits from the start screen

    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made
    animate = False # flag variable for when a move should be animated
    print(gs.board)
    loadImages() # only do this once, and before the loop
    running = True
    squareSelected = () # no square selected initially, keep track of the last click of the user (tuple: (row,col)
    playerClicks = [] # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False
    while running: # game loop
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x,y) position of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if squareSelected == (row, col): # user clicked the same square twice
                    squareSelected = () # deselect
                    playerClicks = [] # clear player clicks
                else:
                    squareSelected = (row,col)
                    playerClicks.append(squareSelected) # append for both first and second clicks
                # was that the users second click?
                if len(playerClicks) == 2: # after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            animate = True
                            squareSelected = () # reset user clicks
                            playerClicks = [] # clear playerClicks
                    if not moveMade:
                        playerClicks = [squareSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: # reset board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves() # update valid moves list after a move is made
            moveMade = False # reset moveMade flag
            animate = False

        drawGameState(screen, gs, validMoves, squareSelected) # draw current state of the game on the screen

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black Wins!')
            else:
                drawText(screen, 'White Wins!')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'StaleMate')

        clock.tick(MAX_FPS) # limit framerate to max fps
        p.display.flip() # update display
'''
Responsible for declaring the start screen
'''
def start_screen(screen):
    """Displays the start screen."""
    running = True
    font_title = p.font.Font(None, 100)  # title font
    font_subtitle = p.font.Font(None, 50)  # subtitle font
    font_start = p.font.Font(None, 50)  # start font

    title_text = font_title.render("Chess", True, p.Color("gold"))
    subtitle_text = font_subtitle.render("by Torii Barnard", True, p.Color("gold"))
    start_text = font_start.render("Press Enter to Start", True, p.Color("white"))
    clock = p.time.Clock()

    # Load and scale the background image
    background = p.image.load("images/startScreen.png")
    background = p.transform.scale(background, (WIDTH, HEIGHT))

    alpha = 0  # For fade-in effect
    fade_in = True

    while running:
        screen.blit(background, (0, 0))  # display the background image

        # display the title and subtitle
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 4 + 100))

        # blinking text effect
        if fade_in:
            alpha += 5
            if alpha >= 255:
                fade_in = False
        else:
            alpha -= 5
            if alpha <= 0:
                fade_in = True
        start_surface = font_start.render("Press Enter to Start", True, p.Color("gold"))
        start_surface.set_alpha(alpha)
        screen.blit(start_surface, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 20))

        p.display.flip()

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                return False  # exit game
            if event.type == p.KEYDOWN and event.key == p.K_RETURN:
                return True  # start game

        clock.tick(30)  # Limit the frame rate

'''
Responsible for all graphics within current gameState
'''
def drawGameState(screen, gs, validMoves, squareSelected):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected) # add square highlight feature
    drawPieces(screen, gs.board) # draw pieces onto squares

'''
Draw the squares on the board, top left square is always white
'''
def drawBoard(screen):
    colors = [p.Color("wheat"), p.Color("darkgoldenrod")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] # alternate colours for each square
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE)) # draw square

'''
Draw pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    # iterate through the board
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Highlight the Square selected and the moves for the piece selected
'''
def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # squareSelected is a piece that can be moved
            # highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(125) # transperancy value (0-255)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight the valid moves from that square
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Move animation
'''
def animateMove(move, screen, board, clock):
    colors = [p.Color("wheat"), p.Color("darkgoldenrod")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames_per_square = 7  # frames to move one square aka the speed at which the piece moves
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.startRow + dR * frame / frame_count, move.startCol + dC * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enpassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

'''
Draw text animation
'''
def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 50, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('DarkGray'))
    screen.blit(textObject, textLocation.move(2, 2))

# run the game
main()
    
