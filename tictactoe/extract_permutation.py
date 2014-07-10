# If we have a complex operation that induces a permutation of a list,
# and we have to execute the operation repeatedly,
# we may save time by performing the operation only once,
# recording the induced permutation, and creating a new function
# that directly permutes the elements.

# This file is just a quick demonstration of the idea, 
# using matrix rotation as the operation. This isn't a very good example
# because there are fast ways of doing straight-up rotation, though.

# The idea applies far more broadly than list permutations, of course.

import random
from time import clock

WIDTH = 3
SIZE = WIDTH ** 2

list0 = range(SIZE)


def funtime(f, reps, *args):
    "Time the execution of function f"
    t0 = clock()
    for _ in xrange(reps):
        f(*args)
    t1 = clock()
    print "Runtime:", t1-t0 

    
# As part of the demonstration, we start with a matrix that is
# expressed as a flat list. It must first be converted to a nested
# list of rows, then rotated, then flattened again.
# It would be arduous to do this repeatedly.
# This example arose out of a tic-tac-toe solver I had created, where the list
# of SIZE = 9 represents a board, and symmetries of the board were calculated
# to speed other calculations.

def rotate1(list0):
    "Standard way of rotating."
    
    # Convert the flat list to a nested list
    mat0 = [list0[i*WIDTH: (i+1)*WIDTH] for i in range(WIDTH)]
    # Rotate by 90 deg CW
    mat1 = zip(*mat0[::-1])
    
    # There could be a lot of other arbitrarily complex stuff going on here.
    # It will impact the running time of rotate1 but not rotate2, even
    # though rotate2 depends on rotate1.
    
    # Flatten back out
    return [x for row in mat1 for x in row]



def rotate2(list0, perm):
    """Rotate using a precomputed permutation.
    Given that rotate1 sends index i to index j, we will have perm[j] = i.
    """
    list1 = [0] * SIZE
    for j, i in enumerate(perm):
        list1[j] = list0[i]
    return list1
    
    
# Now we test these two approaches to rotating.
        
# list0 = [6,2,7,8,9,0,1,2,3]
list0 = [random.randint(0,9) for _ in range(SIZE)]

# We generate the permutation, just once.
perm = rotate1(range(SIZE))

# As you can see, these have the same effect:
print rotate1(list0)
print rotate2(list0, perm)

M = 10**4

funtime(rotate1, M, list0)
funtime(rotate2, M, list0, perm)

# We do get a performance improvement for small enough lists.
# (True in the case of tic-tac-toe).
# This technique would be especially
# useful if the operation we were trying to replace was more complex.
