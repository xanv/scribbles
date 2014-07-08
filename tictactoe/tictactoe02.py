# Find the best response to any tic-tac-toe board configuration.
# taking a memoized approach.

# This could be used as a starting point for a full game with the ability
# to play tic-tac-toe against an intelligent computer.
# It also serves as an example for how to find brute-force solutions for
# more complex games where straightforward logic would not be possible.

# This is a first pass at a solution that takes advantage of the symmetries of 
# the tic-tac-toe board. It builds a best_responses dictionary in ~100 ms,
# which is only a twofold improvement over a previous solution that did not
# consider symmetries.  This is largely due to a lot of copying/conversion between
# lists and tuples.
# It needs to be majorly refactored.

# Xan Vongsathorn
# 7/8/2014

import itertools
from time import clock



class TicTacToe():
    """Implements the basic components of a tic-tac-toe solver.
    
    best_responses is a dictionary where:
        * each key represents a board, e.g. key = (-1, 0, 0, 1, 1, 0, 0, 0, 0),
          where key[0:3] is the first row, and so forth.
          1, -1, and 0 represent an X, an O, and unfilled square respectively.
        * each value is a tuple, (move, value), where: 
            * move: an int in range(9) indicating where the player should move,
                or None if there is nowhere left to go.
            * value: the value of that move to the player who makes it.
                value = +1/-1/0 for a win/loss/draw, respectively.

                
        Note: given a board, the corresponding (move, value) is from the 
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
            board = tuple([0]*self.SIZE)
            player = 1
        
        if board in self.best_responses: 
            return

        win = self.check_win(board, player)
        # If win/loss/draw has been determined, the game is over.
        if win is not None:
            for board2 in self.symmetries(board):
                self.best_responses[board2] = (None, win) # None => no move needed
            return
                
        # If we don't know the best response yet, compute it.
        best_value, best_move = -2, -2
        for i, val in enumerate(board):
            if val == 0:
                # create new tuple with player's move in ith slot
                board2 = board[:i] + (player,) + board[i+1:]
                
                # If board2 is already in best_responses, this does nothing.
                # Otherwise, it ensures board2 is added to best_responses.
                self.build_best_responses(board2, -1 * player)
                # The player's value given board2 is the reverse of the next 
                # player's value
                value = -1 * self.best_responses[board2][1]
                if value > best_value:
                    best_value, best_move = value, i
        
        # ROTATIONS/REFLECTIONS: All 8 are added to best_responses at once.
        
        # Represent best_move in list form so it can be rotated.
        best_move_list = [0] * self.SIZE
        best_move_list[best_move] = 1 
        for board2, best_move2 in zip(self.symmetries(board), self.symmetries(best_move_list)):
            # Convert best_move back to single number:
            best_move2 = best_move2.index(1)
            self.best_responses[board2] = (best_move2, best_value)

        
        # self.best_responses[board] = (best_move, best_value)

                    
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
            
        if board.count(0) == 0: return 0 # draw
        else: return None # game not over yet
                

    def get_row(self, board, i):
        "Return row i of board as a list."    
        return [board[i*self.WIDTH + j] for j in range(self.WIDTH)]
        # return board[i*self.WIDTH:(i+1)*self.WIDTH]
        
    def get_col(self, board, j):
        "Return column j of board as a list."
        return [board[i*self.WIDTH + j] for i in range(self.WIDTH)]

    def get_diag(self, board, i):
        "Return main diagonal if i = 0, other diagonal if i = 1"
        if i == 0:
            # For WIDTH = 3, this gives board[j] for j = 0, 4, 8. 
            return [board[(self.WIDTH+1) * i] for i in range(self.WIDTH)]
        else:
            # For WIDTH = 3, this gives board[j] for = 2, 4, 6.
            return [board[(self.WIDTH-1) + (self.WIDTH-1)*i] for i in range(self.WIDTH)]
    
    
    def symmetries(self, board):
        """Identify the set of 'equivalent' boards to any board.
        (Mirror images and rotations)
        
        board is a tuple.
        symmetries returns a list of tuples, the 8 symmetries of the board.
                """
        boards = [] # tuples
        
        # We build up all the symmetries by combining a single
        # reflection with rotations.
        # This generates the 8 symmetries of a square.        
        
        # I should probably switch to storing the tic-tac-toe board in general
        # as a 2D array. For now, just implementing it here.
        board1 = [self.get_row(board, i) for i in range(self.WIDTH)]
        
        # 4 rotations of the unreflected board:        
        # Rotate 4 times by 90 degrees
        for r in range(4):
            board1 = self.rotate(board1)
            # Flattened tuple. Fix this if I switch to a 2D array.
            boards.append(tuple(elt for row in board1 for elt in row))
            
        # Now rotations of the mirror-image:
        board1 = self.reflect(board1)
        for r in range(4):
            board1 = self.rotate(board1)
            boards.append(tuple(elt for row in board1 for elt in row))
        
        return boards

    def reflect(self, board):
        "Reflect board, vertically across the center row"
        # Code now assumes a list of rows.
        return board[::-1]
        
    def rotate(self, board):
        "Rotate entire board, by 90 degrees clockwise"
        # Code now assumes a list of rows.
        
        # When rotated, the rows become columns, oriented one way or the other
        # depending on CW vs CCW. 
        # Together with a reflection before or after zipping/rotating, we can implement
        # a CW or CCW rotation.
        return zip(*board[::-1])
    
    
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
        
        a = (1,1,1, 0,0,-1, 0,0,0)

        a_Syms = game.symmetries(a)

        assert len(a_Syms) == 8
                
        should_be_syms = [
            (1,1,1, 0,0,-1, 0,0,0),
            (0,0,1, 0,0,1, 0,-1,1),
            (0,0,0, -1,0,0, 1,1,1),
            (1,-1,0, 1,0,0, 1,0,0),
            (1,1,1, -1,0,0, 0,0,0),
            (0,-1,1, 0,0,1, 0,0,1),
            (0,0,0, 0,0,-1, 1,1,1),
            (1,0,0, 1,0,0, 1,-1,0)
        ]
        
        for sym in should_be_syms:
            print sym
            assert sym in a_Syms
                
        print 'test_symmetries passes'
    
    
    def test_check_win(self): 
    
        game = TicTacToe()

        assert game.check_win((0,0,0, 0,0,0, 0,0,0), -1) is None    
        assert game.check_win((1,1,-1, 0,0,0, 0,0,0), -1) is None
        
        assert game.check_win((1,-1,-1, 0,1,0, 0,0,1), -1) == -1 
        assert game.check_win((1,1,1, 0,0,0, -1,-1,0), -1) == -1
        
        assert game.check_win((1,1,-1, 1,0,-1, 0,0,-1), 1) == -1
        assert game.check_win((1,1,1, -1,0,-1, 0,0,-1), 1) == 1
        
        assert game.check_win((1,1,-1, -1,-1,1, 1,1,-1), 1) == 0
        
        print 'test_check_win passes'


    def test_build_best_responses(self):
        
        game = TicTacToe()
        game.build_best_responses()
 
        print game.best_responses[(1,1,0, 0,-1,-1, 0,0,0)]
        assert game.best_responses[(1,1,0, 0,-1,-1, 0,0,0)] == (2, 1)

        # Since the solver has no preference for winning sooner rather than
        # later, it won't necessarily choose the move that ends the game
        # when it could do another move that also leads to an eventual win.
        # assert best_responses[(1,0,0, 1,-1,-1, 0,0,0)] == (6,1) # actually == (1,1)
        
        # But at least we can check that it DOES expect to win given such a board.
        assert game.best_responses[(1,0,0, 1,-1,-1, 0,0,0)][1] == 1
        
        print 'test_build_best_responses passes'

        
        
def funtime(fun, *args):
    "Time the execution of function fun"
    t0 = clock()
    fun(*args)
    t1 = clock()
    print "Runtime: ", t1-t0



tests = TestTicTacToe()
tests.test()


print "Timing for WIDTH = 2..."
tictactoe = TicTacToe(2)
funtime(tictactoe.build_best_responses)
print "Size of best_responses:", len(tictactoe.best_responses)

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
