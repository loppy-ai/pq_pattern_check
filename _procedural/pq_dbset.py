#!/usr/bin/env python
# coding: utf-8

# In[8]:


import copy
import psycopg2
from psycopg2.extras import execute_values
import datetime
all_count = 0

user = 'postgres'
dbname = 'pqdb'
password = 'postgres'
conn = psycopg2.connect(" user=" + user +" dbname=" + dbname + " password=" + password)
cur = conn.cursor()


# In[9]:


# メイン処理
def main():
    global all_count
    board = [0] * 48
    max_trace = 12
    now_trace = 1
    nest_level = 0
    dt_now = datetime.datetime.now()
    print(str(max_trace) + '個の場合のDB登録開始')
    print('開始日時:' + str(dt_now))
    
    all_count = 0  # 1つ前の合計からスタートする
    
    for i in range(max_trace, max_trace+1):
        joined_board = []
        joined_board = checkBoard(nest_level, now_trace, board, i, joined_board)
        # ここでDB登録
        # print(joined_board)
        
        ## 10個以上の場合、文字列が長くなりすぎてバッファが足りずに（1.3GB？）落ちる
        # insert_query = 'INSERT INTO pattern (id, trace, board) VALUES %s'
        # ret = execute_values (cur, insert_query, joined_board, template=None, page_size=len(joined_board))
        # conn.commit()
        # print(str(i) +'個の場合のDB登録完了 (累計件数:'+ str(all_count) +')')
        # dt_now = datetime.datetime.now()
        # print('完了日時:' + str(dt_now))
        # print(' ')
        
        # 10000件の余り分の登録
        if len(joined_board) != 0:
            insert_query = 'INSERT INTO pattern12 (id, trace, board) VALUES %s'
            ret = execute_values (cur, insert_query, joined_board, template=None, page_size=len(joined_board))
            conn.commit()
            print(str(i) + '個の場合のDB登録完了 (累計件数:'+ str(all_count) +')')
            dt_now = datetime.datetime.now()
            print('完了日時:' + str(dt_now))
        
    cur.close()
    conn.close()


# In[10]:


# 組み合わせ探索
def checkBoard(nest_level, now_trace, board, max_trace, joined_board):
    global all_count
    for i in range(nest_level, len(board)-(max_trace-now_trace)):
        nest_level += 1
        board[i] = 1
        if now_trace != max_trace:
            # 組み合わせ探索を継続
            now_trace += 1
            joined_board = checkBoard(nest_level, now_trace, board, max_trace, joined_board)
            now_trace -= 1
        else:
            if max_trace == 1:
                all_count += 1
                tmp_board = []
                tmp_board.append(all_count)
                tmp_board.append(max_trace)
                tmp_board.append("".join(map(str, board)))
                joined_board.append(tmp_board)
            if max_trace >= 2:
                # 結合チェック（他の1とつながっているか？）
                if isCombined(board, max_trace) == True:
                    all_count += 1
                    tmp_board = []
                    tmp_board.append(all_count)
                    tmp_board.append(max_trace)
                    tmp_board.append("".join(map(str, board)))
                    joined_board.append(tmp_board)
                    # 100000件ずつ登録
                    if all_count % 100000 == 0:
                        print(all_count)
                        insert_query = 'INSERT INTO pattern12 (id, trace, board) VALUES %s'
                        ret = execute_values (cur, insert_query, joined_board, template=None, page_size=len(joined_board))
                        conn.commit()
                        joined_board = []
        board[i] = 0
    return joined_board


# In[11]:


# 結合チェック
def isCombined(board, max_trace):
    for i in range(len(board)):
        if board[i] == 1:
            # 結合チェック
            count = 1
            check_board = copy.copy(board)
            check_board, count = isCombinatedIndividual(check_board, i, count, max_trace)
            if count == max_trace:
                return True
            else:
                return False


# In[12]:


# 結合チェック
def isCombinatedIndividual(board, i, count, max_trace):
    board[i] = 2
    if i % 8 != 0 and board[i-1] == 1:
        # 左にいける
        board, count = isCombinatedIndividual(board, i-1, count+1, max_trace)
    if i % 8 != 0 and i >= 8 and board[i-9] == 1:
        # 左上にいける
        board, count = isCombinatedIndividual(board, i-9, count+1, max_trace)
    if i >= 8 and board[i-8] == 1:
        # 上にいける
        board, count = isCombinatedIndividual(board, i-8, count+1, max_trace)
    if i % 8 != 7 and i >= 8 and board[i-7] == 1:
        # 右上にいける
        board, count = isCombinatedIndividual(board, i-7, count+1, max_trace)
    if i % 8 != 7 and board[i+1] == 1:
        # 右にいける
        board, count = isCombinatedIndividual(board, i+1, count+1, max_trace)
    if i < 40 and i % 8 != 7 and board[i+9] == 1:
        # 右下にいける
        board, count = isCombinatedIndividual(board, i+9, count+1, max_trace)
    if i < 40 and board[i+8] == 1:
        # 下にいける
        board, count = isCombinatedIndividual(board, i+8, count+1, max_trace)
    if i % 8 != 0 and i < 40 and board[i+7] == 1:
        # 左下にいける
        board, count = isCombinatedIndividual(board, i+7, count+1, max_trace)
    return board, count


# In[13]:


# デバッグ用出力
def debug(max_trace, board):
    print('max_trace:' + str(max_trace))
    print(board[0:8])
    print(board[8:16])
    print(board[16:24])
    print(board[24:32])
    print(board[32:40])
    print(board[40:48])
    print(' ')


# In[14]:


if __name__ == '__main__':
    main()

