
import STcpClient
import random
import copy

'''
    輪到此程式移動棋子
    board : 棋盤狀態(list of list), board[i][j] = i row, j column 棋盤狀態(i, j 從 0 開始)
            0 = 空、1 = 黑、2 = 白、-1 = 四個角落
    is_black : True 表示本程式是黑子、False 表示為白子

    return Step
    Step : single touple, Step = (r, c)
            r, c 表示要下棋子的座標位置 (row, column) (zero-base)
'''
orientation = [(0, 1), (0, -1), (1, 0), (-1, 0),
               (-1, 1), (1, -1), (1, 1), (-1, -1)]
BLACK_NUM = 1
WHITE_NUM = 2


def GetInitBoard():
    return [[-1, 0, 0, 0, 0, 0, 0, -1],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [ 0, 0, 0, 0, 0, 0, 0,  0],
            [-1, 0, 0, 0, 0, 0, 0, -1]]

def CheckBoardFull(board):
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                return False
    return True

def CheckGameEnd(board):
    if CheckBoardFull(board):
        return True
    blackVacancy = GetRandomStep(board, True)
    whiteVacancy = GetRandomStep(board, False)
    if not blackVacancy and not whiteVacancy:
        return True
    return False

def FindBoardVacancy(board, is_black):
    vacancy = []
    for i in range(8):
        for j in range(8):
            if board[i][j] != 0:
                continue;
            if ((i >= 1 and i < 7 and j >= 1 and j < 7) or
                len(FindPosCanFlipList(board, (i, j), is_black, allList=False)) > 0):
                vacancy.append((i, j))
    return vacancy

def FindWinner(board):
    blackScore, whiteScore = FindBoardScore(board)

    if blackScore == whiteScore:
        return 0
    elif blackScore > whiteScore:
        return BLACK_NUM
    return WHITE_NUM

def FindBoardScore(board):
    blackScore = 0
    whiteScore = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] == BLACK_NUM:
                blackScore += 1
            elif board[i][j] == WHITE_NUM:
                whiteScore += 1
    return blackScore, whiteScore

def FindBoardOpennessScore(board, pos, is_black):
    canFlipList = FindPosCanFlipList(board, pos, is_black)
    if not canFlipList:
        return 100
    score = 0
    for (r,c) in canFlipList:
        for (dr, dc) in orientation:
            new_r = r + dr
            new_c = c + dc
            if (new_r >= 0 and new_r < 8 and new_c >= 0 and new_c < 8 and 
                board[new_r][new_c] == 0):
                score += 1
    return score
    
def GetRandomStep(board, is_black):
    vacancy = FindBoardVacancy(board, is_black)
    if not vacancy:
        return None
    return random.choice(vacancy)

def GetGreedyStep(board, is_black):
    vacancy = FindBoardVacancy(board, is_black)
    if not vacancy:
        return None

    maxScore = -1
    maxScorePos = None
    for pos in vacancy:
        newBoard, _ = TryUpdateBoard(board, pos, is_black)
        blackScore, whiteScore = FindBoardScore(newBoard)
        score = blackScore if is_black else whiteScore
        if score > maxScore:
            maxScore = score
            maxScorePos = [pos]
        elif score == maxScore:
            maxScorePos.append(pos)
    return random.choice(maxScorePos)

def GetOpennessStep(board, is_black):
    vacancy = FindBoardVacancy(board, is_black)
    if not vacancy:
        return None
    
    minOpennessScore = 100
    minOpennessScorePos = []
    for pos in vacancy:
        opennessScore = FindBoardOpennessScore(board, pos, is_black)
        if opennessScore < minOpennessScore:
            minOpennessScore = opennessScore
            minOpennessScorePos = [pos]
        elif opennessScore == minOpennessScore:
            minOpennessScorePos.append(pos)
    return random.choice(minOpennessScorePos)

def GetMinMaxScore(board, is_black, is_max, depth):
    if CheckBoardFull(board) or depth == 0:
        blackScore, _ = FindBoardScore(board)
        return blackScore

    vacancy = FindBoardVacancy(board, is_black)

    targetScore = 0 if is_max else 100
    for pos in vacancy:
        newBoard, _ = TryUpdateBoard(board, pos, is_black)
        score = GetMinMaxScore(newBoard, not is_black, not is_max, depth-1)
        if ((is_max and score > targetScore) or
            (not is_max and score < targetScore)):
            targetScore = score
    return targetScore

