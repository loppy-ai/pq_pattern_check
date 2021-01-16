#!/usr/bin/env python
# coding: utf-8

# In[17]:


import sys
import psycopg2
import datetime

user = 'postgres'
dbname = 'pqdb'
password = 'postgres'
conn = psycopg2.connect(" user=" + user +" dbname=" + dbname + " password=" + password)
cur = conn.cursor()

# In[18]:


# メイン処理
def main():
    arg = sys.argv
    # arg = ('pq.py', '5', '1')
    max_trace = 10 # 最大なぞり消し
    elimination_coefficient = 6.5  # 同時消し係数（蒸気すずらん）
    # chain_coefficient = 7  # 連鎖係数（★7あんどうりんご FP）
    chain_coefficient = 1  # 連鎖係数（通常）
    # chain_coefficient_list = [1, 3.8, 5.9, 8, 9.4, 10.8, 12.2, 13.6, 15, 16.4, 17.8, 19.2, 20.6, 22, 23.4, 24.8]  # その時の連鎖係数
    chain_coefficient_list = [1, 1.4, 1.7, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4]  # その時の連鎖係数

    # 引数チェック
    checkArg(arg)
    # debug('initBoard', puyo_board, puyo_next) # debug
    # なぞりパターン総数取得
    trace_pattern_size = getTracePatternSize(max_trace)
    # 結果保持
    # 赤倍率, 青倍率, 緑倍率, 黄倍率, 紫倍率, ワ倍率, 赤パ, 青パ, 緑パ, 黄パ, 紫パ, ワパ
    result = [0] * 12
    
    # なぞりパターン数だけループする
    for pattern in range(trace_pattern_size):
        if pattern % 1000000 == 0:
            print(pattern)
            dt_now = datetime.datetime.now()
            print(str(dt_now))
        # ネクスト設定
        puyo_next = initNext(int(arg[1]))
        # 盤面設定
        puyo_board = initBoard(int(arg[2]))
        # pattern+1番目のパターンを取得
        trace_pattern = getTracePattern(pattern+1)
        # なぞりパターンと盤面のお邪魔がかぶっていたら次のパターンへ
            # 今回はりんご盤面なのでお邪魔は存在しない
        # 盤面に対してなぞりパターンを適用
        puyo_board = applyTracePattern(puyo_board, trace_pattern)
        # debug('applyedTracePattern', puyo_board, puyo_next) # debug
        # 消えた部分を落とす
        puyo_board = dropBoard(puyo_board)
        # debug('dropBoard', puyo_board, puyo_next) # debug
        
        # 連鎖終了までループする
        isChaining = True
        # 連鎖情報
        all_chain_info = []
        # 連鎖数
        chain_count = 0
        
        while (isChaining):
            # 連鎖数, 赤個, 青個, 緑個, 黄個, 紫個, 邪個, 固個, ハ個, プ個, 赤分, 青分, 緑分, 黄分, 紫分
            chain_info = [0] * 15
            # 結合チェック
            puyo_board, chain_info = checkConnection(puyo_board, chain_info)
            # ぷよが消えた
            if 0 in puyo_board:
                # れんさ！++
                chain_count += 1 
                chain_info[0] = chain_count
                puyo_board = dropBoard(puyo_board)
                # debugChain(chain_info) # debug
                # debug('chaining', puyo_board, puyo_next) # debug
                all_chain_info.append(chain_info)
            # 消えなかった
            else:
                # nextを落とす
                puyo_board, puyo_next, next_drop_flag = dropNext(puyo_board, puyo_next)
                if not next_drop_flag:
                    isChaining = False

        # ダメージ計算
        color_magnification = [0] * 6
        for i in range(chain_count):
            # 同時に消した数
            all_count = sum(all_chain_info[i][1:8])
            # 連鎖係数 * (1 + (同時に消した数 - 3or4) * 0.15 * 同時消し係数)
            # magnification = chain_coefficient_list[i] * ( 1 + (all_count - 3) * 0.15 * elimination_coefficient)
            magnification = chain_coefficient_list[i] * ( 1 + (all_count - 4) * 0.15 * elimination_coefficient)
            for j in range(len(color_magnification) - 1):
                # 連鎖係数 * 分離数 + プリボ
                color_magnification[j] += magnification * all_chain_info[i][10+j] + (3 * all_chain_info[i][9])
            # ワイルドパターン
            color_magnification[5] += magnification * sum(all_chain_info[i][10:15]) + (3 * all_chain_info[i][9])
        
        # ペアカード情報
        if arg[1] == '1':
            # 日向・影山
            color_magnification[0] *= 5.5  # 赤
            color_magnification[4] *= 5.5  # 紫
        elif arg[1] == '5':
            # 宮兄弟
            color_magnification[4] *= 5.5  # 紫
            color_magnification[3] *= 5.5  # 黄
        
        # 今までみたパターンの中で最大のものか？
        for i in range(6):
            # 最大だったら更新
            if result[i] < color_magnification[i]:
                result[i] = color_magnification[i]
                result[i+6] = pattern + 1
    
    # 結果出力
    printResult(max_trace, elimination_coefficient, chain_coefficient, arg, result)
    
    # 終了処理
    cur.close()
    conn.close()


