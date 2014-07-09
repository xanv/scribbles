# Find the best response to any tic-tac-toe board configuration.
# taking a memoized approach.

# This could be used as a starting point for a full game with the ability
# to play tic-tac-toe against an intelligent computer.
# It also serves as an example for how to find brute-force solutions for
# more complex games where straightforward logic would not be possible.

# This solution takes advantage of the symmetries of 
# the tic-tac-toe board. It builds a best_responses dictionary in ~100 ms,
# which is only a twofold improvement over a previous solution that did not
# consider symmetries.

# For practical purposes, 100ms is plenty fast enough for a one-time operation.
# However, my code generalizes to tic-tac-toe boards of size NxN, and 
# at present it is too slow for N = 4.

# If you profile this code with
#     python -m cProfile tictactoe02.py 
# you will see that most of the time is spent computing symmetries.
# In particular, rotations take most of the time.
# This is a fairly complex operation, perhaps there is a way to simplify it.



import itertools
from time import clock



class TicTacToe():
    """Implements the basic components of a tic-tac-toe solver.

    The main object created is best_responses, a dictionary that gives
    best responses to each board configuration. In more detail:

    * each key represents a board, e.g. key = ((-1, 0, 0), (1, 1, 0), (0, 0, 0)),
      where key[0] is the first row, and so forth.
      1, -1, and 0 represent an X, an O, and unfilled square respectively.
    * each value is a tuple, (move, value), where: 
        * move: a 2-tuple (i, j) indicating the player should move
          in row i, col j
            (or move = None if there is nowhere left to go).
        * value: the value of that move to the player who makes it.
            value = +1/-1/0 for a win/loss/draw, respectively.

    Given a board, the corresponding (move, value) is from the 
    perspective of the player whose turn it is to go next.        
    It is assumed without loss that X always goes first; thus,
    because X's and O's alternate, we can always tell whose turn it is 
    given the board configuration.
    """

    def __init__(self, WIDTH=3):
        self.WIDTH = WIDTH
        self.SIZE = WIDTH ** 2
        self.NUM_DIAGS = 2

        self.best_responses = {}

    
    def get_best_response(self, board):
        "Return best response to board configuration."
        try:
            return self.best_responses[board][0]
        except KeyError:
            self.build_best_responses()
            return self.best_responses[board][0]
                

    def build_best_responses(self, board=None, player=None):
        """Recursively compute best responses for all subgames of current board.
        
        Call with no arguments to build the entire best_responses dict.
        
        This adds a key to best_responses for each possible board configuration
        that could follow from board.
        
        player = 1 for X, -1 for O. This is the current player, i.e. the one
        who gets the next move.
        """

        # Initialize
        if board is None:
            board = tuple((0,)*self.WIDTH for _ in range(self.WIDTH))
            player = 1
        
        if board in self.best_responses: 
            return

        current_outcome = self.check_win(board, player)
        # If win/loss/draw has been determined, the game is over.
        if current_outcome is not None:
            for board2 in self.symmetries(board):
                self.best_responses[board2] = (None, current_outcome) # None => no move needed
            return
                
        # If we don't know the best response yet, compute it.
        best_value = -2 
        for i in range(self.WIDTH):
            for j in range(self.WIDTH):
                # This is guaranteed to execute at least once since current_outcome is None
                if board[i][j] == 0:
                    board2 = self.next_board(board, i, j, player)
                                                        
                    # If board2 is already in best_responses, this does nothing.
                    # Otherwise, it ensures board2 is added to best_responses.
                    self.build_best_responses(board2, -1 * player)
                    # player's value given board2 is the reverse of the next 
                    # player's value
                    value = -1 * self.best_responses[board2][1]
                    if value > best_value:
                        best_value, best_move = value, (i, j)
        
        # ROTATIONS/REFLECTIONS: All 8 are added to best_responses at once.
        
        # Represent best_move in board form so it can be rotated/reflected.
        # This is a bit silly...but at least we only do it once for each
        # equivalence class of board configurations.
        best_move_board = self.move_to_board(best_move, self.WIDTH)
        for board2, best_move2 in zip(self.symmetries(board), self.symmetries(best_move_board)):
            best_move2 = self.board_to_move(best_move2, self.WIDTH)
            self.best_responses[board2] = (best_move2, best_value)

        
                    
    def check_win(self, board, player):
        """Evaluate the current board to determine if there is a winner.
        
        Returns 1 if player wins, 0 if draw, -1 if loses, and None if no winner
        is yet determined.
        """
        
        lines = ([self.get_row(board, i) for i in range(self.WIDTH)] +
           [self.get_col(board, i) for i in range(self.WIDTH)] +
           [self.get_diag(board, i) for i in range(self.NUM_DIAGS)]
        )
        
        # First check for win/loss, i.e. row/col/diag with three 1's or three -1's.
        for t in lines:
            winner = sum(t)
            if winner == self.WIDTH or winner == -self.WIDTH: # 3 in a row, X's or O's.
                winner /= self.WIDTH
                # Transform winner to be +-1 from player's perspective, not X's:
                return winner * (player == 1) - winner * (player == -1)
            
        if sum(x == 0 for row in board for x in row) == 0: 
            return 0 # draw
        else: return None # game not over yet
                
    
    def get_row(self, board, i):
        return board[i]
        
    def get_col(self, board, j):
        return zip(*board)[j]

    def get_diag(self, board, i):
        "Return main diagonal if i = 0, other diagonal if i = 1"
        if i == 0: return [board[i][i] for i in range(self.WIDTH)] 
        else: return [board[i][self.WIDTH-i-1] for i in range(self.WIDTH)]
        
      
    def next_board(self, board, i, j, val):
        """Return new board tuple equal to board but with board[i][j] replaced with val.
        
        Ordinarily it would make much more sense to use a list. But this is the
        only step that requires a board to be updated, and it must ultimately 
        be a tuple to be stored as a key in best_responses.
        
        An alternative is to convert to and from a list here.
        """
        new_row = (board[i][:j] + (val,) + board[i][j+1:],)
        return (board[:i] + new_row + board[i+1:]) 
                    
    def move_to_board(self, move, width):
        """Convert a move 2-tuple to board representation.
        The board dimensions must be specified.
        
        NOTE: This returns a list, not a tuple. It doesn't matter
        for our purposes.
        """
        board = [[0]*width for _ in range(width)]
        board[move[0]][move[1]] = 1        
        return board
        
        
    def board_to_move(self, board, width):
        """Convert a move in board representation to a 2-tuple.
        The board dimensions must be specified.
        """    
        
        return next( (i,j) for i in range(width) 
                            for j in range(width)
                            if board[i][j] == 1
        )    
    
    def symmetries(self, board):
        """Identify the set of 'equivalent' boards to any board.
        (Mirror images and rotations)
        
        All 8 symmetries of a square can be generated by rotating the square
        and rotating its reflection.
        
        board is a tuple.
        symmetries returns a list of tuples, the 8 symmetries of the board,
                """
        boards = []
        
        board1 = board
        
        # 4 rotations of the unreflected board:        
        # Rotate 4 times by 90 degrees
        for r in range(4):
            board1 = self.rotate(board1)
            boards.append(board1)
            
        # Now rotations of the mirror-image:
        board1 = self.reflect(board1)
        for r in range(4):
            board1 = self.rotate(board1)
            boards.append(board1)
        
        return boards

    def reflect(self, board):
        "Reflect board, vertically across the center row"
        return tuple(board[::-1])
        
    def rotate(self, board):
        "Rotate entire board, by 90 degrees clockwise"
        # What magic is this?
        return tuple(zip(*board[::-1]))
        

    
