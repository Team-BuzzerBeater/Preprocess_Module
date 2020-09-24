import os
import numpy as np
import itertools
import sys
import math

def isWord(line, word):
    if (len(line) > len(word)) and line[0:len(word)] == word:
        return True
    else:
        return False

def getPrec(line, word):
    line = line.replace(" ", "")
    prec = line.split(word+':')[1].split('%')[0]
    return prec

def getFPS(line):
    line = line.replace(" ", "")
    fps = line.split('FPS:')[1].split('AVG')[0]
    return fps

def getLoc(line):
    line = line.replace(" ", "")
    left_x = line.split('left_x:')[1].split('top_y')[0]
    top_y = line.split('top_y:')[1].split('width')[0]
    width = line.split('width:')[1].split('height')[0]
    height = line.split('height:')[1].split(')')[0]
    return left_x, top_y, width, height

def getRealLoc(list):
    width = float(list[0][2])
    height = float(list[0][3])
    x = float(list[0][0]) + (1 / 2 * width)
    y = float(list[0][1]) - (1 / 2 * height)

    return x, y, width, height

def getTriangleArea(first, second, third):
    dist1 = np.sqrt((first[0] - second[0])**2 + (first[1] - second[1])**2)
    dist2 = np.sqrt((second[0] - third[0])**2 + (second[1] - third[1])**2)
    dist3 = np.sqrt((third[0] - first[0])**2 + (third[1] - first[1])**2)

    s = (dist1 + dist2 + dist3) / 2
    area = (s*(s-dist1)*(s-dist2)*(s-dist3)) ** 0.5
    return area

def getEuclidean(first, second):
    return np.sqrt((float(first[0]) - float(second[0]))**2 + (float(first[1]) - float(second[1]))**2)

# get '~.txt' files on path
path = "./"
file_list = os.listdir(path)
file_list_txt = [file for file in file_list if file.endswith(".txt")]

print(file_list_txt)
r = open(file_list_txt[0], mode='r', encoding='utf-8')
switch = 0


