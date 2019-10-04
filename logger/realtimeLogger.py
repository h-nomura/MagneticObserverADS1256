#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from ADS1256_definitions import *
from pipyadc import ADS1256

import time, datetime
import csv

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

from multiprocessing import Manager,Value, Process
import math
import itertools

from matplotlib import pyplot as plt
from matplotlib import animation
if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")
# Input pin for the potentiometer on the Waveshare Precision ADC board:
Diff0_1 = POS_AIN0|NEG_AIN1
Diff2_3 = POS_AIN2|NEG_AIN3
Diff4_5 = POS_AIN4|NEG_AIN5
Diff6_7 = POS_AIN6|NEG_AIN7
CH_SEQUENCE = (Diff0_1,Diff2_3,Diff4_5,Diff6_7)

def eliminate_f(date_str):
    date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
    return date.strftime('%H:%M:%S')

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def df_maker(f,C_mode):
    df_list = {'dataTime':[],'data':[]}
    df_list_raw = {'dataTime':[],'data':[]}
    SAMdata = 0
    NUMdata = 0
    NOWdate = ''
    SPrate = 0
    average = 0
    index = 0
    for row in f:#row is list
        if index == 0:
            dataday = row[0]
            index = 1
        else:
            if C_mode == 'raw':
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2
            elif C_mode == '':
                SAMdata += float(row[1])
                NUMdata += 1
                if NOWdate != '1s average':
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        average += (SAMdata / NUMdata)
                        average /= 2
                        SAMdata = float(row[1])
                        SPrate = NUMdata
                        NUMdata = 1
                NOWdate = eliminate_f(row[0])
            elif C_mode == 'overlay':
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2

                SAMdata += float(row[1])
                NUMdata += 1
                if NOWdate != '':
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[1])
                        SPrate = NUMdata
                        NUMdata = 1
                NOWdate = eliminate_f(row[0])
            elif C_mode == 'test':
                print(row)

    return df_list['dataTime'],df_list['data'],df_list_raw['dataTime'],df_list_raw['data'],average,SPrate

def _redraw(_, ax, data, C_mode, C_range):
    """グラフを再描画するための関数"""
    # 現在のグラフを消去する
    plt.cla()

    df = df_maker(data,C_mode)
    # 折れ線グラフを再描画する
    ax.yaxis.grid(True)
    ax.set_ylim([df[4] - (C_range/2),df[4] + (C_range/2)])
    if C_mode == "raw" or C_mode == "overlay":
        ax.plot(pd.to_datetime(df[2], utc=True), df[3], color='b')
    if C_mode == "1s average" or C_mode == "overlay":
        ax.plot(pd.to_datetime(df[0], utc=True), df[1], color='r')
    ax.set_title('(JST) ' + 'magnetic force(nT)' + C_mode +"range="+ str(C_range) +"rate="+ str(df[5]))

def _measurement(plotData,C_save,C_Drate):
    # 描画するデータ 
    now = datetime.datetime.now()#get time
    plotData = [['{0:%Y-%m-%d }'.format(now),
    'Magnetic force(nT)_1ch','Magnetic force(nT)_2ch',
    'Magnetic force(nT)_3ch','Magnetic force(nT)_4ch']]
    ads = ADS1256()
    ads.drate = (DRATE_100 if C_Drate == 100 else
    DRATE_500 if C_Drate == 500 else
    DRATE_1000 if C_Drate == 1000 else
    DRATE_2000)
    ads.pga_gain = 1
    ads.cal_self()
    """データを一定間隔で追加するスレッドの処理"""
    counter = 0
    while True:            
        now = datetime.datetime.now()
        # get data
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        voltages     = [(i * ads.v_per_digit * 6.970260223 - 15.522769516) for i in raw_channels]
        MagneticF     = [(i * 1000 / 0.16) for i in voltages]
        plotData.append(['{0:%H:%M:%S.%f}'.format(now), MagneticF[0], MagneticF[1], MagneticF[2], MagneticF[3]])
        counter += 1
        if counter > 1000:
            plotData.pop(1)
            counter -= 1

def show_graph(C_save,C_range,C_mode,C_Drate):
    # 描画領域
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    # loggerプロセスを起動する
    with Manager() as manager:
        plotData = manager.list()
        logger = Process(target=_measurement,args=[plotData,C_save,C_Drate])
        logger.start()    
    def _init():
        """データを一定間隔で追加するためのスレッドを起動する"""
        # t = threading.Thread(target=_measurement, args=(C_Drate,C_save,))
        # t.daemon = True
        # t.start()

    params = {
        'fig': fig,
        'func': _redraw,  # グラフを更新する関数
        'init_func': _init,  # グラフ初期化用の関数 (今回はデータ更新用スレッドの起動)
        'fargs': (ax, plotData, C_mode, C_range),  # 関数の引数 (フレーム番号を除く)
        'interval': 1000,  # グラフを更新する間隔 (ミリ秒)
    }
    anime = animation.FuncAnimation(**params)

    # グラフを表示する
    plt.show()

def main():
    while True:#set config
        print("Do you want to save the observation data?(yes/no)")
        config_save = input('>> ')
        print("Set the graph parameters to be displayed. \nEnter the magnetic Force range.(nT,10-80000)")
        config_range = int(input('>> '))
        print("Select graph to display(1s average/raw/overlay)")
        config_mode = input('>> ')
        print("Set DRATE(2000/1000/500)")
        config_Drate = int(input('>> '))

        if config_save == "yes" or config_save == "no":
            if 10 <= config_range <= 80000:
                if config_mode == "1s average" or config_mode == "raw" or config_mode == "overlay":
                    break
        print("######input errer#######\ntry again!!")
    show_graph(config_save,config_range,config_mode,config_Drate)



if __name__ == '__main__':
    main()