# Some sample tests, not very high coverage.    
class TestTicTacToe():
    
    def test(self):
        print "\n---RUNNING TESTS---\n"
        
        self.test_symmetries()
        self.test_check_win()
        self.test_build_best_responses()
        
        print "\n---ALL TESTS PASS---\n"
    
    
    def test_symmetries(self):
        
        game = TicTacToe()
        
        a = ((1,1,1), (0,0,7), (0,0,0))

        a_Syms = game.symmetries(a)

        assert len(a_Syms) == 8
                
        should_be_syms = [
            ((1,1,1), (0,0,7), (0,0,0)),
            ((0,0,1), (0,0,1), (0,7,1)),
            ((0,0,0), (7,0,0), (1,1,1)),
            ((1,7,0), (1,0,0), (1,0,0)),
            ((1,1,1), (7,0,0), (0,0,0)),
            ((0,7,1), (0,0,1), (0,0,1)),
            ((0,0,0), (0,0,7), (1,1,1)),
            ((1,0,0), (1,0,0), (1,7,0))
        ]
        
        for sym in should_be_syms:
            assert sym in a_Syms
                
        print '\t* test_symmetries passes'
    
    
    def test_check_win(self): 
    
        game = TicTacToe()

        # print game.check_win(((0,0,0), (0,0,0), (0,0,0)), -1)
        assert game.check_win(((0,0,0), (0,0,0), (0,0,0)), -1) is None    
        assert game.check_win(((1,1,-1), (0,0,0), (0,0,0)), -1) is None
        
        assert game.check_win(((1,-1,-1), (0,1,0), (0,0,1)), -1) == -1 
        assert game.check_win(((1,1,1), (0,0,0), (-1,-1,0)), -1) == -1
        
        assert game.check_win(((1,1,-1), (1,0,-1), (0,0,-1)), 1) == -1
        assert game.check_win(((1,1,1), (-1,0,-1), (0,0,-1)), 1) == 1
        
        assert game.check_win(((1,1,-1), (-1,-1,1), (1,1,-1)), 1) == 0
        
        print '\t* test_check_win passes'


    def test_build_best_responses(self):
        
        game = TicTacToe()
        game.build_best_responses()
 
        # print game.best_responses[((1,1,0), (0,-1,-1), (0,0,0))]
        assert game.best_responses[((1,1,0), (0,-1,-1), (0,0,0))] == ((0,2), 1)

        # Since the solver has no preference for winning sooner rather than
        # later, it won't necessarily choose the move that ends the game
        # when it could do another move that also leads to an eventual win.        
        # But at least we can check that it DOES expect to win given such a board.
        assert game.best_responses[((1,0,0), (1,-1,-1), (0,0,0))][1] == 1
        
        print '\t* test_build_best_responses passes'

        
        
def funtime(fun, *args):
    "Time the execution of function fun"
    t0 = clock()
    fun(*args)
    t1 = clock()
    print "Runtime: ", t1-t0



if __name__ == '__main__':

    tests = TestTicTacToe()
    tests.test()

    # print "Timing for WIDTH = 2..."
    # tictactoe = TicTacToe(2)
    # funtime(tictactoe.build_best_responses)
    # print "Size of best_responses:", len(tictactoe.best_responses)

    print "\n"

    print "Timing for WIDTH = 3..."
    tictactoe = TicTacToe(3)
    funtime(tictactoe.build_best_responses)
    print "Size of best_responses:", len(tictactoe.best_responses)

    # print "\n"

    # print "Timing for WIDTH = 4..."
    # tictactoe = TicTacToe(4)
    # funtime(tictactoe.build_best_responses)
    # print "Size of best_responses:", len(tictactoe.best_responses)