# In[19]:


# 引数チェック
def checkArg(arg):
    if len(arg) < 2:
        print("Error:引数指定が足りない")
        sys.exit()
    elif not arg[1].isdecimal():
        print("Error:第1引数が数値でない")
        sys.exit()
    elif not arg[2].isdecimal():
        print("Error:第2引数が数値でない")
        sys.exit()
    return


# In[20]:


# ネクスト設定
def initNext(no):
    if (no >= 1 and no <= 5) or no == 9:
        puyo_next = [no] * 8
    else:
        print("Error:第1引数は1～5 か 9のみ")
        sys.exit()
    return puyo_next


# In[21]:


# 盤面設定    
def initBoard(no):
    # [no]と[uniさんの画像]の位置関係
    # 1 2
    # 3 4
    # 5 6
    # 7 8
    puyo_board = []
    # 数字と盤面の関係
    # 1:赤 2:青 3:緑 4:黄 5:紫 6:邪 7:固 8:ハート 10:プリズム
    if no == 1:    # 15連鎖（全消し）
        puyo_board.extend([1,5,8,5,4,3,4,4,1,4,5,8,4,3,5,3,2,4,3,2,8,4,3,5,2,1,2,1,5,2,1,5,4,3,5,5,1,2,3,3,2,3,2,1,2,4,1,1])
    elif no == 2:  # 15連鎖（全消し）
        puyo_board.extend([4,5,1,2,1,4,3,2,5,3,2,5,4,2,3,2,5,4,1,2,1,4,4,1,8,8,5,3,2,5,1,4,4,3,5,3,2,5,1,8,3,1,3,1,5,3,2,4])
    elif no == 3:  # 15連鎖（全消し）
        puyo_board.extend([3,1,2,4,5,1,5,8,2,4,5,1,2,3,4,3,2,4,5,1,2,3,4,3,4,5,1,2,3,4,3,8,2,1,2,4,5,1,5,8,3,3,1,2,4,5,1,5])
    elif no == 4:  # 14連鎖（全消し可能）
        puyo_board.extend([1,5,4,5,8,3,8,1,5,1,3,1,4,5,2,8,3,3,4,4,2,2,1,1,5,2,5,5,3,3,4,5,5,2,1,2,1,1,5,4,1,1,2,1,2,2,3,4])
    elif no == 5:  # 14連鎖
        puyo_board.extend([2,8,3,5,1,2,4,2,8,3,1,3,5,1,4,3,4,1,4,4,3,5,2,3,5,4,3,3,4,4,1,4,1,2,1,4,3,5,5,3,2,8,2,1,1,3,3,5])
    elif no == 6:  # 14連鎖
        puyo_board.extend([4,3,5,1,4,2,8,4,3,1,1,2,2,8,8,2,3,2,5,3,4,1,5,4,4,4,2,5,3,4,1,5,5,2,1,3,2,1,3,5,1,1,2,2,3,3,4,4])
    elif no == 7:  # 13連鎖
        puyo_board.extend([5,2,4,4,8,4,3,3,4,8,2,5,4,5,1,1,2,3,4,2,5,1,3,2,3,1,3,1,2,3,2,8,1,4,5,1,2,5,2,3,1,4,1,5,5,3,1,3])
    elif no == 8:  # 13連鎖
        puyo_board.extend([1,3,2,1,5,2,8,2,5,4,2,1,4,5,4,5,8,5,5,2,1,1,4,5,4,3,4,3,5,3,1,2,4,3,4,3,1,4,2,8,3,4,3,5,3,3,5,2])
    elif no == 101: # 11連鎖
        puyo_board.extend([1,8,8,1,1,3,5,2,1,1,5,8,8,1,3,3,3,3,1,4,1,3,5,5,3,4,3,2,4,4,1,5,2,2,2,1,1,1,4,2,4,4,4,5,5,5,2,2])
    elif no == 102: # 11連鎖
        puyo_board.extend([4,3,5,8,8,1,8,2,2,3,5,2,1,8,2,2,5,5,2,1,1,2,5,5,3,3,1,2,2,5,4,5,2,4,1,1,3,4,3,4,2,2,4,4,1,3,3,4])
    elif no == 103: # 11連鎖
        puyo_board.extend([2,5,5,1,8,1,1,3,5,2,2,2,1,8,8,4,5,1,3,4,5,2,5,8,1,3,4,5,2,5,3,4,1,3,4,5,2,5,3,4,1,3,4,5,2,5,3,4])
    elif no == 104: # 11連鎖
        puyo_board.extend([8,8,5,4,3,3,2,1,1,5,5,4,3,2,1,8,5,4,4,3,2,2,1,1,1,2,3,1,8,4,5,4,1,1,3,1,1,5,4,4,2,2,2,3,3,1,5,5])
    elif no == 105: # 11連鎖
        puyo_board.extend([5,1,8,4,8,3,2,5,5,4,4,2,3,2,3,5,1,1,4,8,4,1,4,5,1,2,3,1,2,4,5,4,5,5,2,3,3,4,3,4,2,2,3,1,1,4,1,4])
    elif no == 106: # 11連鎖
        puyo_board.extend([8,4,8,8,1,2,2,3,5,4,1,3,8,1,1,1,5,4,2,5,5,3,2,2,4,5,3,3,3,5,4,3,1,5,2,2,2,5,3,3,1,1,3,3,3,4,4,4])
    elif no == 107: # 11連鎖
        puyo_board.extend([5,5,5,8,3,4,3,3,3,2,3,5,4,8,8,8,3,3,1,4,4,2,3,3,1,1,2,1,3,3,2,5,1,2,1,4,3,4,2,2,2,1,1,4,4,5,5,5])
    elif no == 108: # 11連鎖
        puyo_board.extend([2,2,8,3,4,3,5,4,4,4,2,2,8,4,4,8,4,8,4,5,3,4,5,5,1,3,1,2,5,5,1,5,1,1,3,1,1,1,4,4,3,3,5,2,2,2,3,4])
    elif no == 109: # 11連鎖
        puyo_board.extend([4,3,3,5,3,8,2,1,5,1,2,5,4,2,3,3,1,2,5,8,2,3,1,3,5,1,2,5,2,1,4,1,5,1,2,3,5,4,8,4,5,4,4,4,8,5,5,5])
    elif no == 110: # 11連鎖
        puyo_board.extend([1,3,2,4,3,8,5,8,1,3,2,4,3,2,1,8,4,4,5,5,1,2,5,5,5,5,1,1,8,1,5,1,4,1,3,2,4,3,3,1,4,1,3,2,4,2,2,1])
    elif no == 111: # 10連鎖 8個同時消し
        puyo_board.extend([4,8,1,2,3,4,4,2,5,2,2,8,1,4,3,5,1,1,2,1,2,5,2,3,5,3,3,3,4,2,5,3,5,1,1,1,2,5,8,3,5,4,4,4,8,2,2,2])
    elif no == 112: # 10連鎖 8個同時消し
        puyo_board.extend([1,4,2,5,5,3,1,8,8,1,4,4,5,3,1,4,1,4,2,2,2,5,3,1,1,4,8,3,4,4,3,1,3,3,3,2,5,4,5,4,2,2,2,4,5,5,4,4])
    elif no == 113: # 10連鎖 8個同時消し
        puyo_board.extend([3,3,3,1,2,2,5,8,2,1,5,3,4,4,8,5,3,3,3,8,4,1,8,5,5,5,5,4,1,3,2,5,1,1,1,4,1,3,4,2,2,2,2,3,4,4,3,3])
    elif no == 114: # 10連鎖 8個同時消し
        puyo_board.extend([1,8,5,8,2,3,2,4,2,2,5,4,2,3,2,8,5,5,2,2,3,2,3,4,2,3,3,4,1,2,4,4,2,1,8,4,5,1,1,1,1,1,3,3,4,5,5,5])
    elif no == 115: # 9連鎖 12個同時消し
        puyo_board.extend([3,4,4,5,2,2,2,3,5,5,5,2,3,3,3,8,4,4,1,3,1,1,1,8,3,3,3,4,2,2,2,1,8,1,1,1,5,5,5,2,8,4,4,4,3,3,3,5])
    elif no == 116: # 9連鎖 12個同時消し
        puyo_board.extend([2,5,8,4,2,2,1,8,3,4,4,2,8,2,4,1,5,5,5,4,5,5,4,1,3,3,1,3,2,5,4,1,3,2,2,1,3,2,5,4,2,1,1,3,3,2,2,4])
    else:
        print("Error:第2引数は1～8, 101～116のみ")
        sys.exit()
    return puyo_board


