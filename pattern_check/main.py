#!/usr/bin/env python
# coding: utf-8

import sys
import datetime
import psycopg2
from chain_info import ChainInfo
from result import Result

user = 'postgres'
dbname = 'pqdb'
password = 'postgres'
conn = psycopg2.connect(" user=" + user +" dbname=" + dbname + " password=" + password)
cur = conn.cursor()


def main():
    # arg = ('pq.py', '5', '1', '10', '6.5', '7', '3')
    # 第1引数 : Nextの色
    # 第2引数 : 盤面パターン
    # 第3引数 : なぞり消し数(max_trace)
    # 第4引数 : 同時消し係数(elimination_coefficient)
    # 第5引数 : 連鎖係数(chain_coefficient)
    # 第6引数 : 最大結合数(max_connection)
    arg = sys.argv
    if not isArgCorrect(arg):
        sys.exit()

    trace_pattern_size = getTracePatternSize(int(arg[3]))
    elimination_coefficient = int(arg[4])
    chain_coefficient_list = getChainCoefficientList(int(arg[5]))
    max_connection = int(arg[6])
    result = Result()
    is_debug_mode = False

    # なぞり消しパターン数だけループ
    for pattern in range(trace_pattern_size):
        puyo_next = initNext(int(arg[1]))
        puyo_board = initBoard(int(arg[2]))
        if pattern % 100000 == 0:
            print(pattern)
            print(str(datetime.datetime.now()))
        trace_pattern = getTracePattern(pattern)
        # なぞりパターンと盤面のお邪魔がかぶっていたら次のパターンへ
            # 今回はりんご盤面なのでお邪魔は存在しない
        # 連鎖情報オブジェクトの生成
        chain_info = ChainInfo(puyo_next, puyo_board, trace_pattern, max_connection, is_debug_mode)
        # ダメージ計算オブジェクトの生成
        
    # 結果表示オブジェクトの生成

def isArgCorrect(arg):
    ret = False
    if len(arg) < 5:
        print("Error : 引数指定が足りない")
    elif not arg[1].isdecimal():
        print("Error : 第1引数(Nextの色)が数値でない")
    elif not ((int(arg[1]) >= 1 and int(arg[1]) <= 5) or (int(arg[1]) == 9)):
        print("Error : 第1引数は1～5 か 9のみ")
    elif not arg[2].isdecimal():
        print("Error : 第2引数(盤面パターン)が数値でない")
    elif not ((int(arg[2]) >= 1 and int(arg[2]) <= 8) or (int(arg[2]) >= 101 and int(arg[2]) <= 116)):
        print("Error : 第2引数は1～8, 101～116のみ")
    elif not arg[3].isdecimal():
        print("Error : 第3引数(なぞり消し係数)が数値でない")
    elif not arg[4].isdecimal():
        print("Error : 第4引数(同時消し係数)が数値でない")
    elif not arg[5].isdecimal():
        print("Error : 第5引数(連鎖係数)が数値でない")
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

def getChainCoefficientList(chain_coefficient):
    if chain_coefficient == 1:
        ret = [1, 1.4, 1.7, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4]
    elif chain_coefficient == 4:
        ret = [1, 2.6, 3.8, 5.0, 5.8, 6.6, 7.4, 8.2, 9.0, 9.8, 10.6, 11.4, 12.2, 13.0, 13.8, 14.6]
    elif chain_coefficient == 5:
        ret = [1, 3.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0]
    elif chain_coefficient == 6:
        ret = [1, 3.4, 5.2, 7.0, 8.2, 9.4, 10.6, 11.8, 13.0, 14.2, 15.4, 16.6, 17.8, 19.0, 20.2, 21.4]
    elif chain_coefficient == 7:
        ret = [1, 3.8, 5.9, 8.0, 9.4, 10.8, 12.2, 13.6, 15.0, 16.4, 17.8, 19.2, 20.6, 22.0, 23.4, 24.8]
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


def getTracePattern(pattern):
    # TODO:pattern+1からpattern+10万までを一括で取得するように変更する
    cur.execute('SELECT board FROM pattern WHERE id = %s', (pattern+1,))
    trace_pattern = list(list(cur.fetchone())[0])
    return trace_pattern


if __name__ == '__main__':
    main()