def GetMinMaxStep(board, is_black):
    vacancy = FindBoardVacancy(board, is_black)
    if not vacancy:
        return None

    maxScore = 0
    maxScorePos = None
    for pos in vacancy:
        newBoard, _ = TryUpdateBoard(board, pos, is_black)
        score = GetMinMaxScore(newBoard, not is_black, True, depth=2)
        if score > maxScore:
            maxScore = score
            maxScorePos = pos
    return maxScorePos



def FindPosCanFlipList(board, pos, is_black, allList=True):
    this = BLACK_NUM if is_black else WHITE_NUM
    another = WHITE_NUM if is_black else BLACK_NUM
    canFlipList = []
    for (dr, dc) in orientation:
        tmpFlipList = []
        r = pos[0] + dr
        c = pos[1] + dc
        while r >= 0 and r < 8 and c >= 0 and c < 8:
            if board[r][c] == this:
                canFlipList += tmpFlipList
                if canFlipList and not allList:
                    return canFlipList
                break
            elif board[r][c] == another:
                tmpFlipList.append((r,c))
                r += dr
                c += dc
            else:
                break
    return canFlipList

def UpdateBoard(board, pos, is_black):
    this = BLACK_NUM if is_black else WHITE_NUM
    board[pos[0]][pos[1]] = this
    canFlipList = FindPosCanFlipList(board, pos, is_black)
    for (r,c) in canFlipList:
        board[r][c] = this

def TryUpdateBoard(board, pos, is_black):
    this = BLACK_NUM if is_black else WHITE_NUM
    newBoard = copy.deepcopy(board)
    newBoard[pos[0]][pos[1]] = this
    canFlipList = FindPosCanFlipList(board, pos, is_black)
    for (r,c) in canFlipList:
        newBoard[r][c] = this
    return newBoard, canFlipList


def PrintBoard(board):
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                print('  0', end='')
            elif board[i][j] == -1:
                print(f'{TextColor.FAIL} -1{TextColor.ENDC}', end='')
            elif board[i][j] == 1:
                print(f'{TextColor.OKGREEN}  1{TextColor.ENDC}', end='')
            elif board[i][j] == 2:
                print(f'{TextColor.OKBLUE}  2{TextColor.ENDC}', end='')
        print('')
    print('')

def GetStep(board, is_black):
    """
    Example:
    x = random.randint(0, 7)
    y = random.randint(0, 7)
    return (x,y)
    """
    pass

class TextColor:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# while(True):
#     (stop_program, id_package, board, is_black) = STcpClient.GetBoard()
#     if(stop_program):
#         break
#     
#     Step = GetStep(board, is_black)
#     STcpClient.SendStep(id_package, Step)

def GameStart(allCount=100):
    blackWinCount = 0
    whiteWinCount = 0
    evenCount = 0
    for i in range(allCount):
        board = GetInitBoard()
        is_black = True
        while not CheckGameEnd(board):
            if is_black:
                # step = GetRandomStep(board, is_black) # 43
                # step = GetGreedyStep(board, is_black) # 69 
                # step = GetOpennessStep(board, is_black) # 69
                step = GetMinMaxStep(board, is_black) # 42 
            else:
                step = GetRandomStep(board, is_black)
            # PrintBoard(board)
                
            if step:
                UpdateBoard(board, step, is_black)
            is_black = not is_black
        winner = FindWinner(board)
        if winner == 0:
            print(f'game {i}/100, even')
            evenCount += 1
        elif winner == BLACK_NUM:
            print(f'game {i}/100, black win')
            blackWinCount += 1
        else:
            print(f'game {i}/100, white win')
            whiteWinCount += 1
    print(f'black: {blackWinCount/allCount*100}%, white: {whiteWinCount/allCount*100}%, even: {evenCount/allCount*100}%')


if __name__ == "__main__":

    GameStart(allCount=100)
    # board = GetInitBoard()
    # is_black = True
    # UpdateBoard(board, (1,1), is_black)
    # UpdateBoard(board, (1,2), not is_black)
    # PrintBoard(board)
    # UpdateBoard(board, (0,2), is_black)
    # PrintBoard(board)

