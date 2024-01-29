# This class is responible for storing all the information about the current state of the chess game.
# It is also resposible for determining the valid moves at the current state. It will also keep a move log.

class GameState():
    def __init__(self):
        # board is 8x8 2d list, each element of the list has 2 characters.
        # the first character represents the colour of the piece
        # the second character represents the type of piece
        # "--" represents and empty space
        self.board =[
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        # dictionary to map a piece to its functions
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}


        self.whiteToMove = True
        self.moveLog = [] # list to store the moves made during the game
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates where an en passant capture is possible
    
    # method to execute a move, doesn't work for enpassant, castling, or pawn promotion
    def makeMove(self, move):
        # update the with the piece moved and the destination square
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log move for a potential undo later
        self.whiteToMove = not self.whiteToMove # swap players
        # update kings location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn

        #update the enpassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # only if pawn moved 2 squares
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.endCol) # startCol or endCol works
        else:
            self.enpassantPossible = ()
    
    # method to undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure there is a move to undo
            move = self.moveLog.pop()
            # restore the original position of moved and captured pieces
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # switch turns back
            self.whiteToMove = not self.whiteToMove
            # update kings position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
    
    # method to generate all moves considering checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible #preserve original value of enpassantPossible before modification
        # 1) generate all posible moves
        moves = self.getAllPossibleMoves()
        # 2) for each move, make the move
        for i in range(len(moves)-1, -1, -1): # when removing from a list, go backwards
            self.makeMove(moves[i])
            # 3) generate all oponents moves
            # 4) for each of your opponents moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove # making a move always switches the turn, so we have to switch it back before calling inCheck
            if self.inCheck():
                moves.remove(moves[i])
        # 5) if they do attack your king, its not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        return moves
    
    # method to determine if the current player is in check
    def inCheck(self):
        # check if it is white's turn and the square of the white king is under attack
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else: # blacks turn
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
        
    # method determine if the enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves() # generate all opponent moves
        self.whiteToMove = not self.whiteToMove # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False
        

    # method to get all moves not considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # iterate through rows
            for c in range(len(self.board[r])): # iterate through columns in the given row
                turn = self.board[r][c][0]
                # check if the piece belongs to the current player
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based on piece type
        return moves
                
    # method to get all pawn moves for the pawn located at row, col and add them to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # white pawn moves
            if self.board[r-1][c] == '--': # 1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2 square advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: # captures to the left
                if self.board[r-1][c-1][0] == 'b': # there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible: # enpassant capture
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: # captures to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible: # enpassnt capture
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else: #black pawn moves
            if self.board[r+1][c] == '--': # 1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2 square advance
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0: # captures to the left
                if self.board[r+1][c-1][0] == 'w': # there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible: # enpassant capture
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7: # captures to the right
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible: # enpassant capture
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
        # add pawn promotions later

    # method to get all rook moves for the rook located at row, col and add them to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1,0), (0, 1)) # define directions: up down left right
        enemyColor = 'b' if self.whiteToMove else 'w' # determine enemy colour based off current players turn
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # check if potential move is on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space; valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece; valid capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # friendly piece; invalid
                        break
                else: # off board; break
                    break

    # method to get all Knight moves for the Knight located at row, col and add them to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),(1, -2), (1, 2), (2, -1), (2, 1)) # define directions
        allyColor = 'w' if self.whiteToMove else 'b' # determine ally colour based off current players turn
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    # method to get all Bishop moves for the Bishop located at row, col and add them to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1,-1), (1, 1)) # define directions: 4 diagonals
        enemyColor = 'b' if self.whiteToMove else 'w' # determine enemy colour based off current players turn
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # check if potential move is on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space; valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece; valid capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # friendly piece; invalid
                        break
                else: # off board; break
                    break
    # method to get all Queen moves for the Queen located at row, col and add them to the list
    def getQueenMoves(self, r, c, moves):
        # a queen is just a bishop and rook put together
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    # method to get all King moves for the King located at row, col and add them to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, 0), (0, -1), (1,0), (0, 1), (-1, -1), (-1, 1), (1,-1), (1, 1)) #define directions: all 8
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # check if potential move is on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                    

    # method to get piece
    def getPiece(self, row, col):
        return self.board[row][col]

class Move():
    # maps keys to values for chessboard rank and file conversions
    # key : value
    # used for converting chess notation to array indices and vice versa
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, 
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowstoRanks = {v: k for k, v in ranksToRows.items()} # reverse mapping for rows to ranks
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()} # reverse mapping for columns to files

    # initializes a move object
    def __init__(self, startSq, endsQ, board, isEnpassantMove=False):
        # initialize move object with start and end square coordinates, the chessboard, and a flag for enpassant moves
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endsQ[0]
        self.endCol = endsQ[1]
        # record the piece that is being moved and the piece that is being captured (if any)
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion: check if the move results in a pawn reaching the opposite end and set the flag accordingly
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True
        # en passant: check if the move is an en passant capture and update the captured piece accordingly
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            # set the captured piece to the corresponding pawn based on the moved pawn's color
            self.pieceCaptured = 'wP'if self.pieceMoved == 'bP' else 'bP'
        # unique identifier for the move based on board coordinates (useful for move logging and identification)
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # override the equals method to compare move objects
    def __eq__(self, other):
        # check if the other object is an instance of the move class
        if isinstance(other, Move):
            # return true if the move IDs match, indicating the same move
            return self.moveID == other.moveID
        return False

    # method to get chess notation for a move
    def getChessNotation(self):
        # can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    # method to convert row and column indices to chess notation
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowstoRanks[r]








