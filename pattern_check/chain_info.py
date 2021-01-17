#!/usr/bin/env python
# coding: utf-8

import copy

class ChainInfo:
    # 入力：ネクスト・盤面・最大結合数・デバッグモードかどうか
    def __init__(self, puyo_next, puyo_board, trace_pattern, max_connection, is_debug_mode):
        self.puyo_next = puyo_next
        self.puyo_board = puyo_board
        self.trace_pattern = trace_pattern
        self.max_connection = max_connection
        self.is_debug_mode = is_debug_mode
        # 連鎖処理
        self.chain_result = self._chain()


    def getChainResult(self):
        return self.chain_result


    def _chain(self):
        if self.is_debug_mode:
            self._debug('defaultBoard', self.puyo_next)
            self._debugTracePattern('tracePattern')
        # 盤面に対してなぞりパターンを適用
        self._applyTracePattern()
        if self.is_debug_mode:
            self._debug('applyedTracePattern', self.puyo_next)
        # 消えた部分を落とす
        self._dropBoard()
        if self.is_debug_mode:
            self._debug('dropBoard', self.puyo_next)
        # 連鎖終了までループする
        is_chaining = True
        # 連鎖情報
        all_chain_info = []
        # 連鎖数
        chain_count = 0
        while (is_chaining):
            # 連鎖数, 赤個, 青個, 緑個, 黄個, 紫個, 邪個, 固個, ハ個, プ個, 赤分, 青分, 緑分, 黄分, 紫分
            self.chain_info = [0] * 15
            # 結合チェック
            self._checkConnection()
            # ぷよが消えた
            if 0 in self.puyo_board:
                # 次の連鎖
                chain_count += 1 
                self.chain_info[0] = chain_count
                if self.is_debug_mode:
                    self._debug('elimination', self.puyo_next)
                    self._debugChain()
                self._dropBoard()
                if self.is_debug_mode:
                    self._debug('dropBoard', self.puyo_next)
                all_chain_info.append(self.chain_info)
            # 消えなかった
            else:
                # nextを落とす
                next_drop_flag = self._dropNext()
                if self.is_debug_mode:
                    self._debug('dropNext', self.puyo_next)
                if not next_drop_flag:
                    is_chaining = False
        return all_chain_info


    def _applyTracePattern(self):
        for i in range(48):
            if self.trace_pattern[i] == '1':
                self.puyo_board[i] = 0


    def _dropBoard(self):
        # 0:なぞったorぷよが消えたところ 9:落ちて消えたところ
        # 右下から左上まで走査
        for ri in reversed(range(48)):
            # 0以外は次を見る
            if self.puyo_board[ri] != 0:
                continue
            # 0だったら1つ上を見る
            target = ri - 8
            while target >= 0:
                if self.puyo_board[target] != 0:
                    # 1つ上が0以外だったら落として、1つ上を0にする
                    self.puyo_board[ri] = self.puyo_board[target]
                    self.puyo_board[target] = 0
                    break
                else:
                    # 1つ上が0だったら、更に1つ上を見る
                    target -= 8
        # 落ちて消えたところを9にする
        for i in range(48):
            if self.puyo_board[i] == 0:
                self.puyo_board[i] = 9


    def _dropNext(self):
        next_drop_flag = False
        for i in range(47, -1, -1):
            if self.puyo_board[i] != 9:
                continue
            if self.puyo_next[i%8] != 9:
                self.puyo_board[i] = self.puyo_next[i%8]
                self.puyo_next[i%8] = 9
                next_drop_flag = True
        return next_drop_flag


    def _checkConnection(self):
        # 確認用配列の生成
        # 0:未チェック 1:チェック中 2:チェック済み(結合) 3:チェック済み(未結合)
        check_board = [0] * 48
        # 確認用配列の設定
        for i in range(48):
            # 6:邪 7:固 8:ハ 9:無 は確認しなくてよい
            if self.puyo_board[i] >= 6 and self.puyo_board[i] <= 9:
                check_board[i] = 3
        
        # 結合チェック
        for i in range(48):
            # 結合数
            count = 0
            # 確定している時は飛ばす
            if check_board[i] == 2 or check_board[i] == 3:
                continue
            check_board, count = self._recursionCheckConnection(i, check_board, count)
            # iのぷよは何個つながっているかが返ってくる
            # 消える数だけ繋がっている場合
            if count >= self.max_connection:
                # chain_infoに赤/青/緑/黄/紫の情報を格納
                self.chain_info[self.puyo_board[i]] += count
                self.chain_info[9+self.puyo_board[i]] += 1
                for j in range(48):
                    if check_board[j] == 1:
                        check_board[j] = 2
            # 繋がっていない場合
            else:
                for j in range(48):
                    if check_board[j] == 1:
                        check_board[j] = 3


        # 確認用配列が2になっている箇所の盤面を0にする
        for i in range(48):
            if check_board[i] == 2:
                self.puyo_board[i] = 0


        # 1:赤 2:青 3:緑 4:黄 5:紫 6:邪 7:固 8:ハート 10:プリズム
        # 邪・固・ハ・プ処理
        for i in range(48):
            if self.puyo_board[i] == 6 or self.puyo_board[i] == 7 or self.puyo_board[i] == 8 or self.puyo_board[i] == 10:
                # 上がある
                if i >= 8 and check_board[i-8] == 2:
                    self._checkConnectionOther(i)
                # 右がある
                elif i % 8 != 7 and check_board[i+1] == 2:
                    self._checkConnectionOther(i)
                # 下がある
                elif i < 40 and check_board[i+8] == 2:
                    self._checkConnectionOther(i)
                # 左がある
                elif i % 8 != 0 and check_board[i-1] == 2:
                    self._checkConnectionOther(i)


    # 再帰結合チェック
    def _recursionCheckConnection(self, i, check_board, count):
        # 確認中
        check_board[i] = 1
        # 結合カウント+1
        count += 1
        # 上がある
        if i >= 8:
            if check_board[i-8] == 0 and (self.puyo_board[i] == self.puyo_board[i-8]):
                check_board, count = self._recursionCheckConnection(i-8, check_board, count)
        # 右がある
        if i % 8 != 7:
            if check_board[i+1] == 0 and (self.puyo_board[i] == self.puyo_board[i+1]):
                check_board, count = self._recursionCheckConnection(i+1, check_board, count)
        # 下がある
        if i < 40:
            if check_board[i+8] == 0 and (self.puyo_board[i] == self.puyo_board[i+8]):
                check_board, count = self._recursionCheckConnection(i+8, check_board, count)
        # 左がある
        if i % 8 != 0:
            if check_board[i-1] == 0 and (self.puyo_board[i] == self.puyo_board[i-1]):
                check_board, count = self._recursionCheckConnection(i-1, check_board, count)
        return check_board, count


    def _checkConnectionOther(self, i):
        # 邪の場合
        if self.puyo_board[i] == 6:
            self.puyo_board[i] = 0
            self.chain_info[6] += 1
        # 固の場合
        elif self.puyo_board[i] == 7:
            self.puyo_board[i] = 6
            self.chain_info[7] += 1
        # ハの場合
        elif self.puyo_board[i] == 8:
            self.puyo_board[i] = 0
            self.chain_info[8] += 1
        # プの場合
        elif self.puyo_board[i] == 10:
            self.puyo_board[i] = 0
            self.chain_info[9] += 1


    def _debug(self, text, puyo_next='[         none         ]',):
        board = copy.deepcopy(self.puyo_board)
        next = copy.deepcopy(puyo_next)
        if type(next) is not str:
            for i in range(8):
                if next[i] == 9:
                    next[i] = 0
        for i in range(48):
            if board[i] == 9:
                board[i] = 0
        print(text)
        print(next)
        print('------------------------')
        print(board[0:8])
        print(board[8:16])
        print(board[16:24])
        print(board[24:32])
        print(board[32:40])
        print(board[40:48])
        print(' ')


    def _debugTracePattern(self, text, next='[         none         ]',):
        board = [int(i) for i in self.trace_pattern]
        print(text)
        print(next)
        print('------------------------')
        print(board[0:8])
        print(board[8:16])
        print(board[16:24])
        print(board[24:32])
        print(board[32:40])
        print(board[40:48])
        print(' ')


    def _debugChain(self):
        print('連鎖数:'+ str(self.chain_info[0]))
        print('赤個数:'+ str(self.chain_info[1]) + ' 赤分離:' + str(self.chain_info[10]))
        print('青個数:'+ str(self.chain_info[2]) + ' 青分離:' + str(self.chain_info[11]))
        print('緑個数:'+ str(self.chain_info[3]) + ' 緑分離:' + str(self.chain_info[12]))
        print('黄個数:'+ str(self.chain_info[4]) + ' 黄分離:' + str(self.chain_info[13]))
        print('紫個数:'+ str(self.chain_info[5]) + ' 紫分離:' + str(self.chain_info[14]))
        print('邪個数:'+ str(self.chain_info[6]) + ' 固個数:' + str(self.chain_info[7]) + ' ハ個数:' + str(self.chain_info[8]) + ' プ個数:' + str(self.chain_info[9]))  
        print(' ')