# In[22]:


# なぞりパターン総数取得
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


# In[23]:


# なぞりパターン取得
def getTracePattern(i):
    cur.execute('SELECT board FROM pattern WHERE id = %s', (i,))
    trace_pattern = list(list(cur.fetchone())[0])
    return trace_pattern


# In[24]:


# 盤面に対してなぞりパターンを適用
def applyTracePattern(puyo_board, trace_pattern):
    target = '1'
    for i in range(len(trace_pattern)):
        if trace_pattern[i] == target:
            puyo_board[i] = 0
    return puyo_board


# In[25]:


# 消えた部分を落とす
def dropBoard(puyo_board):
    # 数字と盤面の関係
    # 0:なぞったorぷよが消えたところ 9:落ちて消えたところ
    # 右下から左上まで走査
    for ri in reversed(range(len(puyo_board))):
        # 0以外は次を見る
        if puyo_board[ri] != 0:
            continue
        # 0だったら1つ上を見る
        target = ri - 8
        while target >= 0:
            if puyo_board[target] != 0:
                # 1つ上が0以外だったら落として、1つ上を0にする
                puyo_board[ri] = puyo_board[target]
                puyo_board[target] = 0
                # debug('dropBoard', puyo_board) # debug
                break
            else:
                # 1つ上が0だったら、更に1つ上を見る
                target -= 8
    # 落ちて消えたところを9にする
    for i in range(len(puyo_board)):
        if puyo_board[i] == 0:
            puyo_board[i] = 9

    return puyo_board


