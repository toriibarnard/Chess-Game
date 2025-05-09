import random


class ChessAI:
    """
    A chess AI using the Negamax algorithm with Alpha-Beta pruning.
    This AI evaluates positions and selects the best move based on piece values,
    position control, and other chess heuristics.
    """

    def __init__(self, depth=3):
        """
        Initialize the chess AI.

        Args:
            depth (int): The search depth for the Negamax algorithm.
        """
        self.depth = depth
        # Piece scores: pawn=1, knight=3, bishop=3, rook=5, queen=9, king=0 (infinite value but not used in eval)
        self.piece_scores = {"P": 10, "N": 30, "B": 30, "R": 50, "Q": 90, "K": 900}

        # Position tables to encourage good piece placement
        self.pawn_scores = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        self.knight_scores = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]

        self.bishop_scores = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]

        self.rook_scores = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ]

        self.queen_scores = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]

        self.king_scores_middle_game = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]

        self.king_scores_end_game = [
            [-50, -40, -30, -20, -20, -30, -40, -50],
            [-30, -20, -10, 0, 0, -10, -20, -30],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-30, -10, 30, 40, 40, 30, -10, -30],
            [-30, -10, 30, 40, 40, 30, -10, -30],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-30, -30, 0, 0, 0, 0, -30, -30],
            [-50, -30, -30, -30, -30, -30, -30, -50]
        ]

    def find_best_move(self, game_state, valid_moves):
        """
        Find the best move for the current position using Negamax with Alpha-Beta pruning.

        Args:
            game_state: The current state of the chess game.
            valid_moves: List of valid moves for the current player.

        Returns:
            The best move according to the evaluation.
        """
        self.counter = 0  # For tracking nodes evaluated (useful for debugging)

        # Randomize move order for better alpha-beta pruning
        random.shuffle(valid_moves)

        # Find best move with negamax
        best_score = -float('inf')
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        for move in valid_moves:
            game_state.makeMove(move)
            score = -self.negamax(game_state, self.depth - 1, -beta, -alpha, -1)
            game_state.undoMove()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        return best_move

    def negamax(self, game_state, depth, alpha, beta, color):
        """
        Negamax algorithm with Alpha-Beta pruning.

        Args:
            game_state: Current state of the chess game.
            depth: Remaining search depth.
            alpha: Alpha value for pruning.
            beta: Beta value for pruning.
            color: 1 for white, -1 for black.

        Returns:
            The best score according to the evaluation.
        """
        self.counter += 1

        if depth == 0:
            return color * self.evaluate_board(game_state)

        valid_moves = game_state.getValidMoves()

        # Check for checkmate or stalemate
        if len(valid_moves) == 0:
            if game_state.inCheck():
                return -float('inf')  # Checkmate
            else:
                return 0  # Stalemate

        # Sort moves to improve alpha-beta pruning efficiency
        # This is a simple ordering heuristic - capturing moves first
        valid_moves.sort(key=lambda move: 1 if move.pieceCaptured != '--' else 0, reverse=True)

        max_score = -float('inf')
        for move in valid_moves:
            game_state.makeMove(move)
            score = -self.negamax(game_state, depth - 1, -beta, -alpha, -color)
            game_state.undoMove()

            max_score = max(max_score, score)
            alpha = max(alpha, max_score)

            if alpha >= beta:
                break  # Alpha-Beta pruning

        return max_score

    def evaluate_board(self, game_state):
        """
        Evaluate the chess board from the perspective of the current player.

        Args:
            game_state: Current state of the chess game.

        Returns:
            A score representing how good the position is for the current player.
        """
        if game_state.checkMate:
            # If current player is in checkmate, return worst possible score
            return -float('inf')
        if game_state.staleMate:
            # Stalemate is a draw (0)
            return 0

        score = 0

        # Count material and apply piece-square tables
        for row in range(8):
            for col in range(8):
                piece = game_state.board[row][col]
                if piece != '--':
                    # Determine if piece is white or black
                    is_white = piece[0] == 'w'
                    multiplier = 1 if is_white else -1
                    piece_type = piece[1]

                    # Add material value
                    score += multiplier * self.piece_scores[piece_type]

                    # Apply piece-square tables (adjusting indices for black perspective)
                    position_score = 0
                    if piece_type == 'P':
                        position_score = self.pawn_scores[row][col]
                    elif piece_type == 'N':
                        position_score = self.knight_scores[row][col]
                    elif piece_type == 'B':
                        position_score = self.bishop_scores[row][col]
                    elif piece_type == 'R':
                        position_score = self.rook_scores[row][col]
                    elif piece_type == 'Q':
                        position_score = self.queen_scores[row][col]
                    elif piece_type == 'K':
                        # Simplified detection of endgame
                        is_endgame = self.is_endgame(game_state)
                        if is_endgame:
                            position_score = self.king_scores_end_game[row][col]
                        else:
                            position_score = self.king_scores_middle_game[row][col]

                    # Adjust position score for black pieces (flip board perspective)
                    if not is_white:
                        position_score = self.pawn_scores[7 - row][col] if piece_type == 'P' else position_score
                        position_score = self.knight_scores[7 - row][col] if piece_type == 'N' else position_score
                        position_score = self.bishop_scores[7 - row][col] if piece_type == 'B' else position_score
                        position_score = self.rook_scores[7 - row][col] if piece_type == 'R' else position_score
                        position_score = self.queen_scores[7 - row][col] if piece_type == 'Q' else position_score
                        position_score = (self.king_scores_end_game[7 - row][col] if self.is_endgame(game_state)
                                          else self.king_scores_middle_game[7 - row][
                            col]) if piece_type == 'K' else position_score

                    score += multiplier * position_score * 0.1  # Scale down the position influence

        # Add bonus for mobility (number of legal moves)
        current_valid_moves = len(game_state.getValidMoves())

        # Temporarily switch sides to count opponent's moves
        game_state.whiteToMove = not game_state.whiteToMove
        opponent_valid_moves = len(game_state.getValidMoves())
        game_state.whiteToMove = not game_state.whiteToMove

        mobility_score = (current_valid_moves - opponent_valid_moves) * 0.1
        score += mobility_score

        # Adjust score perspective based on whose turn it is
        # If it's black's turn, negate the score to maintain consistent perspective
        return score if game_state.whiteToMove else -score

    def is_endgame(self, game_state):
        """
        Determine if the game is in the endgame phase.
        A simple heuristic: endgame starts when both sides have no queens or
        when both sides have less than 13 points in pieces (not counting king).

        Args:
            game_state: Current state of the chess game.

        Returns:
            True if in endgame, False otherwise.
        """
        # Count queens
        white_queen = black_queen = False
        white_material = black_material = 0

        for row in range(8):
            for col in range(8):
                piece = game_state.board[row][col]
                if piece == 'wQ':
                    white_queen = True
                elif piece == 'bQ':
                    black_queen = True
                elif piece[0] == 'w' and piece[1] != 'K':
                    piece_type = piece[1]
                    white_material += self.piece_scores[piece_type]
                elif piece[0] == 'b' and piece[1] != 'K':
                    piece_type = piece[1]
                    black_material += self.piece_scores[piece_type]

        # No queens endgame condition
        if not white_queen and not black_queen:
            return True

        # Low material endgame condition
        if white_material < 130 and black_material < 130:
            return True

        return False
