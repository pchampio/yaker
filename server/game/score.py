def is_Sorted(lst):
    if len(lst) == 1:
       return True
    return lst[0] < lst[1] and is_Sorted(lst[1:])

# return one row
def diagonal(matrix):
    return ([matrix[i][i] for i in range(min(len(matrix[0]),len(matrix)))])

def score_in_row(row):
    row_count = []
    pts = 0
    for item in row:
         row_count.append(row.count(item))

    if row_count.count(2) == 4: # 2 paire
        pts += 3
    elif row_count.count(4) == 4: # carre
        pts += 6
    elif row_count.count(5) == 5: # 5x
        pts += 8
    elif row_count.count(3) == 3 and row_count.count(2) == 2: # full
        pts += 6
    elif row_count.count(3) == 3: # brelan
        pts += 3
    elif row_count.count(2) == 2: # paire
        pts += 1
    elif row_count.count(1) == 5:
        if max(row) - min(row) == 4:
            if  is_Sorted(row) or is_Sorted(row[::-1]):
                pts += 12 # suite sorted
            else:
                pts += 8 # suite
    return pts


def score_in_board(board):
    pts = 0
    for row in board:
        pts += score_in_row(row)

    pts += ( score_in_row(diagonal(board)) )*2
    return pts

def Score(board):

    # rotation 90* pour calcul des col
    board2 = list(zip(*board[::-1]))
    return (score_in_board(board) + score_in_board(board2))