# In[26]:


# ネクストを落とす
def dropNext(puyo_board, puyo_next):
    next_drop_flag = False
    for i in range(47, -1, -1):
        if puyo_board[i] != 9:
            continue
        if puyo_next[i%8] != 9:
            puyo_board[i] = puyo_next[i%8]
            puyo_next[i%8] = 9
            next_drop_flag = True
            
    return puyo_board, puyo_next, next_drop_flag


# In[27]:


# 結合チェック
def checkConnection(puyo_board, chain_info):
    # 確認用配列の生成
    # 0:未チェック 1:チェック中 2:チェック済み(結合) 3:チェック済み(未結合)
    check_board = [0] * 48
    # 確認用配列の設定
    for i in range(len(puyo_board)):
        # 6:邪 7:固 8:ハ 9:無 は確認しなくてよい
        if puyo_board[i] >= 6 and puyo_board[i] <= 9:
            check_board[i] = 3
    
    # 結合チェック
    for i in range(len(puyo_board)):
        # 結合数
        count = 0
        # 確定している時は飛ばす
        if check_board[i] == 2 or check_board[i] == 3:
            continue
        check_board, count = recursionCheckConnection(i, check_board, puyo_board, count)
        # iのぷよは何個つながっているかが返ってくる
        # 消える数だけ繋がっている場合
        # if count >= 3:    # りんごだから3 通常なら4
        if count >= 4:    # りんごだから3 通常なら4
            # chain_infoに赤/青/緑/黄/紫の情報を格納
            chain_info[puyo_board[i]] += count
            chain_info[9+puyo_board[i]] += 1
            for j in range(len(check_board)):
                if check_board[j] == 1:
                    check_board[j] = 2
        # 繋がっていない場合
        else:
            for j in range(len(check_board)):
                if check_board[j] == 1:
                    check_board[j] = 3
    
    # 確認用配列が2になっている箇所の盤面を0にする
    for i in range(len(puyo_board)):
        if check_board[i] == 2:
            puyo_board[i] = 0

    # 1:赤 2:青 3:緑 4:黄 5:紫 6:邪 7:固 8:ハート 10:プリズム
    # 邪・固・ハ・プ処理
    for i in range(len(puyo_board)):
        if puyo_board[i] == 6 or puyo_board[i] == 7 or puyo_board[i] == 8 or puyo_board[i] == 10:
            # 上がある
            if i >= 8 and check_board[i-8] == 2:
                puyo_board, chain_info = checkConnectionOther(puyo_board, i, chain_info)
            # 右がある
            elif i % 8 != 7 and check_board[i+1] == 2:
                puyo_board, chain_info = checkConnectionOther(puyo_board, i, chain_info)
            # 下がある
            elif i < 40 and check_board[i+8] == 2:
                puyo_board, chain_info = checkConnectionOther(puyo_board, i, chain_info)
            # 左がある
            elif i % 8 != 0 and check_board[i-1] == 2:
                puyo_board, chain_info = checkConnectionOther(puyo_board, i, chain_info)
    
    return puyo_board, chain_info


