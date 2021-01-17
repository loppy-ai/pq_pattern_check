#!/usr/bin/env python
# coding: utf-8

import sys
sys.dont_write_bytecode = True
import datetime
import psycopg2
import time
import numpy as np
from chain_info import ChainInfo
from damage_info import DamageInfo
from display_chain_result import display_settings, display_chain_result

user = 'postgres'
dbname = 'pqdb'
password = 'postgres'
conn = psycopg2.connect(" user=" + user +" dbname=" + dbname + " password=" + password)
cur = conn.cursor()


def search_optimal_fixed_board():
    start_time = time.time()
    # arg = ('pq.py', '5', '1', '10', '6.5', '7', '3')
    # 第1引数 : Nextの色(next_color)
    # 第2引数 : 盤面パターン(board_pattern)
    # 第3引数 : なぞり消し数(max_trace)
    # 第4引数 : 同時消し係数(elimination_coefficient)
    # 第5引数 : 連鎖係数(chain_coefficient)
    # 第6引数 : 最大結合数(max_connection)
    arg = sys.argv
    if not isArgCorrect(arg):
        sys.exit()

    next_color = int(arg[1])
    board_pattern = int(arg[2])
    max_trace = int(arg[3])
    elimination_coefficient = int(arg[4])
    chain_coefficient = int(arg[5])
    max_connection = int(arg[6])
    
    trace_pattern_size = getTracePatternSize(max_trace)
    now_max_magnification = 0
    is_debug_mode = False
    frequency = 10000
    count = 0

    # なぞり消しパターン数だけループ
    print("-------------------処理開始時間-------------------")
    for pattern in range(-(-trace_pattern_size // frequency)):  # 切り上げ
        print(str(pattern * frequency).rjust(9) + "～" + str((pattern+1)*frequency).rjust(9) + " : " + str(datetime.datetime.now()))
        cur = getTracePattern(pattern*frequency, frequency, trace_pattern_size)
        for row in cur:
            count += 1
            trace_pattern = list(list(row)[0])
            puyo_next = initNext(int(arg[1]))
            puyo_board = initBoard(int(arg[2]))
            # なぞりパターンと盤面のお邪魔がかぶっていたら次のパターンへ
                # 今回はりんご/もあクル盤面なのでお邪魔は存在しない
            # 連鎖情報インスタンスの生成
            chain_info = ChainInfo(puyo_next, puyo_board, trace_pattern, max_connection, is_debug_mode)
            chain_result = chain_info.getChainResult()
            # ダメージ計算インスタンスの生成
            damage_info = DamageInfo(chain_result, elimination_coefficient, chain_coefficient, max_connection)

            # 最適解を見つけるための条件設定
                # print("紫の消去数 : " + str(damage_info.getNumOfElimination(5)))
                # print("全ぷよの消去数 : " + str(damage_info.getAllColorPuyoNumOfElimination()))
                # print("お邪魔の消去数 : " + str(damage_info.getAllOjamaPuyoNumOfElimination()))
                # print("チャンスぷよ生成 : " + str(damage_info.canMakeChancePuyo()))
                # print("紫の倍率 : " + str(damage_info.getMagnificationByColor(5)))
                # print("ワイルドの倍率 : " + str(damage_info.getMagnificationByColor(9)))
            # ある色の最大倍率を求める
            magnification = damage_info.getMagnificationByColor(next_color)
            if now_max_magnification < magnification:
                now_max_magnification = magnification
                now_max_pattern = trace_pattern

            del chain_info
            del damage_info

    elapsed_time = time.time() - start_time
    print("")
    print("-------------------合計処理時間-------------------")
    print(datetime.timedelta(seconds=elapsed_time))
    print("")

    # 結果表示
    puyo_next = initNext(int(arg[1]))
    puyo_board = initBoard(int(arg[2]))
    is_process_print = False
    display_settings(next_color, board_pattern, max_trace, elimination_coefficient, chain_coefficient, max_connection, now_max_pattern)
    display_chain_result(puyo_next, puyo_board, max_trace, elimination_coefficient, chain_coefficient, max_connection, now_max_pattern, is_process_print)

    # 終了処理
    cur.close()
    conn.close()


def isArgCorrect(arg):
    ret = False
    if len(arg) < 5:
        print("Error : 引数指定が足りない")
    elif not arg[1].isdecimal():
        print("Error : 第1引数(Nextの色)が数値でない")
    elif not ((int(arg[1]) >= 1 and int(arg[1]) <= 5) or (int(arg[1]) == 9)):
        print("Error : 第1引数は1～5か9のみ")
    elif not arg[2].isdecimal():
        print("Error : 第2引数(盤面パターン)が数値でない")
    elif not ((int(arg[2]) >= 1 and int(arg[2]) <= 8) or (int(arg[2]) >= 101 and int(arg[2]) <= 116)):
        print("Error : 第2引数は1～8, 101～116のみ")
    elif not arg[3].isdecimal():
        print("Error : 第3引数(なぞり消し数)が数値でない")
    elif not arg[4].isdecimal():
        print("Error : 第4引数(同時消し係数)が数値でない")
    elif not arg[5].isdecimal():
        print("Error : 第5引数(連鎖係数)が数値でない")
    elif not ((int(arg[5]) >= 4 and int(arg[5]) <= 7) or (int(arg[5]) == 1)):
        print("Error : 第5引数は1か4～7のみ")
    elif not arg[6].isdecimal():
        print("Error : 第6引数(最大結合数)が数値でない")
    else:
        ret = True
    return ret


def getTracePatternSize(max_trace):
    # max_traceの数に応じて、なぞりパターン数が決まる
    # 固定値であり、毎回DBに確認しに行くと時間がかかりそうなので、あらかじめ調べておく
    # 1なら48、2なら200、…、13なら？？？
    if max_trace == 1:
        ret = 48
    elif max_trace == 2:
        ret = 200
    elif max_trace == 3:
        ret = 804
    elif max_trace == 4:
        ret = 3435
    elif max_trace == 5:
        ret = 15359
    elif max_trace == 6:
        ret = 70147
    elif max_trace == 7:
        ret = 320111
    elif max_trace == 8:
        ret = 1438335
    elif max_trace == 9:
        ret = 6300691
    elif max_trace == 10:
        ret = 26702013
    return ret


def initNext(next_color_no):
    return [next_color_no] * 8


def initBoard(board_pattern_no):
    if board_pattern_no == 1:    # 15連鎖（全消し）
        ret = [1,5,8,5,4,3,4,4,1,4,5,8,4,3,5,3,2,4,3,2,8,4,3,5,2,1,2,1,5,2,1,5,4,3,5,5,1,2,3,3,2,3,2,1,2,4,1,1]
    elif board_pattern_no == 2:  # 15連鎖（全消し）
        ret = [4,5,1,2,1,4,3,2,5,3,2,5,4,2,3,2,5,4,1,2,1,4,4,1,8,8,5,3,2,5,1,4,4,3,5,3,2,5,1,8,3,1,3,1,5,3,2,4]
    elif board_pattern_no == 3:  # 15連鎖（全消し）
        ret = [3,1,2,4,5,1,5,8,2,4,5,1,2,3,4,3,2,4,5,1,2,3,4,3,4,5,1,2,3,4,3,8,2,1,2,4,5,1,5,8,3,3,1,2,4,5,1,5]
    elif board_pattern_no == 4:  # 14連鎖（全消し可能）
        ret = [1,5,4,5,8,3,8,1,5,1,3,1,4,5,2,8,3,3,4,4,2,2,1,1,5,2,5,5,3,3,4,5,5,2,1,2,1,1,5,4,1,1,2,1,2,2,3,4]
    elif board_pattern_no == 5:  # 14連鎖
        ret = [2,8,3,5,1,2,4,2,8,3,1,3,5,1,4,3,4,1,4,4,3,5,2,3,5,4,3,3,4,4,1,4,1,2,1,4,3,5,5,3,2,8,2,1,1,3,3,5]
    elif board_pattern_no == 6:  # 14連鎖
        ret = [4,3,5,1,4,2,8,4,3,1,1,2,2,8,8,2,3,2,5,3,4,1,5,4,4,4,2,5,3,4,1,5,5,2,1,3,2,1,3,5,1,1,2,2,3,3,4,4]
    elif board_pattern_no == 7:  # 13連鎖
        ret = [5,2,4,4,8,4,3,3,4,8,2,5,4,5,1,1,2,3,4,2,5,1,3,2,3,1,3,1,2,3,2,8,1,4,5,1,2,5,2,3,1,4,1,5,5,3,1,3]
    elif board_pattern_no == 8:  # 13連鎖
        ret = [1,3,2,1,5,2,8,2,5,4,2,1,4,5,4,5,8,5,5,2,1,1,4,5,4,3,4,3,5,3,1,2,4,3,4,3,1,4,2,8,3,4,3,5,3,3,5,2]
    elif board_pattern_no == 101: # 11連鎖
        ret = [1,8,8,1,1,3,5,2,1,1,5,8,8,1,3,3,3,3,1,4,1,3,5,5,3,4,3,2,4,4,1,5,2,2,2,1,1,1,4,2,4,4,4,5,5,5,2,2]
    elif board_pattern_no == 102: # 11連鎖
        ret = [4,3,5,8,8,1,8,2,2,3,5,2,1,8,2,2,5,5,2,1,1,2,5,5,3,3,1,2,2,5,4,5,2,4,1,1,3,4,3,4,2,2,4,4,1,3,3,4]
    elif board_pattern_no == 103: # 11連鎖
        ret = [2,5,5,1,8,1,1,3,5,2,2,2,1,8,8,4,5,1,3,4,5,2,5,8,1,3,4,5,2,5,3,4,1,3,4,5,2,5,3,4,1,3,4,5,2,5,3,4]
    elif board_pattern_no == 104: # 11連鎖
        ret = [8,8,5,4,3,3,2,1,1,5,5,4,3,2,1,8,5,4,4,3,2,2,1,1,1,2,3,1,8,4,5,4,1,1,3,1,1,5,4,4,2,2,2,3,3,1,5,5]
    elif board_pattern_no == 105: # 11連鎖
        ret = [5,1,8,4,8,3,2,5,5,4,4,2,3,2,3,5,1,1,4,8,4,1,4,5,1,2,3,1,2,4,5,4,5,5,2,3,3,4,3,4,2,2,3,1,1,4,1,4]
    elif board_pattern_no == 106: # 11連鎖
        ret = [8,4,8,8,1,2,2,3,5,4,1,3,8,1,1,1,5,4,2,5,5,3,2,2,4,5,3,3,3,5,4,3,1,5,2,2,2,5,3,3,1,1,3,3,3,4,4,4]
    elif board_pattern_no == 107: # 11連鎖
        ret = [5,5,5,8,3,4,3,3,3,2,3,5,4,8,8,8,3,3,1,4,4,2,3,3,1,1,2,1,3,3,2,5,1,2,1,4,3,4,2,2,2,1,1,4,4,5,5,5]
    elif board_pattern_no == 108: # 11連鎖
        ret = [2,2,8,3,4,3,5,4,4,4,2,2,8,4,4,8,4,8,4,5,3,4,5,5,1,3,1,2,5,5,1,5,1,1,3,1,1,1,4,4,3,3,5,2,2,2,3,4]
    elif board_pattern_no == 109: # 11連鎖
        ret = [4,3,3,5,3,8,2,1,5,1,2,5,4,2,3,3,1,2,5,8,2,3,1,3,5,1,2,5,2,1,4,1,5,1,2,3,5,4,8,4,5,4,4,4,8,5,5,5]
    elif board_pattern_no == 110: # 11連鎖
        ret = [1,3,2,4,3,8,5,8,1,3,2,4,3,2,1,8,4,4,5,5,1,2,5,5,5,5,1,1,8,1,5,1,4,1,3,2,4,3,3,1,4,1,3,2,4,2,2,1]
    elif board_pattern_no == 111: # 10連鎖 8個同時消し
        ret = [4,8,1,2,3,4,4,2,5,2,2,8,1,4,3,5,1,1,2,1,2,5,2,3,5,3,3,3,4,2,5,3,5,1,1,1,2,5,8,3,5,4,4,4,8,2,2,2]
    elif board_pattern_no == 112: # 10連鎖 8個同時消し
        ret = [1,4,2,5,5,3,1,8,8,1,4,4,5,3,1,4,1,4,2,2,2,5,3,1,1,4,8,3,4,4,3,1,3,3,3,2,5,4,5,4,2,2,2,4,5,5,4,4]
    elif board_pattern_no == 113: # 10連鎖 8個同時消し
        ret = [3,3,3,1,2,2,5,8,2,1,5,3,4,4,8,5,3,3,3,8,4,1,8,5,5,5,5,4,1,3,2,5,1,1,1,4,1,3,4,2,2,2,2,3,4,4,3,3]
    elif board_pattern_no == 114: # 10連鎖 8個同時消し
        ret = [1,8,5,8,2,3,2,4,2,2,5,4,2,3,2,8,5,5,2,2,3,2,3,4,2,3,3,4,1,2,4,4,2,1,8,4,5,1,1,1,1,1,3,3,4,5,5,5]
    elif board_pattern_no == 115: # 9連鎖 12個同時消し
        ret = [3,4,4,5,2,2,2,3,5,5,5,2,3,3,3,8,4,4,1,3,1,1,1,8,3,3,3,4,2,2,2,1,8,1,1,1,5,5,5,2,8,4,4,4,3,3,3,5]
    elif board_pattern_no == 116: # 9連鎖 12個同時消し
        ret = [2,5,8,4,2,2,1,8,3,4,4,2,8,2,4,1,5,5,5,4,5,5,4,1,3,3,1,3,2,5,4,1,3,2,2,1,3,2,5,4,2,1,1,3,3,2,2,4]
    return ret


def getTracePattern(pattern, frequency, trace_pattern_size):
    if (pattern + frequency) > trace_pattern_size:
        # 余り部分だけを取得
        cur.execute('SELECT board FROM pattern WHERE id BETWEEN %s AND %s', (pattern+1, trace_pattern_size))
    else:
        # pattern+1からpattern+1+frequencyまで(つまりfrequency行)を一括で取得する
        cur.execute('SELECT board FROM pattern WHERE id BETWEEN %s AND %s', (pattern+1, pattern+frequency))
    return cur


if __name__ == '__main__':
    search_optimal_fixed_board()