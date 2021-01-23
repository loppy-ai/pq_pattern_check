#!/usr/bin/env python
# coding: utf-8

import sys
sys.dont_write_bytecode = True
from chain_info import ChainInfo
from damage_info import DamageInfo

def main():
    # ユーザ指定部分
    next_color              = 5     # ネクストの色
    board_pattern           = 8     # 盤面パターン
    max_trace               = 10    # 最大なぞり消し数（表示するだけ）
    elimination_coefficient = 6.5   # 同時消し係数
    chain_coefficient       = 7     # 連鎖係数
    max_connection          = 3     # 消えるときの結合数
    is_process_print        = True # 連鎖過程の表示有無
    trace_pattern = [               # なぞり消しパターン
        1, 0, 0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 0, 1, 0,
        1, 0, 0, 1, 0, 0, 1, 0,
        1, 0, 0, 0, 1, 0, 1, 0,
        0, 0, 0, 1, 0, 1, 1, 0,
        0, 0, 0, 1, 0, 0, 0, 0
    ]
    '''
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0
    '''

    from search_optimal_fixed_board import initNext, initBoard
    puyo_next = initNext(next_color)
    puyo_board = initBoard(board_pattern)
    pattern = [str(i) for i in trace_pattern]
    display_settings(next_color, board_pattern, max_trace, elimination_coefficient, chain_coefficient, max_connection, trace_pattern)
    display_chain_result(puyo_next, puyo_board, max_trace, elimination_coefficient, chain_coefficient, max_connection, pattern, is_process_print)

def display_settings(next_color, board_pattern, max_trace, elimination_coefficient, chain_coefficient, max_connection, pattern):
    print("---------------------設定情報---------------------")
    print("ネクストの色       : " + str(next_color))
    print("盤面パターン       : " + str(board_pattern))
    print("最大なぞり消し数   : " + str(max_trace))
    print("同時消し係数       : " + str(elimination_coefficient))
    print("連鎖係数           : " + str(chain_coefficient))
    print("消えるときの結合数 : " + str(max_connection))
    print("なぞり消しパターン : ")
    for i in range(5):
        print(str(pattern[i*8]) + ", " + str(pattern[i*8+1]) + ", " + str(pattern[i*8+2]) + ", " + str(pattern[i*8+3]) + ", " + str(pattern[i*8+4]) + ", " + str(pattern[i*8+5]) + ", " + str(pattern[i*8+6]) + ", " + str(pattern[i*8+7]) + ",")
    print(str(pattern[40]) + ", " + str(pattern[41]) + ", " + str(pattern[42]) + ", " + str(pattern[43]) + ", " + str(pattern[44]) + ", " + str(pattern[45]) + ", " + str(pattern[46]) + ", " + str(pattern[47]))


def display_chain_result(puyo_next, puyo_board, max_trace, elimination_coefficient, chain_coefficient, max_connection, pattern, is_process_print):
    if is_process_print:
        print("")
        print("---------------------連鎖過程---------------------")
    chain_info = ChainInfo(puyo_next, puyo_board, pattern, max_connection, is_process_print)
    chain_result = chain_info.getChainResult()
    damage_info = DamageInfo(chain_result, elimination_coefficient, chain_coefficient, max_connection)
    
    red_elimi = damage_info.getNumOfElimination(1)
    blue_elimi = damage_info.getNumOfElimination(2)
    green_elimi = damage_info.getNumOfElimination(3)
    yellow_elimi = damage_info.getNumOfElimination(4)
    purple_elimi = damage_info.getNumOfElimination(5)
    wild_elimi = damage_info.getAllColorPuyoNumOfElimination()
    ojama_elimi = damage_info.getAllOjamaPuyoNumOfElimination()
    heart_elimi = damage_info.getHeartNumOfElimination()

    red_magni = damage_info.getMagnificationByColor(1)
    blue_magni = damage_info.getMagnificationByColor(2)
    green_magni = damage_info.getMagnificationByColor(3)
    yellow_magni = damage_info.getMagnificationByColor(4)
    purple_magni = damage_info.getMagnificationByColor(5)
    wild_magni = damage_info.getMagnificationByColor(9)
    heart_magni = damage_info.getMagnificationHeart()

    print("")
    print("---------------------連鎖情報---------------------")
    print("----------------------------------")
    print("   色   |消去数|  倍率  |ペア倍率")
    print("----------------------------------")
    print("   赤   |" + str(red_elimi).rjust(6) + "|" + str('{:.2f}'.format(red_magni)).rjust(8) + "|" + str('{:.2f}'.format(red_magni*5.5)).rjust(8))
    print("   青   |" + str(blue_elimi).rjust(6) + "|" + str('{:.2f}'.format(blue_magni)).rjust(8) + "|   --")
    print("   緑   |" + str(green_elimi).rjust(6) + "|" + str('{:.2f}'.format(green_magni)).rjust(8) + "|   --")
    print("   黄   |" + str(yellow_elimi).rjust(6) + "|" + str('{:.2f}'.format(yellow_magni)).rjust(8) + "|   --")
    print("   紫   |" + str(purple_elimi).rjust(6) + "|" + str('{:.2f}'.format(purple_magni)).rjust(8) + "|" + str('{:.2f}'.format(purple_magni*5.5)).rjust(8))
    print("ワイルド|" + str(wild_elimi).rjust(6) + "|" + str('{:.2f}'.format(wild_magni)).rjust(8) + "|   --")
    print("  邪固  |" + str(ojama_elimi).rjust(6)+ "|   --   |   --")
    print(" ハート |" + str(heart_elimi).rjust(6)+ "|" + str('{:.2f}'.format(heart_magni)).rjust(8) + "|   --")
    print("----------------------------------")
    if damage_info.canMakeChancePuyo():
        print("チャンスぷよ : 生成される")
    else:
        print("チャンスぷよ : 生成されない")


if __name__ == '__main__':
    main()