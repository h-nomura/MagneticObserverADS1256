#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import math
import itertools

from matplotlib import pyplot as plt
from matplotlib import animation


def _redraw(_, x, y, x2, y2):
    """グラフを再描画するための関数"""
    # 現在のグラフを消去する
    plt.cla()
    # 折れ線グラフを再描画する
    plt.plot(x, y)
    plt.plot(x2, y2)


def show_graph():
    # 描画領域
    fig = plt.figure(figsize=(10, 6))
    # 描画するデータ (最初は空っぽ)
    x = []
    y = []
    x2 = []
    y2 = []

    def _update():
        """データを一定間隔で追加するスレッドの処理"""
        for frame in itertools.count(0, 0.1):
            x.append(frame)
            y.append(math.sin(frame))
            x2.append(frame)
            y2.append(math.cos(frame))
            # データを追加する間隔 (100ms)
            time.sleep(0.1)

    def _init():
        """データを一定間隔で追加するためのスレッドを起動する"""
        t = threading.Thread(target=_update)
        t.daemon = True
        t.start()

    params = {
        'fig': fig,
        'func': _redraw,  # グラフを更新する関数
        'init_func': _init,  # グラフ初期化用の関数 (今回はデータ更新用スレッドの起動)
        'fargs': (x, y, x2, y2),  # 関数の引数 (フレーム番号を除く)
        'interval': 250,  # グラフを更新する間隔 (ミリ秒)
    }
    anime = animation.FuncAnimation(**params)

    # グラフを表示する
    plt.show()

def main():
    while True:#set config
        print("Do you want to save the observation data?(yes/no)")
        flag_save = input('>> ')

        print("Set the graph parameters to be displayed. \nEnter the magnetic Force range.(nT,10-80000)")
        config_range = int(input('>> '))
        print("Select graph to display(1s average/raw/overlay)")
        config_mode = input('>> ')
        if flag_save == "yes" or flag_save == "no":
            if 10 <= config_range <= 80000:
                if config_mode == "1s average" or config_mode == "raw" or config_mode == "overlay":
                    break
        print("######input errer#######\ntry again!!")
    show_graph()



if __name__ == '__main__':
    main()