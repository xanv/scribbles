# Find the best response to any tic-tac-toe board configuration.
# taking a memoized approach.

# This could be used as a starting point for a full game with the ability
# to play tic-tac-toe against an intelligent computer.
# It also serves as an example for how to find brute-force solutions for
# more complex games where straightforward logic would not be possible.

# When I profile this code with
#     python -m cProfile tictactoe02.py 
# there is no single dominant bottleneck.
# It might be time to try a different approach.

# I exploit the symmetries of the tic-tac-toe board positions to reduce
# the problem. In addition, to accelerate the process of rotating and reflecting
# the board repeatedly, I precompute the permutation induced by these operations
# and apply that permutation directly. It doesn't save that much time, given
# that it wasn't a bottleneck. However, it's an interesting approach that could
# be used more generally when a complex transformation has to be performed repeatedly.


import itertools
from time import clock



class TicTacToe():
    """Implements the basic components of a tic-tac-toe solver.

    The main object created is best_responses, a dictionary that gives
    best responses to each board configuration. In more detail:

    * each key represents a board, e.g. key = (-1, 0, 0, 1, 1, 0, 0, 0, 0),
      where key[0:3] is the first row, and so forth.
      1, -1, and 0 represent an X, an O, and unfilled square respectively.
    * each value is a tuple, (move, value), where: 
        * move = i means player goes in ith square of board
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
        
        # Precomputing to speed up board reflection and rotation
        self.rotation_perm = self.extract_perm(self.rotate_raw)
        self.reflection_perm = self.extract_perm(self.reflect_raw)                

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
            board = (0,) * self.SIZE
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
        for i in range(self.SIZE):
            if board[i] == 0: # True at least once
                # Replace ith spot with player's move
                board2 = board[:i] + (player,) + board[i+1:]
                                                    
                # If board2 is already in best_responses, this does nothing.
                # Otherwise, it ensures board2 is added to best_responses.
                self.build_best_responses(board2, -1 * player)
                # player's value given board2 is the reverse of the next 
                # player's value
                value = -1 * self.best_responses[board2][1]
                if value > best_value:
                    best_value, best_move = value, i
        
        # ROTATIONS/REFLECTIONS: All 8 are added to best_responses at once.
        best_move_board = (0,)*best_move + (player,) + (0,)*(self.SIZE - best_move - 1)
        for board2, best_move2 in zip(self.symmetries(board), self.symmetries(best_move_board)):
            best_move2 = best_move2.index(player)
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
            
        if board.count(0) == 0: 
            return 0 # draw
        else: return None # game not over yet

        
    def get_row(self, board, i):
        return board[i*self.WIDTH:(i+1)*self.WIDTH]
        
    def get_col(self, board, j):
        return [board[i*self.WIDTH + j] for i in range(self.WIDTH)]

    def get_diag(self, board, i):
        "Return main diagonal if i = 0, other diagonal if i = 1"
        if i == 0: 
            return [board[(self.WIDTH+1) * i] for i in range(self.WIDTH)]
        else:
            return [board[(self.WIDTH-1) + (self.WIDTH-1)*i] for i in range(self.WIDTH)]
                    
    
    def symmetries(self, board):
        """Identify the set of 'equivalent' boards to any board.
        (Mirror images and rotations)
        
        All 8 symmetries of a square can be generated as the 4 rotations
        together with their reflections.
        
        board is a tuple.
        symmetries is a generator yielding tuples, the 8 symmetries of the board.
        
        """        
        board1 = tuple(board)
        yield board1
        yield self.reflect(board1)
        
        for _ in range(3):
            board1 = self.rotate(board1)
            yield board1
            yield self.reflect(board1)
        

    # These are the operations we actually USE to reflect and rotate
    def reflect(self, board):
        """Return board reflected across center row.
           The reflection operation is accelerated by executing a
           precomputed permutation template.
        """
        return self.execute_perm(board, self.reflection_perm)
        
    def rotate(self, board):
        """Return board rotated 90 degreese clockwise.
           The reflection operation is accelerated by executing a
           precomputed permutation template.
        """
        return self.execute_perm(board, self.rotation_perm)
        
        
    # These are the ordinary reflect and rotation operations, with no
    # precomputing.
    def reflect_raw(self, board):
        "Return board reflected across the center row"
        nested = self.flat_to_nested(board)
        return self.nested_to_flat(nested[::-1])
        
    def rotate_raw(self, board):
        "Return board rotated by 90 degrees clockwise"
        nested = self.flat_to_nested(board)
        nested_rotated = zip(*nested[::-1])
        return self.nested_to_flat(nested_rotated)

    # This is used with f = reflect_raw and rotate_raw to extract 
    # the permutations they induce. It is separated from execute_perm
    # because this is the operation that only needs to be performed ONCE.
    def extract_perm(self, f):
        "Extract the permutation of board elements induced by f."
        A = range(self.SIZE)
        # Track the indices through the operation of f:
        fA = f(A)
        
        # fA[j] tells us the original index i of the element that
        # got sent to index j by f. We want to know the inverse:
        # Given original index i, what index j does i get sent to?
        # So we sort A according to fA, 'inverting' the permutation.        
        return [j for i,j in sorted(zip(fA, A))]
        
    def execute_perm(self, board, perm):
        "Execute an extracted permutation on board"
        board2 = [0] * self.SIZE
        for i1, i2 in enumerate(perm):
            board2[i2] = board[i1]
        return tuple(board2)

        
    def flat_to_nested(self, flat_list):
        "Turn flat_list into nested list of rows"
        return [flat_list[i*self.WIDTH: (i+1)*self.WIDTH] for i in range(self.WIDTH)]

    def nested_to_flat(self, nested_list):
        "Turn nested list of rows into flat list"
        return [x for row in nested_list for x in row]
    
    
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

        b = (1,2,3, 4,5,6, 7,8,9)
        
        assert game.reflect(b) == (7,8,9, 4,5,6, 1,2,3)
        assert game.rotate(b) == (7,4,1, 8,5,2, 9,6,3)

        a = (1,1,1, 0,0,7, 0,0,0)

        a_Syms = set(game.symmetries(a))

        assert len(a_Syms) == 8
                
        should_be_syms = [
            (1,1,1, 0,0,7, 0,0,0),
            (0,0,1, 0,0,1, 0,7,1),
            (0,0,0, 7,0,0, 1,1,1),
            (1,7,0, 1,0,0, 1,0,0),
            (1,1,1, 7,0,0, 0,0,0),
            (0,7,1, 0,0,1, 0,0,1),
            (0,0,0, 0,0,7, 1,1,1),
            (1,0,0, 1,0,0, 1,7,0)
        ]
        
        for sym in should_be_syms:
            assert sym in a_Syms
                            
        print '\t* test_symmetries passes'
    
    
    def test_check_win(self): 
    
        game = TicTacToe()

        # print game.check_win((0,0,0, 0,0,0, 0,0,0), -1)
        assert game.check_win((0,0,0, 0,0,0, 0,0,0), -1) is None    
        assert game.check_win((1,1,-1, 0,0,0, 0,0,0), -1) is None
        
        assert game.check_win((1,-1,-1, 0,1,0, 0,0,1), -1) == -1 
        assert game.check_win((1,1,1, 0,0,0, -1,-1,0), -1) == -1
        
        assert game.check_win((1,1,-1, 1,0,-1, 0,0,-1), 1) == -1
        assert game.check_win((1,1,1, -1,0,-1, 0,0,-1), 1) == 1
        
        assert game.check_win((1,1,-1, -1,-1,1, 1,1,-1), 1) == 0
        
        print '\t* test_check_win passes'


    def test_build_best_responses(self):
        
        game = TicTacToe()
        game.build_best_responses()
        
        # Note these are reachable board positions, which is important for 
        # these tests. Non-reachable boards will not be in best_responses.
        
        # Finished game is evaluated correctly. 
        assert game.best_responses[(1,-1,1, -1,1,-1, 1,-1,1)] == (None, -1)
        assert game.best_responses[(1,1,-1, -1,-1,1, 1,1,-1)] == (None, 0)
        
        # Nearly finished game evaluated correctly: 
        # X to go in last slot and will win
        assert game.best_responses[(1,-1,1, -1,1,1, -1,-1,0)] == (8,1)
        # X to go in first slot and will win
        assert game.best_responses[(0,1,1, -1,-1,1, 1,-1,-1)] == (0,1)        
 
        # Need more tests here.
        
        # Since the solver has no preference for winning sooner rather than
        # later, it won't necessarily choose the move that ends the game
        # when it could do another move that also leads to an eventual win.        
        # But we can check that it only does moves in this class, and expects to win 
        a = game.best_responses[(1,1,0, 0,-1,-1, 0,0,0)]
        assert a == (2, 1) or a == (3, 1) 
        b = game.best_responses[(1,0,0, 1,-1,-1, 0,0,0)]
        assert b == (1, 1) or b == (2,1) or b == (6,1)
        
        if game.WIDTH == 3:
            # There are 5478 possible board states.
            assert len(game.best_responses) == 5478
        
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
