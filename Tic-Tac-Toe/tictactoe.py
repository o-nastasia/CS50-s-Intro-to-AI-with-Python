"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):

    if terminal(board) == True:
        return None
    elif board == EMPTY:
        return(X)
    else:
        counter_X = 0
        for i in range(3):
                for j in range(3):
                    if board[i][j] == X:
                        counter_X += 1
        counter_O = 0
        for i in range(3):
                for j in range(3):
                    if board[i][j] == O:
                        counter_O += 1
        if counter_X > counter_O:
            return(O)
        else:
            return(X)
    """
    Returns player who has the next turn on a board.
    raise NotImplementedError
    """


def actions(board):


    actions = set()

    for i in range(3):
         for j in range(3):
              if board[i][j] == EMPTY:
                  actions.add((i, j))
    return(actions)


    """
    Returns set of all possible actions (i, j) available on the board.
    raise NotImplementedError
    """


def result(board, action):

    copied_board = copy.deepcopy(board)
    if copied_board[action[0]][action[1]] == EMPTY:
        copied_board[action[0]][action[1]] = player(board)
    elif action[0] or action[1] < 0:
        raise Exception("Out of range")
    else:
        raise Exception("Not a valid move")
    return copied_board


    """
    Returns the board that results from making move (i, j) on the board.
    raise NotImplementedError
    """


def winner(board):

    for i in range(3):
        if (board[i][0] != EMPTY and board[i][0] == board[i][1] == board[i][2]):
            if board[i][0] == X:
                return(X)
            else:
                return(O)
    for j in range(3):
        if (board[0][j] != EMPTY and board[0][j] == board[1][j] == board[2][j]):
            if board[0][j] == X:
                return(X)
            else:
                return(O)

    if (board[0][0] == board[1][1] == board[2][2] != EMPTY or board[0][2] == board[1][1] == board [2][0] != EMPTY):
        if board[1][1] == X:
            return(X)
        else:
            return(O)
    else:
        return None

    """
    Returns the winner of the game, if there is one.
    raise NotImplementedError
    """


def terminal(board):

    if winner(board) is not None:
        return True
    elif not actions(board):
        return True
    else:
        return False

    """
    Returns True if game is over, False otherwise.
    raise NotImplementedError
    """


def utility(board):

    if winner(board) == X:
        return(1)
    elif winner(board) == O:
        return(-1)
    else:
        return(0)

    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    raise NotImplementedError
    """

def minimax(board):
    """
    Returns the optimal move for the current player on the board.
    """
    # Check for terminal state
    if terminal(board):
        return None

    # If X's turn
    elif player(board) == X:
        options = []
        for action in actions(board):
            score = min_value(result(board, action))
            # Store options in list
            options.append([score, action])
        # Return highest value action
        return sorted(options, reverse=True)[0][1]

    # If O's turn
    else:
        options = []
        for action in actions(board):
            score = max_value(result(board, action))
            # Store options in list
            options.append([score, action])
        # Return lowest value action
        return sorted(options)[0][1]


def max_value(board):
    """
    Returns the highest value option of a min-value result
    """
    # Check for terminal state
    if terminal(board):
        return utility(board)

    # Loop through possible steps
    v = float('-inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    """
    Returns the smallest value option of a max-value result
    """
    # Check for terminal state
    if terminal(board):
        return utility(board)

    # Loop through possible steps
    v = float('inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v