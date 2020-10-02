#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#### test ####
# import random
##############
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

from time import sleep
from datetime import timezone
from statistics import mean
from statistics import median

from matplotlib import pyplot as plt
from matplotlib import animation
if not os.path.exists("/dev/spidev0.1"):
   raise IOError("Error: No SPI device. Check settings in /boot/config.txt")
#### Input pin for the potentiometer on the Waveshare Precision ADC board:
Diff0_1 = POS_AIN0|NEG_AIN1
Diff2_3 = POS_AIN2|NEG_AIN3
Diff4_5 = POS_AIN4|NEG_AIN5
Diff6_7 = POS_AIN6|NEG_AIN7
CH_SEQUENCE = (Diff0_1,Diff2_3,Diff4_5,Diff6_7)

PLOT_DATA_NUM = 201

def eliminate_f(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
        return date.strftime('%H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%H:%M:%S')

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def df_maker(f,C_mode):
    df_list = {'Time':[],'1ch':[],'2ch':[],'3ch':[],'4ch':[]}
    index = 0
    for row in f:#row is list
        if index == 0:
            dataday = row[0]
            index = 1
        else:
            if row[0] != 0:
                df_list['Time'].append(dataday + row[0])
                df_list['1ch'].append(float(row[1]))
                df_list['2ch'].append(float(row[2]))
                df_list['3ch'].append(float(row[3]))
                df_list['4ch'].append(float(row[4]))
    return df_list['Time'],df_list['1ch'],df_list['2ch'],df_list['3ch'],df_list['4ch']

def get_Srate(time_dat):
    now_time  = eliminate_f(time_dat[0])
    i = 0
    try:
        #### load head ####
        while(1):
            i += 1
            if now_time != eliminate_f(time_dat[i]):
                now_time = eliminate_f(time_dat[i])
                break
        #### count ####
        count = 0
        while(1):
            i += 1
            count += 1
            if now_time != eliminate_f(time_dat[i]):
                return count
    except IndexError:
        return 0

def eliminate_errerdata(Cutoff,time,data):
    data_median = median(data)
    arg = []
    #### search ####
    for j in range(len(data)):
        if abs(data[j] - data_median) >= Cutoff:
            arg.insert(0, j)
    #### eliminate ####
    for j in arg:
        time.pop(j)
        data.pop(j)
    return time, data

def medianFilter(time_dat,dat,Cutoff):
    out = {'time':[],'data':[]}
    now_time = eliminate_f(time_dat[0])
    buf_t = []
    buf_d = []
    i = -1
    try:
        while(1):
            i += 1
            buf_t.append(time_dat[i])
            buf_d.append(dat[i])            
            if i+1 == len(dat):
                clean_data = eliminate_errerdata(Cutoff,buf_t,buf_d)
                out['time'].extend(clean_data[0])
                out['data'].extend(clean_data[1])                
                return out['time'], out['data']
            if now_time != eliminate_f(time_dat[i+1]):
                clean_data = eliminate_errerdata(Cutoff,buf_t,buf_d)
                out['time'].extend(clean_data[0])
                out['data'].extend(clean_data[1])
                buf_t.clear
                buf_d.clear
    except IndexError:
        return time_dat,dat

def _redraw(_, ax, data, C_mode, C_range):
    """グラフを再描画するための関数"""
    # 現在のグラフを消去する
    plt.cla()
    print("redraw")
    
    # print(data[990])

    df = df_maker(data,C_mode)
    # 折れ線グラフを再描画する
    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    
    t_1ch = df[0]
    d_1ch = df[1]
    d_2ch = df[2]
    d_3ch = df[3]
    d_4ch = df[4]

    ax_1ch.set_ylabel('X [nT]', fontsize=18)
    ax_2ch.set_ylabel('Y [nT]', fontsize=18)
    ax_3ch.set_ylabel('Z [nT]', fontsize=18)
    ax_4ch.set_ylabel('Temperature [C]', fontsize=18)
    ax_1ch.set_ylim([mean(d_1ch) - (C_range/2),mean(d_1ch) + (C_range/2)])
    ax_2ch.set_ylim([mean(d_2ch) - (C_range/2),mean(d_2ch) + (C_range/2)])
    ax_3ch.set_ylim([mean(d_3ch) - (C_range/2),mean(d_3ch) + (C_range/2)])
    ax_1ch.plot(pd.to_datetime(t_1ch, utc=True), d_1ch, color='r')
    ax_2ch.plot(pd.to_datetime(t_1ch, utc=True), d_2ch, color='g')
    ax_3ch.plot(pd.to_datetime(t_1ch, utc=True), d_3ch, color='b')
    ax_4ch.plot(pd.to_datetime(t_1ch, utc=True), d_4ch, color='k')
    ax_1ch.set_title('(JST) ' + 'magnetic force(nT)' + C_mode +"range="+ str(C_range) +"rate="+ str(df[5]))

def ploting(plotData,C_save,C_range,C_mode,C_Drate):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(411) #Z axis
    ax_2ch = fig.add_subplot(412) #Y axis
    ax_3ch = fig.add_subplot(413) #X axis
    ax_4ch = fig.add_subplot(414)

    while True:
        df = df_maker(plotData ,C_mode)
        if len(df[0]) > 200:
            # 折れ線グラフを再描画する
            plt.cla()
            ax_1ch.yaxis.grid(True)
            ax_2ch.yaxis.grid(True)
            ax_3ch.yaxis.grid(True)
            ax_4ch.yaxis.grid(True)
            
            t_1ch = df[0]
            d_1ch = df[1]
            d_2ch = df[2]
            d_3ch = df[3]
            d_4ch = df[4]

            ax_1ch.set_ylabel('X [nT]', fontsize=18)
            ax_2ch.set_ylabel('Y [nT]', fontsize=18)
            ax_3ch.set_ylabel('Z [nT]', fontsize=18)
            ax_4ch.set_ylabel('Temperature [C]', fontsize=18)
            ax_1ch.set_ylim([mean(d_1ch) - (C_range/2),mean(d_1ch) + (C_range/2)])
            ax_2ch.set_ylim([mean(d_2ch) - (C_range/2),mean(d_2ch) + (C_range/2)])
            ax_3ch.set_ylim([mean(d_3ch) - (C_range/2),mean(d_3ch) + (C_range/2)])
            ax_1ch.plot(pd.to_datetime(t_1ch, utc=True), d_1ch, color='r')
            ax_2ch.plot(pd.to_datetime(t_1ch, utc=True), d_2ch, color='g')
            ax_3ch.plot(pd.to_datetime(t_1ch, utc=True), d_3ch, color='b')
            ax_4ch.plot(pd.to_datetime(t_1ch, utc=True), d_4ch, color='k')

            ax_1ch.set_title('(JST) ' + 'magnetic force(nT)' + C_mode +"range="+ str(C_range) +"rate="+ str(get_Srate(df[0])))
            plt.pause(0.01)

def measurement(plotData,C_save,C_Drate):
    #1007B:1029A:1024A:LM60
    slope = [6.041297912, 6.032822234, 6.024782582, 1.004970735]
    intercept = [-15.21584595, -15.20405742, -15.17129194, -0.000415594]
    transform = [0.16*0.001, 0.16*0.001, 0.16*0.001, 6.25*0.001]
    off_set = [0,0,0,424*0.001]
    # 描画するデータ 
    now = datetime.datetime.now(timezone.utc)
    plotData.append(['{0:%Y-%m-%d }'.format(now),
    'Magnetic force(nT)_1ch','Magnetic force(nT)_2ch',
    'Magnetic force(nT)_3ch','Magnetic force(nT)_4ch']) 
    ads = ADS1256()
    ads.drate = (DRATE_100 if C_Drate == 100 else
    DRATE_500 if C_Drate == 500 else
    DRATE_1000 if C_Drate == 1000 else
    DRATE_2000)
    ads.pga_gain = 1
    ads.cal_self()

    with open('./data/MI{0:%y-%m-%d_%Hh%Mm%Ss}.csv'.format(now),'w', newline="") as f:
        saveData = ['{0:%Y-%m-%d }'.format(now),
        'Magnetic force(nT)_1ch','Magnetic force(nT)_2ch',
        'Magnetic force(nT)_3ch','Magnetic force(nT)_4ch']
        writer = csv.writer(f)
        writer.writerow(saveData)
        counter = 0
        while True:
            now = datetime.datetime.now(timezone.utc)
            #### get data ####
            raw_channels = ads.read_sequence(CH_SEQUENCE)
            # raw_channels = ads.read_continue(CH_SEQUENCE)
            voltages = [i * ads.v_per_digit for i in raw_channels]
            voltages_15 = [(voltages[i] * slope[i] + intercept[i]) for i in range(4)]
            MagF = [((voltages_15[i] - off_set[i]) / transform[i]) for i in range(4)]
            #### test ####
            #sleep(0.1)
            #MagF = [8 + random.random(),8 + random.random(),8 + random.random(),2 + random.random()]
            ##############
            plotData.append(['{0:%H:%M:%S.%f}'.format(now), MagF[0], MagF[1], MagF[2], MagF[3]])
            saveData = ['{0:%H:%M:%S.%f}'.format(now), MagF[0], MagF[1], MagF[2], MagF[3]]
            writer = csv.writer(f)
            writer.writerow(saveData)
            counter += 1
            if counter >= PLOT_DATA_NUM:
                plotData.pop(1)
                counter -= 1
            
def test(plotData):
    while True:
        sleep(2)
        print("test")
        print(plotData)

def show_graph(C_save,C_range,C_mode,C_Drate):
    with Manager() as manager:
        plotData = manager.list()
        logger = Process(target=measurement,args=[plotData,C_save,C_Drate])
        plotter = Process(target=ploting,args=[plotData,C_save,C_range,C_mode,C_Drate])
        # tester = Process(target=test,args=[plotData])
        print('logger start!!!!')
        logger.start()
        plotter.start()
        # tester.start()
        # tester.join()
        logger.join()
        plotter.join()
        print(plotData[990])

def main():
    while True:#set config
        #print("Do you want to save the observation data?(yes/no)")
        #config_save = input('>> ')
        config_save = "yes"
        print("Set the graph parameters to be displayed. \nEnter the magnetic Force range.(nT,10-80000)")
        config_range = int(input('>> '))
        # print("Select graph to display(raw/filter)")
        config_mode = "raw"
        #config_mode = "raw"
        print("Set DRATE(2000/1000/500)")
        config_Drate = int(input('>> '))

        if config_save == "yes" or config_save == "no":
            if 10 <= config_range <= 80000:
                break
        print("######input errer#######\ntry again!!")
    show_graph(config_save,config_range,config_mode,config_Drate)

if __name__ == '__main__':
    main()