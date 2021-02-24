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
from statistics import mode
from decimal import Decimal, ROUND_HALF_UP
import collections

from sklearn.decomposition import FastICA
from sklearn.decomposition import PCA

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000
oldData = False

def eliminate_f(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
        return date.strftime('%H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d %H:%M:%S')

def add_day(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    date = date + datetime.timedelta(days=1)
    return date.strftime('%Y-%m-%d ')


def format_to_day(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date.strftime('%Y-%m-%d ')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d ')  

def format_to_day_T(date_timestamp):
    try:
        date = date_timestamp
        return date.strftime('%Y-%m-%d ')
    except ValueError:
        date = datetime.datetime.strptime(date_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d ')        

def search_start(dataTime,start_dataTime_str):
    i = 0
    while i < len(dataTime):
        check_dataTime_str = eliminate_f(dataTime[i])
        if check_dataTime_str == start_dataTime_str:
            return i
        i += 1
    return -1

def search_end(dataTime,end_dataTime_str,start_arg):
    i = start_arg
    while i < len(dataTime):
        check_dataTime_str = eliminate_f(dataTime[i])
        if check_dataTime_str == end_dataTime_str:
            next_check_dataTime_str = eliminate_f(dataTime[i+1])
            if next_check_dataTime_str != end_dataTime_str:
                return i
        i += 1
    return -1

def rawdata_maker(f,start_dataTime_str,end_dataTime_str,offset=0):
    df_list_raw = {'Time':[],'ch1':[],'ch2':[],'ch3':[],'ch4':[]}
    startFlag = False
    endFlagNum = False
    dataday = format_to_day(start_dataTime_str)
    num = 1
    if offset < 0:
        num = -1
    for row in f:#row is list
        time_Date = datetime.datetime.strptime(row[0], '%H:%M:%S.%f') + datetime.timedelta(seconds=offset)
        time_Str = time_Date.strftime('%H:%M:%S.%f')
        if startFlag == False:
            if (dataday + eliminate_f(time_Str)) == start_dataTime_str:
                print("START")
                startFlag = True
        if startFlag == True:
            if (dataday + eliminate_f(time_Str)) == end_dataTime_str:
                endFlagNum = True
        if endFlagNum == True:
            if (dataday + eliminate_f(time_Str)) != end_dataTime_str:
                print("END")
                endFlagNum = False
                startFlag = False
                break
        
        if startFlag == True:
            df_list_raw['Time'].append(dataday + time_Str)
            df_list_raw['ch1'].append(float(row[1]))
            df_list_raw['ch2'].append(float(row[2]))
            df_list_raw['ch3'].append(float(row[3])*num)
            df_list_raw['ch4'].append(float(row[4]))
    return df_list_raw['Time'],df_list_raw['ch1'],df_list_raw['ch2'],df_list_raw['ch3'],df_list_raw['ch4']

def append_lists(l1,l2,l3,l4,dat1,dat2,dat3,dat4):
    l1.append(dat1)
    l2.append(dat2)
    l3.append(dat3)
    l4.append(dat4)
    return l1, l2, l3, l4

def my_round(num,dec=0.1):
    out_str = Decimal(str(num)).quantize(Decimal(str(dec)), rounding=ROUND_HALF_UP)
    return float(out_str)

def list_round(l):
    out_list = []
    for i in l:
        out_list.append(my_round(i))
    return out_list

def test_plot(x):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(611)
    ax_2ch = fig.add_subplot(612)
    ax_3ch = fig.add_subplot(613)
    ax_4ch = fig.add_subplot(614)
    ax_5ch = fig.add_subplot(615)
    ax_6ch = fig.add_subplot(616)
    ax_1ch.plot(x[0], color = 'r')
    ax_2ch.plot(x[1], color = 'b')
    ax_3ch.plot(x[2], color = 'g')
    ax_4ch.plot(x[3], color = 'm')
    ax_5ch.plot(x[4], color = 'c')
    ax_6ch.plot(x[5], color = 'y')
    fig.tight_layout()
    plt.show()

def search_maxmin(pd_data, mode_num):
    if mode_num == 0:
        max_ = pd_data.max()
        max_index = pd_data.idxmax()
        max_ave = pd_data[max_index-30:max_index+30].mean()
        if abs(max_ - max_ave) < 1:
            return max_index
        else:
            for i in range(60):
                pd_data.at[max_index-30+i] = -80000
            return search_maxmin(pd_data,mode_num)
    else:
        min_ = pd_data.min()
        min_index = pd_data.idxmin()
        min_ave = pd_data[min_index-30:min_index+30].mean()
        if abs(min_ - min_ave) < 1:
            return min_index
        else:
            for i in range(60):
                pd_data.at[min_index-30+i] = 80000
            return search_maxmin(pd_data,mode_num)

def fig_plot2(df_print,labelList, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(16, 6))
    ax_1ch = fig.add_subplot(321)
    ax_2ch = fig.add_subplot(323)
    ax_3ch = fig.add_subplot(325)
    ax_4ch = fig.add_subplot(322)
    ax_5ch = fig.add_subplot(324)
    ax_6ch = fig.add_subplot(326)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_5ch.yaxis.grid(True)
    ax_6ch.yaxis.grid(True)
    ax_1ch.set_ylabel(labelList[0])
    ax_2ch.set_ylabel(labelList[1])
    ax_3ch.set_ylabel(labelList[2])
    ax_4ch.set_ylabel(labelList[3])
    ax_5ch.set_ylabel(labelList[4])
    ax_6ch.set_ylabel(labelList[5])
    # ax_9ch.set_ylabel(labelList[8], fontsize=18)

    #### plot line color ####
    ax_1ch.plot(df_print[0]['time'], df_print[0]['1ch'], color = 'r')
    ax_2ch.plot(df_print[0]['time'], df_print[0]['2ch'], color = 'b')
    ax_3ch.plot(df_print[0]['time'], df_print[0]['3ch'], color = 'g')
    ax_4ch.plot(df_print[1]['time'], df_print[1]['1ch'], color = 'r')
    ax_5ch.plot(df_print[1]['time'], df_print[1]['2ch'], color = 'b')
    ax_6ch.plot(df_print[1]['time'], df_print[1]['3ch'], color = 'g')
    #### plot grid ####
    ax_1ch.xaxis.grid(True)
    ax_2ch.xaxis.grid(True)
    ax_3ch.xaxis.grid(True)
    ax_4ch.xaxis.grid(True)
    ax_5ch.xaxis.grid(True)
    ax_6ch.xaxis.grid(True)
    #### plot Y axis limit ####
    if Yrange != 0:
        median_1ch = np.median(df_print[0]['1ch'])
        median_2ch = np.median(df_print[0]['2ch'])
        median_3ch = np.median(df_print[0]['3ch'])
        median_4ch = np.median(df_print[1]['1ch'])
        median_5ch = np.median(df_print[1]['2ch'])
        median_6ch = np.median(df_print[1]['3ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])
        ax_5ch.set_ylim([median_5ch - (Yrange/2),median_5ch + (Yrange/2)])
        ax_6ch.set_ylim([median_6ch - (Yrange/2),median_6ch + (Yrange/2)])
    
    ax_1ch.get_yaxis().get_major_formatter().set_useOffset(False)# X軸の数字をオフセットを使わずに表現する
    ax_2ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_3ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_4ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_5ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_6ch.get_yaxis().get_major_formatter().set_useOffset(False)
 
    #### plot X axis justified ####
    ax_1ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_2ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_3ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_4ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_5ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_6ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    #### plot X label print format ####
    strings = '%H:%M'
    # strings = '%d'
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    ax_3ch.xaxis.set_major_formatter(mpl.dates.DateFormatter(strings))
    ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter(strings))
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H'))
    time_scale = False
    if time_scale == True:
        # x = ['2020-10-04 00:00:00','2020-10-08 00:00:00','2020-10-12 00:00:00','2020-10-16 00:00:00','2020-10-20 00:00:00',]
        x_axis = ['19:10:00','19:12:00','19:14:00','19:16:00','19:18:00','19:20:00']
        x = []
        print(":type:"+ str(type(df_print[0]['time'][0])))
        for s in x_axis:
            x.append(format_to_day_T(df_print[0]['time'][0]) + s)
        # x.append(add_day(format_to_day_T(df_print['time'][0]) + '00:00:00'))
        x_axis_np = pd.to_datetime(np.array(x))
        ax_1ch.set_xticks(x_axis_np)
        ax_2ch.set_xticks(x_axis_np)
        ax_3ch.set_xticks(x_axis_np)
        ax_4ch.set_xticks(x_axis_np)
        ax_5ch.set_xticks(x_axis_np)
        ax_6ch.set_xticks(x_axis_np)
        
    #### show only X label of bottom graph #### 
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    # plt.setp(ax_3ch.get_xticklabels(),visible=False)
    plt.setp(ax_4ch.get_xticklabels(),visible=False)
    plt.setp(ax_5ch.get_xticklabels(),visible=False)

    if dat_path != '':    
        df_print.to_csv(dat_path)
    # plt.suptitle(title)
    # plt.subplots_adjust(top=0.7) # 図と被ってしまうので少し上を空ける
    # ax_4ch.set_title("")
    fig.tight_layout()    #文字が重ならないよう調整
    fig.align_labels()    #軸ラベルを揃える
    plt.savefig(fig_path)
    plt.close()

def fig_plot3(df_print,labelList, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(16, 6))
    ax_1ch = fig.add_subplot(331)
    ax_2ch = fig.add_subplot(334)
    ax_3ch = fig.add_subplot(337)
    ax_4ch = fig.add_subplot(332)
    ax_5ch = fig.add_subplot(335)
    ax_6ch = fig.add_subplot(338)
    ax_7ch = fig.add_subplot(333)
    ax_8ch = fig.add_subplot(336)
    ax_9ch = fig.add_subplot(339)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_5ch.yaxis.grid(True)
    ax_6ch.yaxis.grid(True)
    ax_7ch.yaxis.grid(True)
    ax_8ch.yaxis.grid(True)
    ax_9ch.yaxis.grid(True)
    # ax_1ch.tick_params(labelsize=18)
    # ax_2ch.tick_params(labelsize=18)
    # ax_3ch.tick_params(labelsize=18)
    # ax_4ch.tick_params(labelsize=18)
    # ax_5ch.tick_params(labelsize=18)
    # ax_6ch.tick_params(labelsize=18)
    # ax_7ch.tick_params(labelsize=18)
    # ax_8ch.tick_params(labelsize=18)
    # ax_9ch.tick_params(labelsize=18)
    if len(labelList) != 9:
        labelList = ['X of MIM-Pi No1 [nT]','Y of MIM-Pi No1 [nT]',
        'Z of MIM-Pi No1 [nT]','X of MIM-Pi No2 [nT]',
        'Y of MIM-Pi No2 [nT]','Z of MIM-Pi No2 [nT]',
        'X of Fluxgate [nT]','Y of Fluxgate [nT]','Z of Fluxgate [nT]']
    ax_1ch.set_ylabel(labelList[0])
    ax_2ch.set_ylabel(labelList[1])
    ax_3ch.set_ylabel(labelList[2])
    ax_4ch.set_ylabel(labelList[3])
    ax_5ch.set_ylabel(labelList[4])
    ax_6ch.set_ylabel(labelList[5])
    ax_7ch.set_ylabel(labelList[6])
    ax_8ch.set_ylabel(labelList[7])
    ax_9ch.set_ylabel(labelList[8])
    # ax_9ch.set_ylabel(labelList[8], fontsize=18)

    #### plot line color ####
    ax_1ch.plot(df_print[0]['time'], df_print[0]['1ch'], color = 'r')
    ax_2ch.plot(df_print[0]['time'], df_print[0]['2ch'], color = 'b')
    ax_3ch.plot(df_print[0]['time'], df_print[0]['3ch'], color = 'g')
    ax_4ch.plot(df_print[1]['time'], df_print[1]['1ch'], color = 'r')
    ax_5ch.plot(df_print[1]['time'], df_print[1]['2ch'], color = 'b')
    ax_6ch.plot(df_print[1]['time'], df_print[1]['3ch'], color = 'g')
    ax_7ch.plot(df_print[2]['time'], df_print[2]['1ch'], color = 'r')
    ax_8ch.plot(df_print[2]['time'], df_print[2]['2ch'], color = 'b')
    ax_9ch.plot(df_print[2]['time'], df_print[2]['3ch'], color = 'g')
    
    time_scale = True
    if time_scale == True:
    #### max line ####
        value_2chmaxIndex = search_maxmin(df_print[0]['2ch'],0)
        value_2chmax = df_print[0]['2ch'][value_2chmaxIndex]
        value_2chmaxAve = df_print[0]['2ch'][value_2chmaxIndex-30:value_2chmaxIndex+30].mean()
        value_5chmaxIndex = search_maxmin(df_print[1]['2ch'],0)
        value_5chmax = df_print[1]['2ch'][value_5chmaxIndex]
        value_5chmaxAve = df_print[1]['2ch'][value_5chmaxIndex-30:value_5chmaxIndex+30].mean()
        value_8chmaxIndex = search_maxmin(df_print[2]['2ch'],0)
        value_8chmax = df_print[2]['2ch'][value_8chmaxIndex]
        value_8chmaxAve = df_print[2]['2ch'][value_8chmaxIndex-30:value_8chmaxIndex+30].mean()
        ax_2ch.axhline(value_2chmax, ls = "-.", color = "magenta")
        ax_2ch.text(0.05, 0.9, "Max="+'{:.1f}'.format(value_2chmax)+" MaxAve="+'{:.1f}'.format(value_2chmaxAve), size=11, transform= ax_2ch.transAxes)
        ax_5ch.axhline(value_5chmax, ls = "-.", color = "magenta")
        ax_5ch.text(0.05, 0.9, "Max="+'{:.1f}'.format(value_5chmax)+" MaxAve="+'{:.1f}'.format(value_5chmaxAve), size=11, transform= ax_5ch.transAxes)
        ax_8ch.axhline(value_8chmax, ls = "-.", color = "magenta")
        ax_8ch.text(0.05, 0.9, "Max="+'{:.1f}'.format(value_8chmax)+" MaxAve="+'{:.1f}'.format(value_8chmaxAve), size=11, transform= ax_8ch.transAxes)
    #### min line ####
        value_2chminIndex = search_maxmin(df_print[0]['2ch'],1)
        value_2chmin = df_print[0]['2ch'][value_2chminIndex]
        value_2chminAve = df_print[0]['2ch'][value_2chminIndex-30:value_2chminIndex+30].mean()
        value_5chminIndex = search_maxmin(df_print[1]['2ch'],1)
        value_5chmin = df_print[1]['2ch'][value_5chminIndex]
        value_5chminAve = df_print[1]['2ch'][value_5chminIndex-30:value_5chminIndex+30].mean()
        value_8chminIndex = search_maxmin(df_print[2]['2ch'],1)
        value_8chmin = df_print[2]['2ch'][value_8chminIndex]
        value_8chminAve = df_print[2]['2ch'][value_8chminIndex-30:value_8chminIndex+30].mean()
        ax_2ch.axhline(value_2chmin, ls = "-.", color = "magenta")
        ax_2ch.text(0.05, 0.03, "Min="+'{:.1f}'.format(value_2chmin)+" MinAve="+'{:.1f}'.format(value_2chminAve), size=11, transform= ax_2ch.transAxes)
        ax_5ch.axhline(value_5chmin, ls = "-.", color = "magenta")
        ax_5ch.text(0.05, 0.03, "Min="+'{:.1f}'.format(value_5chmin)+" MinAve="+'{:.1f}'.format(value_5chminAve), size=11, transform= ax_5ch.transAxes)
        ax_8ch.axhline(value_8chmin, ls = "-.", color = "magenta")
        ax_8ch.text(0.05, 0.03, "Min="+'{:.1f}'.format(value_8chmin)+" MinAve="+'{:.1f}'.format(value_8chminAve), size=11, transform= ax_8ch.transAxes)

    #### plot grid ####
    ax_1ch.xaxis.grid(True)
    ax_2ch.xaxis.grid(True)
    ax_3ch.xaxis.grid(True)
    ax_4ch.xaxis.grid(True)
    ax_5ch.xaxis.grid(True)
    ax_6ch.xaxis.grid(True)
    ax_7ch.xaxis.grid(True)
    ax_8ch.xaxis.grid(True)
    ax_9ch.xaxis.grid(True)
    #### plot Y axis limit ####
    if Yrange != 0:
        median_1ch = np.median(df_print[0]['1ch'])
        median_2ch = np.median(df_print[0]['2ch'])
        median_3ch = np.median(df_print[0]['3ch'])
        median_4ch = np.median(df_print[1]['1ch'])
        median_5ch = np.median(df_print[1]['2ch'])
        median_6ch = np.median(df_print[1]['3ch'])
        median_7ch = np.median(df_print[2]['1ch'])
        median_8ch = np.median(df_print[2]['2ch'])
        median_9ch = np.median(df_print[2]['3ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])
        ax_5ch.set_ylim([median_5ch - (Yrange/2),median_5ch + (Yrange/2)])
        ax_6ch.set_ylim([median_6ch - (Yrange/2),median_6ch + (Yrange/2)])
        ax_7ch.set_ylim([median_7ch - (Yrange/2),median_7ch + (Yrange/2)])
        ax_8ch.set_ylim([median_8ch - (Yrange/2),median_8ch + (Yrange/2)])
        ax_9ch.set_ylim([median_9ch - (Yrange/2),median_9ch + (Yrange/2)])
    
    ax_1ch.get_yaxis().get_major_formatter().set_useOffset(False)# X軸の数字をオフセットを使わずに表現する
    ax_2ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_3ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_4ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_5ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_6ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_7ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_8ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_9ch.get_yaxis().get_major_formatter().set_useOffset(False)
 
    #### plot X axis justified ####
    ax_1ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_2ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_3ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_4ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_5ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_6ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_7ch.set_xlim([df_print[2]['time'][0],df_print[2]['time'][len(df_print[2]['time'])-1]])
    ax_8ch.set_xlim([df_print[2]['time'][0],df_print[2]['time'][len(df_print[2]['time'])-1]])
    ax_9ch.set_xlim([df_print[2]['time'][0],df_print[2]['time'][len(df_print[2]['time'])-1]])
    #### plot X label print format ####
    strings = '%H:%M'
    # strings = '%m%d'
    # strings = '%d'
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    ax_3ch.xaxis.set_major_formatter(mpl.dates.DateFormatter(strings))
    ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter(strings))
    ax_9ch.xaxis.set_major_formatter(mpl.dates.DateFormatter(strings))
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H'))
    
    if time_scale == True:
        # x = ['2020-10-04 00:00:00','2020-10-08 00:00:00','2020-10-12 00:00:00','2020-10-16 00:00:00','2020-10-20 00:00:00',]
        # x_axis = ['19:10:00','19:12:00','19:14:00','19:16:00','19:18:00','19:20:00']
        x_axis = ['00:00:00','03:00:00','06:00:00','09:00:00','12:00:00','15:00:00','18:00:00','21:00:00']
        x = []
        print(":type:"+ str(type(df_print[0]['time'][0])))
        for s in x_axis:
            x.append(format_to_day_T(df_print[0]['time'][0]) + s)
        x.append(add_day(format_to_day_T(df_print[0]['time'][0]) + '00:00:00'))
        x_axis_np = pd.to_datetime(np.array(x))
        ax_1ch.set_xticks(x_axis_np)
        ax_2ch.set_xticks(x_axis_np)
        ax_3ch.set_xticks(x_axis_np)
        ax_4ch.set_xticks(x_axis_np)
        ax_5ch.set_xticks(x_axis_np)
        ax_6ch.set_xticks(x_axis_np)
        ax_7ch.set_xticks(x_axis_np)
        ax_8ch.set_xticks(x_axis_np)
        ax_9ch.set_xticks(x_axis_np)
        
    #### show only X label of bottom graph #### 
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    # plt.setp(ax_3ch.get_xticklabels(),visible=False)
    plt.setp(ax_4ch.get_xticklabels(),visible=False)
    plt.setp(ax_5ch.get_xticklabels(),visible=False)
    plt.setp(ax_7ch.get_xticklabels(),visible=False)
    plt.setp(ax_8ch.get_xticklabels(),visible=False)

    if dat_path != '':    
        df_print.to_csv(dat_path)
    # plt.suptitle(title)
    # plt.subplots_adjust(top=0.7) # 図と被ってしまうので少し上を空ける
    # ax_4ch.set_title("")
    fig.tight_layout()    #文字が重ならないよう調整
    fig.align_labels()    #軸ラベルを揃える
    plt.savefig(fig_path)
    plt.close()

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def rewrite_day(reference_date,num):
    day = int(reference_date[8:10])
    hour = int(reference_date[11:13]) + num
    if hour >= 24:
        hour -= 24
        day += 1 #Here, we do not consider DAY overflow
    return reference_date[0:8] + '{0:02d}'.format(day) + ' ' + '{0:02d}'.format(hour) + reference_date[13:19]

def crop_str(str1,target,mode=0):
    for i in range(len(str1)):
        if str1[i] == target:
            if mode == 0:
                return str1[i+1:len(str1)]
            else:
                return str1[0:i]

def check_errerData(date_numpy,start_datetime):
    errer_index = []
    NaN_date = []
    sec = 0
    for i in range(len(date_numpy)):
        # print([date_numpy[i], (start_datetime + datetime.timedelta(seconds=sec))])
        if date_numpy[i] == (start_datetime + datetime.timedelta(seconds=sec)):
            sec += 1
        elif date_numpy[i] < (start_datetime + datetime.timedelta(seconds=sec)):
            errer_index.append(i)
        elif date_numpy[i] > (start_datetime + datetime.timedelta(seconds=sec)):
            diff = date_numpy[i] - (start_datetime + datetime.timedelta(seconds=sec))
            NaN_date.append(start_datetime + datetime.timedelta(seconds=sec))
            sec += int(diff.total_seconds()) + 1
            print(int(diff.total_seconds()))
    return errer_index,NaN_date

def Process(fileName,StartTime,EndTime, F_flag ,Yrange):
    siteInfo = ""
    df_print = []
    for i in range(3):
        Pass = "/nas5/users/nomura/"
        FsiteInfo = "@"+crop_str(crop_str(fileName[i],"@"),".",mode=1)
        if FsiteInfo == "@inabu_Flux":
            Pass += "jst_1sec_FGM@inabu/" + fileName[i]
        elif FsiteInfo == "@inabu_byNo1":
            Pass += "jst_1sec_MIM-Pi1@inabu/" + fileName[i]
        elif FsiteInfo == "@inabu_byNo2":
            Pass += "jst_1sec_MIM-Pi2@inabu/" + fileName[i]
        siteInfo += "@" + crop_str(crop_str(fileName[i],"@"),".",mode=1)
        csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
        f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        header = next(f)
        print(header)
        start_time_str = header[0] + ' ' + StartTime
        end_time_str = header[0] + ' ' + EndTime
        if i == -1:
            offset_sec = -1
        else:
            offset_sec = 0
        rawdata = rawdata_maker(f,start_time_str,end_time_str,offset=offset_sec)
        csv_file.close()
        rawtime = pd.to_datetime(rawdata[0])
        print(rawtime)
        errer_index, NaN_data = check_errerData(rawtime,rawtime[0])
        errer_index.reverse()
        for i in errer_index:
            rawdata[0].pop(i)
            rawdata[1].pop(i)
            rawdata[2].pop(i)
            rawdata[3].pop(i)
            rawdata[4].pop(i)
        rawtime = pd.to_datetime(rawdata[0])
        raw1ch = np.array(rawdata[1])
        raw2ch = np.array(rawdata[2])
        raw3ch = np.array(rawdata[3])
        raw4ch = np.array(rawdata[4])
        rawdata = []
        df_print.append(pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch}))

    if oldData == True:
        df_print[1]['2ch'] = df_print[1]['3ch']
        df_print[1]['3ch'] = df_print[2]['2ch']
    
    fig_date = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    # fig_dir = './fig/AGU_10min/' + fig_date.strftime('%Y-%m-%d') + siteInfo
    fig_dir = './fig/Inabu_Sq_jst'
    figFileDate = fig_date.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S')
    my_makedirs(fig_dir)
    title = start_time_str + '(UT) magnetic force(nT)' + F_flag + siteInfo
    #### graph print ####
    if F_flag == "median2sig":
        labelList = ["X [nT]","Y [nT]","Z [nT]","X [nT]","Y [nT]","Z [nT]"]
        fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        fig_plot2(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

        Yrange = int(Yrange / 2)
        fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        fig_plot2(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

        Yrange = 0
        fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        fig_plot2(df_print,labelList,title, fig_path,F_flag, Yrange=0)    
    else:
        my_makedirs(fig_dir+"/" + str(Yrange) + 'nt/')
        labelList = ["X [nT]","Y [nT]","Z [nT]","X [nT]","Y [nT]","Z [nT]","X [nT]","Y [nT]","Z [nT]"]
        fig_path = fig_dir+"/" + str(Yrange) + 'nt/' + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        fig_plot3(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

        # Yrange = int(Yrange / 2)
        # my_makedirs(fig_dir + str(Yrange) + 'nt/')
        # fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        # fig_plot3(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

        # Yrange = 0
        # my_makedirs(fig_dir + str(Yrange) + 'nt/')
        # fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        # fig_plot3(df_print,labelList,title, fig_path,F_flag, Yrange=0)

def Process_long(fileName,F_flag ,Yrange):
    #### initialize ####
    siteInfo = ""
    df_print = []
    for j in range(3):
        buff_time = []
        buff_1ch = []
        buff_2ch = []
        buff_3ch = []
        buff_4ch = []
        siteInfo +="@"+crop_str(crop_str(fileName[j][0],"@"),".",mode=1)
        dirPass = "/nas5/users/nomura/"
        FsiteInfo = "@"+crop_str(crop_str(fileName[j][0],"@"),".",mode=1)
        if FsiteInfo == "@inabu_Flux":
            dirPass += "1sec_FGM@inabu/"
        elif FsiteInfo == "@inabu_byNo1":
            dirPass += "1sec_MIM-Pi1@inabu/"
        elif FsiteInfo == "@inabu_byNo2":
            dirPass += "1sec_MIM-Pi2@inabu/"
        for i in range(len(fileName[j])):
            Pass = dirPass + fileName[j][i]
            csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
            f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
            header = next(f)
            print(header)
            start_time_str = header[0] + ' 00:00:00'
            if i == len(fileName[j])-1:
                end_time_str = header[0] + ' 23:00:00'
            else:
                end_time_str = header[0] + ' 23:59:59'
            if j == 4:
                Dray = -1
            else:
                Dray = 0
            rawdata = rawdata_maker(f,start_time_str,end_time_str,Dray)
            rawtime = pd.to_datetime(rawdata[0])
            # print(rawtime)
            errer_index, NaN_date = check_errerData(rawtime,rawtime[0])
            print("errer index amount = ",len(errer_index))
            print("NaN index amount = ",len(NaN_date))
            errer_index.reverse()
            for i in errer_index:
                rawdata[0].pop(i)
                rawdata[1].pop(i)
                rawdata[2].pop(i)
                rawdata[3].pop(i)
                rawdata[4].pop(i)
            rawtime = pd.to_datetime(rawdata[0])
            # print(rawtime)
            #### joint ####
            buff_time = buff_time + rawdata[0]
            buff_1ch = buff_1ch + rawdata[1]
            buff_2ch = buff_2ch + rawdata[2]
            buff_3ch = buff_3ch + rawdata[3]
            buff_4ch = buff_4ch + rawdata[4]
        rawtime = pd.to_datetime(buff_time)
        raw1ch = np.array(buff_1ch)
        raw2ch = np.array(buff_2ch)
        raw3ch = np.array(buff_3ch)
        raw4ch = np.array(buff_4ch)

        df_print.append(pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch}))
    
    if oldData == True:
        df_print[1]['2ch'] = df_print[1]['3ch']
        df_print[1]['3ch'] = df_print[2]['2ch']
    
    fig_dir = './fig/LongTarm/'
    figFileDate = rawtime[0].strftime('%Y-%m-%d_%H%M%S') + rawtime[-1].strftime('-%Y-%m-%d_%H%M%S')
    my_makedirs(fig_dir)
    title = start_time_str + '(UT) magnetic force(nT)' + F_flag + siteInfo
    #### graph print ####
    for i in range(4):
        Yrange -= (i*10)
        my_makedirs(fig_dir + str(Yrange) + 'nt/')
        labelList = ["X [nT]","Y [nT]","Z [nT]","X [nT]","Y [nT]","Z [nT]","X [nT]","Y [nT]","Z [nT]"]
        fig_path = fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
        fig_plot3(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))
    
    # Yrange_ori = Yrange
    # Yrange = int(Yrange_ori*2/3)
    # my_makedirs(fig_dir + str(Yrange) + 'nt/')
    # fig_path = fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    # fig_plot3(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

    # Yrange = int(Yrange_ori / 3)
    # my_makedirs(fig_dir + str(Yrange) + 'nt/')
    # fig_path = fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    # fig_plot3(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

    # Yrange = 0
    # my_makedirs(fig_dir + str(Yrange) + 'nt/')
    # fig_path = fig_dir + '0nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    # fig_plot3(df_print,labelList,title, fig_path,F_flag, Yrange=0)

def cal_time(ProcessTime,mode,sec):
    before = datetime.datetime.strptime(ProcessTime,"%H:%M:%S")
    if mode == "add":
        after = before + datetime.timedelta(seconds=sec)
    elif mode == "sub":
        after = before - datetime.timedelta(seconds=sec)
    return after.strftime("%H:%M:%S")

def day_1hour(File, f_type, Yrange):
    ProcessTime = "00:00:00"
    for i in range(24):
        # print(ProcessTime)
        if i != 23:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",60*60),f_type,Yrange)
        else:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",59*60+59),f_type,Yrange)
        ProcessTime = cal_time(ProcessTime,"add",60*60)

def day_10min(File, f_type, Yrange):
    ProcessTime = "00:00:00"
    for i in range(144):
        # print(ProcessTime)
        if i != 143:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",10*60),f_type,Yrange)
        else:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",9*60+59),f_type,Yrange)
        ProcessTime = cal_time(ProcessTime,"add",10*60)

def countUP_filename(F_str,Num,day):
    if Num == 3:
        F_date = datetime.datetime.strptime(F_str,"Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
    else:
        try:
            F_date = datetime.datetime.strptime(F_str,"MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
            F_date += datetime.timedelta(days=day)
            return F_date.strftime("MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
        except ValueError:
            F_date = datetime.datetime.strptime(F_str,"1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
            F_date += datetime.timedelta(days=day)
            return F_date.strftime("1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")

def main():
    #### Input Example ####
    # File = [
    # "MI20-11-10_00h00m00s@inabu_byNo1.csv",
    # "MI20-11-10_00h00m00s@inabu_byNo2.csv",
    # "Fx20-11-10_00h00m00s@inabu_Flux.csv"]
    File = [
    "1sec_median_MI21-01-17_00h00m00s@inabu_byNo1.csv",
    "1sec_median_MI21-01-17_00h00m00s@inabu_byNo2.csv",
    "1sec_median_MI21-01-17_00h00m00s@inabu_byNo2.csv"]
    File2 = [
    "1sec_median_MI20-10-04_00h00m00s@inabu_byNo1.csv",
    "1sec_median_MI20-10-04_00h00m00s@inabu_byNo2.csv",
    "Fx20-10-04_00h00m00s@inabu_Flux.csv"]
    File3 = [
    "1sec_median_MI20-06-19_00h00m00s@inabu_byNo1.csv",
    "Fx20-06-19_00h00m00s@inabu_Flux.csv",
    "Fx20-06-19_00h00m00s@inabu_Flux.csv"]

    File_list1 = []
    File_list2 = []
    File_list3 = []
    # for i in range(7):
    #     File_list1.append(countUP_filename(File3[0],1,i))
    #     File_list2.append(countUP_filename(File3[1],3,i))
    #     File_list3.append(countUP_filename(File3[1],3,i))

    for i in range(30):
        File_list1.append(countUP_filename(File[0],1,i))
        File_list2.append(countUP_filename(File[1],2,i))
        File_list3.append(countUP_filename(File[1],2,i))
        # print(countUP_filename(File[2],2,i))
    for i in range(55):
        File_list1.append(countUP_filename(File2[0],1,i))
        File_list2.append(countUP_filename(File2[1],2,i))
        File_list3.append(countUP_filename(File2[2],3,i))
    #     print(countUP_filename(File2[1],2,i))

    for i in range(85):
        # File_list1 = []
        # File_list2 = []
        # File_list3 = []

        # File_list1.append(countUP_filename(File[0],1,i))
        # File_list2.append(countUP_filename(File[1],2,i))
        # File_list3.append(countUP_filename(File[2],3,i))
        # Process_long([File_list1,File_list2,File_list3],"median",125)
        try:
            Process([File_list1[i],File_list2[i],File_list3[i]],"00:00:00","23:59:59","median",125)
        except:
            print("ERROR  =  "+File_list1[i])
        # Process([File_list1[i],File_list2[i],File_list3[i]],"15:30:00","16:30:00","median",10)
        # Process([File_list1[i],File_list2[i],File_list3[i]],"21:30:00","23:30:00","median",10)
        # day_10min([File_list1[i],File_list2[i],File_list3[i]],"median",10)
            
    # Process([File[0],File[1],File[2]],"00:00:00","00:59:59","median",125)
    # Process_long([File_list1,File_list2,File_list3],"median",160)
 

if __name__ == '__main__':
    main()