print("************   Start   ************")
while True:
    line = r.readline()

    if not line: break

    while not isWord(line, 'FPS'):
        line = r.readline()

        if not line: break

    # get FPS
    if not line:
        break
    fps = getFPS(line)
    check_gp = False
    check_ball = False
    gpInfo = []
    ballInfo = []
    playerInfo = []

    if fps is None: break

    print('\nfps :', fps)
    line = r.readline()
    line = r.readline()

    while True:
        # fps 한 단락의 시작 의미
        line = r.readline()

        if line == "\n":
            # fps 한 단락의 끝 의미
            break

        elif isWord(line, 'player'):
            playerInfo.append(getLoc(line))

        elif isWord(line, 'goalpost'):
            # get goalpost precision
            goalpost = getPrec(line, 'goalpost')
            if goalpost is not None:
                check_gp = True
                gpInfo.append(getLoc(line))

        elif isWord(line, 'ball'):
            # get Ball precision
            ball = getPrec(line, 'ball')
            if ball is not None:
                check_ball = True
                ballInfo.append(getLoc(line))

    # 공과 골대를 찾은 경우
    if(check_ball and check_gp):
        # print("ball precision :", ball)
        # print("gopo precision :", goalpost)
        # print('plyr location :', playerInfo)
        # print('gopo location :', gpInfo)
        # print('ball location :', ballInfo)

        # 공과 골대의 중심좌표, width, height 구하기
        b_x, b_y, b_w, b_h = getRealLoc(ballInfo)
        gp_x, gp_y, gp_w, gp_h = getRealLoc(gpInfo)
        playerList = []

        for i in playerInfo:
            playerList.append(getRealLoc([i]))
        # print('공의 중심좌표 :', b_x, b_y, b_w, b_h)
        # print('골대 중심좌표 :', gp_x, gp_y, gp_w, gp_h)
        # print('선수 중심좌표 :', playerList)

        '''
         1. 공과 골대간의 유클리드 거리
        '''
        distance = np.sqrt((b_x - gp_x)**2 + (b_y - gp_y)**2)
        print('1. distance :', distance)

        '''
        2. 공과 골대간의 선수 명수
        '''
        obstacle = 0

        # 공과 골대로 삼각형 만들어 최대 크기의 삼각형을 이루는 골대의 두 점 선택
        gp_left_top_x = gp_x - (1 / 2 * gp_w)
        gp_left_top_y = gp_y + (1 / 2 * gp_h)

        gp_right_top_x = gp_x + (1 / 2 * gp_w)
        gp_right_top_y = gp_y + (1 / 2 * gp_h)

        gp_left_bot_x = gp_x - (1 / 2 * gp_w)
        gp_left_bot_y = gp_y - (1 / 2 * gp_h)

        gp_right_bot_x = gp_x + (1 / 2 * gp_w)
        gp_right_bot_y = gp_y - (1 / 2 * gp_h)

        gp_loc_list = []
        gp_loc_list.append([gp_left_top_x, gp_left_top_y])
        gp_loc_list.append([gp_right_top_x, gp_right_top_y])
        gp_loc_list.append([gp_left_bot_x, gp_left_bot_y])
        gp_loc_list.append([gp_right_bot_x, gp_right_bot_y])
        # print('골대 4개 꼭짓점 :', gp_loc_list)

        combi_list = itertools.combinations(gp_loc_list, 2)
        triangleMaxArea = 0
        gpMax1_x, gpMax1_y = 0, 0
        gpMax2_x, gpMax2_y = 0, 0

        for first, second in combi_list:
            area = getTriangleArea(first, second, [b_x, b_y])
            if area > triangleMaxArea:
                triangleMaxArea = area
                gpMax1_x, gpMax1_y = first[0], first[1]
                gpMax2_x, gpMax2_y = second[0], second[1]
        # print('선택된 골대 꼭짓점 :', gpMax1_x, gpMax1_y, gpMax2_x, gpMax2_y)

        for p_x, p_y, p_w, p_h in playerList:
            # print('선수 중심좌표 :', p_x, p_y, p_w, p_h)

            first_term = np.array([gpMax1_x - b_x, gpMax1_y - b_y])
            second_term = np.array([gpMax2_x - b_x, gpMax2_y - b_y])
            third_term = np.array([b_x - float(p_x), b_y - float(p_y)])

            cross1 = np.cross(first_term, third_term)
            cross2 = np.cross(second_term, third_term)

            result = np.dot(cross1, cross2)

            if result < 0:
                obstacle = obstacle + 1
                # print('삼각형에 포함된 선수 중심좌표 :', p_x, p_y)

        print('2. obstacle :', obstacle)

        '''
        3. 공 근처의 선수 명 수
        '''
        threshold = 100
        disturbance = 0
        for p_x, p_y, p_w, p_h in playerList:
            dist = getEuclidean([b_x, b_y], [p_x, p_y])
            # print('공과 선수간의 거리 :', dist)
            if dist < threshold:
                disturbance = disturbance + 1
        print('3. disturbance :', disturbance)

        '''
        4. 공과 선수들의 유클리드 거리 역수 총합
        '''
        concentration = 0
        for p_x, p_y, p_w, p_h in playerList:
            dist = getEuclidean([b_x, b_y], [p_x, p_y]) + sys.float_info.epsilon
            dist = 1 / dist
            concentration = concentration + dist
        print('4. concentration :', concentration)

        '''
        5. 공 진행방향에 대한 선수들의 방해도
        '''
        d_list = gp_loc_list
        d_list.append([gp_x, gp_y])

        interference = 0
        obstacle_candidates = []
        first_term = np.array([gp_x - b_x, gp_y - b_y])
        for p_x, p_y, p_w, p_h in playerList:
            second_term = np.array([p_x - b_x, p_y - b_y])
            result = np.cross(first_term, second_term)
            if result <= 0:
                obstacle_candidates.append([p_x, p_y])

        self_epsilon = 1

        for p in obstacle_candidates:
            p_x, p_y = p[0], p[1]
            theta_list = []

            for d in d_list:
                alpha, beta = d[0], d[1]

                numerator = np.dot([alpha - b_x, beta - b_y], [p_x - b_x, p_y - b_y])
                denominator = (getEuclidean([alpha, beta], [b_x, b_y]) * getEuclidean([p_x, p_y], [b_x, b_y]))
                theta = numerator / denominator
                theta_list.append(math.acos(theta))

            for theta in theta_list:
                denominator = getEuclidean([p_x, p_y], [b_x, b_y]) * math.sin(theta) + self_epsilon
                interference = interference + (1 / denominator)

        print('5. interference :', interference)
        break

if not (check_ball and check_gp):
    if not check_ball:
        print("***********************************")
        print("*                                 *")
        print("*   [ERROR] There's no ball.      *")
        print("*                                 *")
        print("***********************************")
    else:
        print("***********************************")
        print("*                                 *")
        print("*   [ERROR] There's no goalpost.  *")
        print("*                                 *")
        print("***********************************")

print("************   Finish   ************")
r.close()