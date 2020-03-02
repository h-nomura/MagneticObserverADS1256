# coding: UTF-8
import csv
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys
import datetime
from statistics import median
from statistics import mean
from control.matlab import * #### pip install control // pip install slycot

def BODE_print(b,a):
    bessel = tf(b,a)
    #bode(bessel,[0.1,1000])
    bode(bessel)
    plt.show()

def main():
    # パラメータ設定
    fs = 155                  # サンプリング周波数[Hz]
    fpass = 10                       # 通過遮断周波数[Hz]
    fstop = 30                       # 阻止域遮断周波数[Hz]
    gpass = 0.4                      # 通過域最大損失量[dB]
    gstop = 20                       # 阻止域最小減衰量[dB]

    # 正規化
    fn = fs/2                        # ナイキスト周波数
    wp = fpass/fn                    # 正規化通過遮断周波数(無次元)
    ws = fstop/fn                    # 正規化阻止域遮断周波数(無次元)


    N = 6 #### order of the filter
    # n, wn = signal.bessel(N, ws, "low")
    # b, a = signal.iirfilter(N, wp, rp=gpass, rs=gstop, btype='low',ftype='bessel')
    b, a = signal.bessel(N, wp, "low")
    BODE_print(b, a)
    print("end")

if __name__ == '__main__':
    main()