# In[28]:


# 色ぷよ以外のチェック
def checkConnectionOther(puyo_board, i, chain_info):
    # 邪の場合
    if puyo_board[i] == 6:
        puyo_board[i] = 0
        chain_info[6] += 1
    # 固の場合
    elif puyo_board[i] == 7:
        puyo_board[i] = 6
        chain_info[7] += 1
    # ハの場合
    elif puyo_board[i] == 8:
        puyo_board[i] = 0
        chain_info[8] += 1
    # プの場合
    elif puyo_board[i] == 10:
        puyo_board[i] = 0
        chain_info[9] += 1
    return puyo_board, chain_info


# In[29]:


# 再帰結合チェック
def recursionCheckConnection(i, check_board, puyo_board, count):
    # 確認中
    check_board[i] = 1
    # 結合カウント+1
    count += 1
    # 上がある
    if i >= 8:
        if check_board[i-8] == 0 and (puyo_board[i] == puyo_board[i-8]):
            check_board, count = recursionCheckConnection(i-8, check_board, puyo_board, count)
    # 右がある
    if i % 8 != 7:
        if check_board[i+1] == 0 and (puyo_board[i] == puyo_board[i+1]):
            check_board, count = recursionCheckConnection(i+1, check_board, puyo_board, count)
    # 下がある
    if i < 40:
        if check_board[i+8] == 0 and (puyo_board[i] == puyo_board[i+8]):
            check_board, count = recursionCheckConnection(i+8, check_board, puyo_board, count)
    # 左がある
    if i % 8 != 0:
        if check_board[i-1] == 0 and (puyo_board[i] == puyo_board[i-1]):
            check_board, count = recursionCheckConnection(i-1, check_board, puyo_board, count)
    return check_board, count


