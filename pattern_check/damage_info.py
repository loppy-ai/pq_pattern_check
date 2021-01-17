#!/usr/bin/env python
# coding: utf-8


class DamageInfo:
    # 入力：連鎖結果・同時消し係数・連鎖係数リスト・最大結合数
    def __init__(self, chain_result, elimination_coefficient, chain_coefficient, max_connection):
        self.chain_result = chain_result
        self.elimination_coefficient = elimination_coefficient
        self.chain_coefficient = chain_coefficient
        self.max_connection = max_connection
        
        self.chain_coefficient_list = self._getChainCoefficientList()
        self.chain_count = len(self.chain_result)

    def _getChainCoefficientList(self):
        if self.chain_coefficient == 1:
            ret = [1, 1.4, 1.7, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4]
        elif self.chain_coefficient == 4:
            ret = [1, 2.6, 3.8, 5.0, 5.8, 6.6, 7.4, 8.2, 9.0, 9.8, 10.6, 11.4, 12.2, 13.0, 13.8, 14.6]
        elif self.chain_coefficient == 5:
            ret = [1, 3.0, 4.5, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0]
        elif self.chain_coefficient == 6:
            ret = [1, 3.4, 5.2, 7.0, 8.2, 9.4, 10.6, 11.8, 13.0, 14.2, 15.4, 16.6, 17.8, 19.0, 20.2, 21.4]
        elif self.chain_coefficient == 7:
            ret = [1, 3.8, 5.9, 8.0, 9.4, 10.8, 12.2, 13.6, 15.0, 16.4, 17.8, 19.2, 20.6, 22.0, 23.4, 24.8]
        return ret

    # 色別消去数取得
    def getNumOfElimination(self, colorNumber):
        ret = 0
        if self.chain_count != 0:
            ret = sum([count[colorNumber] for count in self.chain_result])
        return ret

    # 全色ぷよ消去数取得
    def getAllColorPuyoNumOfElimination(self):
        ret = 0
        for i in range(5):
            ret += self.getNumOfElimination(i+1)
        return ret

    # 全おじゃまぷよ消去数取得
    def getAllOjamaPuyoNumOfElimination(self):
        return self.getNumOfElimination(6) + self.getNumOfElimination(7)

    # ハート消去数取得
    def getHeartNumOfElimination(self):
        return self.getNumOfElimination(8)

    # チャンスぷよを生成するかどうか
    def canMakeChancePuyo(self):
        ret = False
        if self.max_connection != 3:
            # 特別ルール時は作らない
            if self.chain_count >= 6:
                ret = True
            else:
                for i in range(self.chain_count):
                    if sum(self.chain_result[i][1:8]) >= 16:
                        ret = True
                        break
        return ret

    # 色別倍率
    def getMagnificationByColor(self, colorNumber):
        all_chain_magnification = 0
        if self.chain_count != 0:
            for i in range(self.chain_count):
                all_count = sum(self.chain_result[i][1:8])
                # i連鎖目のダメージ
                # 連鎖係数 * (1 + (同時に消した数 - 3or4) * 0.15 * 同時消し係数)
                chain_magnification = self.chain_coefficient_list[i] * ( 1 + (all_count - self.max_connection) * 0.15 * self.elimination_coefficient)
                # 足していく
                # i連鎖目のダメージ * i連鎖目の分離数 + 3 * 全プリボの数
                if colorNumber != 9:
                    # 通常時
                    all_chain_magnification += chain_magnification * self.chain_result[i][9+colorNumber] + (3 * self.chain_result[i][9])
                else:
                    # ワイルド時
                    all_chain_magnification += chain_magnification * sum(self.chain_result[i][10:15]) + (3 * self.chain_result[i][9])
        return all_chain_magnification

    # ハート倍率
    def getMagnificationHeart(self):
        # TODO:全消ししたら+1倍
        return self.getHeartNumOfElimination()*(1+0.05*self.chain_count)