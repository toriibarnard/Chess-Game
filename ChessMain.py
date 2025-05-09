# This is the main driver file. It is responsible for handling user input and displaying the current GameState object

import pygame as p
import ChessEngine
import ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8  # dimensions 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}

# Game modes
PLAYER_VS_PLAYER = "player_vs_player"
PLAYER_VS_AI = "player_vs_ai"

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
    game_mode = start_screen(screen)
    if not game_mode:
        return  # Exit if the player quits from the start screen

    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when a move should be animated
    print(gs.board)
    loadImages()  # only do this once, and before the loop
    running = True
    squareSelected = ()  # no square selected initially, keep track of the last click of the user (tuple: (row,col)
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False

    # Set up AI if in Player vs AI mode
    playerOne = True  # True if human plays white, False if AI plays white
    playerTwo = True  # True if human plays black, False if AI plays black

    if game_mode == PLAYER_VS_AI:
        playerTwo = False  # AI plays as black
        ai = ChessAI.ChessAI(depth=3)  # Initialize AI with depth 3

    while running:  # game loop
        # Check if it's AI's turn
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) position of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if squareSelected == (row, col):  # user clicked the same square twice
                        squareSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)  # append for both first and second clicks
                    # was that the users second click?
                    if len(playerClicks) == 2:  # after second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = ()  # reset user clicks
                                playerClicks = []  # clear playerClicks
                        if not moveMade:
                            playerClicks = [squareSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    # If in Player vs AI mode and undoing, undo twice to get back to human's turn
                    if game_mode == PLAYER_VS_AI and len(gs.moveLog) > 0:
                        gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:  # reset board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                if e.key == p.K_m:  # Return to main menu with 'm' key
                    return main()  # Restart the game

        # AI Move Finder
        if not gameOver and not humanTurn and game_mode == PLAYER_VS_AI:
            # Display thinking text
            drawGameState(screen, gs, validMoves, squareSelected)
            thinking_text = "AI thinking..."
            draw_thinking_text(screen, thinking_text)
            p.display.flip()

            # Get AI move
            ai_move = ai.find_best_move(gs, validMoves)
            if ai_move is None:
                ai_move = validMoves[0]  # Fallback to first available move

            gs.makeMove(ai_move)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()  # update valid moves list after a move is made
            moveMade = False  # reset moveMade flag
            animate = False

        drawGameState(screen, gs, validMoves, squareSelected)  # draw current state of the game on the screen

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black Wins!')
            else:
                drawText(screen, 'White Wins!')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'StaleMate')

        if gameOver:
            draw_return_text(screen, "Press 'M' to return to main menu")

        clock.tick(MAX_FPS)  # limit framerate to max fps
        p.display.flip()  # update display


'''
Display thinking text for AI
'''


def draw_thinking_text(screen, text):
    font = p.font.SysFont("Arial", 20, True, False)
    text_object = font.render(text, True, p.Color('Red'))
    text_location = p.Rect(0, 0, WIDTH, 20).move(10, 10)
    screen.blit(text_object, text_location)


'''
Display return to menu text
'''


def draw_return_text(screen, text):
    font = p.font.SysFont("Arial", 20, True, False)
    text_object = font.render(text, True, p.Color('Blue'))
    text_location = p.Rect(0, 0, WIDTH, 20).move(WIDTH // 2 - text_object.get_width() // 2, HEIGHT - 30)
    screen.blit(text_object, text_location)


'''
Responsible for declaring the start screen
'''


def start_screen(screen):
    """Displays the start screen and returns the selected game mode."""
    running = True
    font_title = p.font.Font(None, 100)  # title font
    font_subtitle = p.font.Font(None, 50)  # subtitle font
    font_start = p.font.Font(None, 40)  # start font
    font_options = p.font.Font(None, 36)  # options font

    title_text = font_title.render("Chess", True, p.Color("white"))
    subtitle_text = font_subtitle.render("by Torii Barnard", True, p.Color("white"))
    option1_text = font_options.render("1: Player vs Player", True, p.Color("yellow"))
    option2_text = font_options.render("2: Player vs AI", True, p.Color("yellow"))
    clock = p.time.Clock()

    selected_option = None

    # Load and scale the background image
    background = p.image.load("images/startScreen.png")
    background = p.transform.scale(background, (WIDTH, HEIGHT))

    # Create a semi-transparent overlay for the background
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)  # Adjust the transparency level (0 = fully transparent, 255 = fully opaque)
    overlay.fill(p.Color('black'))

    alpha = 0  # for fade-in effect
    fade_in = True

    while running:
        screen.blit(background, (0, 0))  # display the background image
        screen.blit(overlay, (0, 0))  # display the overlay for better contrast

        # display the title and subtitle
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 - 50))
        screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 4 + 20))

        # display the options
        screen.blit(option1_text, (WIDTH // 2 - option1_text.get_width() // 2, HEIGHT // 2))
        screen.blit(option2_text, (WIDTH // 2 - option2_text.get_width() // 2, HEIGHT // 2 + 50))

        # blinking text effect
        if fade_in:
            alpha += 5
            if alpha >= 255:
                fade_in = False
        else:
            alpha -= 5
            if alpha <= 0:
                fade_in = True
        instruction_text = font_start.render("Press 1 or 2 to select", True, p.Color("green"))
        instruction_text.set_alpha(alpha)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 120))

        p.display.flip()

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
                return None  # exit game
            if event.type == p.KEYDOWN:
                if event.key == p.K_1:
                    return PLAYER_VS_PLAYER
                elif event.key == p.K_2:
                    return PLAYER_VS_AI

        clock.tick(30)  # limit the frame rate


'''
Responsible for all graphics within current gameState
'''


def drawGameState(screen, gs, validMoves, squareSelected):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected)  # add square highlight feature
    drawPieces(screen, gs.board)  # draw pieces onto squares


'''
Draw the squares on the board, top left square is always white
'''


def drawBoard(screen):
    colors = [p.Color("wheat"), p.Color("darkgoldenrod")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]  # alternate colours for each square
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # draw square


'''
Draw pieces on the board using the current GameState.board
'''


def drawPieces(screen, board):
    # iterate through the board
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Highlight the Square selected and the moves for the piece selected
'''


def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # squareSelected is a piece that can be moved
            # highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(125)  # transperancy value (0-255)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight the valid moves from that square
            s.fill(p.Color('green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


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
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('DarkGray'))
    screen.blit(textObject, textLocation.move(2, 2))


# run the game
if __name__ == "__main__":
    main()