# In[30]:


# デバッグ用出力
def debug(text, puyo_board, puyo_next='[         none         ]',):
    print(text)
    print(puyo_next)
    print('------------------------')
    print(puyo_board[0:8])
    print(puyo_board[8:16])
    print(puyo_board[16:24])
    print(puyo_board[24:32])
    print(puyo_board[32:40])
    print(puyo_board[40:48])
    print(' ')

def debugChain(chain_info):
    print('連鎖数:'+ str(chain_info[0]))
    print('赤個数:'+ str(chain_info[1]) + ' 赤分離:' + str(chain_info[10]))
    print('青個数:'+ str(chain_info[2]) + ' 青分離:' + str(chain_info[11]))
    print('緑個数:'+ str(chain_info[3]) + ' 緑分離:' + str(chain_info[12]))
    print('黄個数:'+ str(chain_info[4]) + ' 黄分離:' + str(chain_info[13]))
    print('紫個数:'+ str(chain_info[5]) + ' 紫分離:' + str(chain_info[14]))
    print('邪個数:'+ str(chain_info[6]) + ' 固個数:' + str(chain_info[7]) + ' ハ個数:' + str(chain_info[8]) + ' プ個数:' + str(chain_info[9]))  
    print(' ')


# In[31]:


# 結果出力
def printResult(max_trace, elimination_coefficient, chain_coefficient, arg, result):
    path_w = 'result_P' + str(arg[1]) + '_R' + str(arg[2]) + '.txt'
    with open(path_w, 'w', encoding='utf-8') as f:
        print('最大なぞり    :' + str(max_trace), file=f)
        print('同時消し係数  :' + str(elimination_coefficient), file=f)
        print('連鎖係数      :' + str(chain_coefficient), file=f)
        print('ネクスト      :' + str(arg[1]), file=f)
        print('りんごパターン:' + str(arg[2]), file=f)
        print('', file=f)
        print('赤 倍率       :' + str(round(result[0], 2)), file=f)
        print('赤 パターン   :' + str(result[6]), file=f)
        getPattern(result[6])
        print('', file=f)
        print('青 倍率       :' + str(round(result[1], 2)), file=f)
        print('青 パターン   :' + str(result[7]), file=f)
        print('')
        getPattern(result[7])
        print('', file=f)
        print('緑 倍率       :' + str(round(result[2], 2)), file=f)
        print('緑 パターン   :' + str(result[8]), file=f)
        print('')
        getPattern(result[8])
        print('', file=f)
        print('黄 倍率       :' + str(round(result[3], 2)), file=f)
        print('黄 パターン   :' + str(result[9]), file=f)
        print('')
        getPattern(result[9])
        print('', file=f)
        print('紫 倍率       :' + str(round(result[4], 2)), file=f)
        print('紫 パターン   :' + str(result[10]), file=f)
        print('')
        getPattern(result[10])
        print('', file=f)
        print('ワ 倍率       :' + str(round(result[5], 2)), file=f)
        print('ワ パターン   :' + str(result[11]), file=f)
        print('')
        getPattern(result[11])

def getPattern(value):
    cur.execute('SELECT board FROM pattern WHERE id = %s', (value,))
    trace_pattern = list(list(cur.fetchone())[0])
    pattern = list(map((lambda x: int(x)), trace_pattern))
    print(pattern[0:8])
    print(pattern[8:16])
    print(pattern[16:24])
    print(pattern[24:32])
    print(pattern[32:40])
    print(pattern[40:48])


# In[32]:


if __name__ == '__main__':
    main()

