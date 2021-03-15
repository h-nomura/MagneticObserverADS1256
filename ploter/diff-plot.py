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
from sklearn import linear_model #線形単回帰分析
import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

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

def rawdata_maker(f,start_dataTime_str,end_dataTime_str):
    df_list_raw = {'Time':[],'ch1':[],'ch2':[],'ch3':[],'ch4':[]}
    startFlag = False
    endFlagNum = False
    dataday = format_to_day(start_dataTime_str)
    for row in f:#row is list
        if startFlag == False:
            if (dataday + eliminate_f(row[0])) == start_dataTime_str:
                print("START")
                startFlag = True
        if startFlag == True:
            if (dataday + eliminate_f(row[0])) == end_dataTime_str:
                endFlagNum = True
        if endFlagNum == True:
            if (dataday + eliminate_f(row[0])) != end_dataTime_str:
                print("END")
                endFlagNum = False
                startFlag = False
                break
        
        if startFlag == True:
            df_list_raw['Time'].append(dataday + row[0])
            df_list_raw['ch1'].append(float(row[1]))
            df_list_raw['ch2'].append(float(row[2]))
            df_list_raw['ch3'].append(float(row[3]))
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

def fit_timecode(df_print):
    a = 0
    b = 1
    print("time",len(df_print[0]['time']),len(df_print[1]['time']))
    print("1ch",len(df_print[0]['1ch']),len(df_print[1]['1ch']))
    print("2ch",len(df_print[0]['2ch']),len(df_print[1]['2ch']))
    print("3ch",len(df_print[0]['3ch']),len(df_print[1]['3ch']))
    print("4ch",len(df_print[0]['4ch']),len(df_print[1]['4ch']))
    
    if len(df_print[0]['time']) >= len(df_print[1]['time']):
        num = len(df_print[1]['time'])
        a = 1
        b = 0
    else:
        num = len(df_print[0]['time'])
        a = 0
        b = 1
    arg_list = []
    count = 0
    # for i in [65019,65020,65021,65022,65023]:
    #     print(i,df_print[a]['time'][i],df_print[b]['time'][i+count])
    for i in range(num):
        if df_print[a]['time'][i] > df_print[b]['time'][i+count]:
            print(i,df_print[a]['time'][i],df_print[b]['time'][i+count])
            arg_list.append(i)
            count -= 1
        if count <= -20:
            break
    arg_list.reverse()
    print(len(arg_list))
    for i in arg_list:
        df_print[a]['time'].pop(i)
        df_print[a]['1ch'].pop(i)
        df_print[a]['2ch'].pop(i)
        df_print[a]['3ch'].pop(i)
        df_print[a]['4ch'].pop(i)
    print(arg_list)
    print("time",len(df_print[0]['time']),len(df_print[1]['time']))
    print("1ch",len(df_print[0]['1ch']),len(df_print[1]['1ch']))
    print("2ch",len(df_print[0]['2ch']),len(df_print[1]['2ch']))
    print("3ch",len(df_print[0]['3ch']),len(df_print[1]['3ch']))
    print("4ch",len(df_print[0]['4ch']),len(df_print[1]['4ch']))
    return df_print

def fig_plot(df_print, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(10, 3))
    ax_1ch = fig.add_subplot(131)
    ax_2ch = fig.add_subplot(132)
    ax_3ch = fig.add_subplot(133)
    # ax_4ch = fig.add_subplot(224)
    # ax_1ch.set_aspect('equal', adjustable='box')
    # ax_2ch.set_aspect('equal', adjustable='box')
    # ax_3ch.set_aspect('equal', adjustable='box')

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    # ax_4ch.yaxis.grid(True)
    # ax_1ch.tick_params(labelsize=18)
    # ax_2ch.tick_params(labelsize=18)
    # ax_3ch.tick_params(labelsize=18)
    # ax_4ch.tick_params(labelsize=18)
    ax_1ch.set_title('X [nT]')
    ax_2ch.set_title('Y [nT]')
    ax_3ch.set_title('Z [nT]')
    # ax_4ch.set_title('Temperature [C]', fontsize=18)

    #### plot line color ####
    df_print = fit_timecode(df_print)
    if F_flag == "scatter":
        ax_1ch.scatter(df_print[0]['1ch'], df_print[1]['1ch'], color = 'r', marker='x', alpha=0.3)
        ax_2ch.scatter(df_print[0]['2ch'], df_print[1]['2ch'], color = 'b', marker='x', alpha=0.3)
        ax_3ch.scatter(df_print[0]['3ch'], df_print[1]['3ch'], color = 'g', marker='x', alpha=0.3)
        # ax_4ch.scatter(df_print[0]['4ch'], df_print[1]['4ch'], color = 'k')
        #### plot X axis limit ####
        median_1ch = np.median(df_print[0]['1ch'])
        median_2ch = np.median(df_print[0]['2ch'])
        median_3ch = np.median(df_print[0]['3ch'])
        # median_4ch = np.median(df_print[0]['4ch'])
        ax_1ch.set_xlim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_xlim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_xlim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        # ax_4ch.set_xlim([median_4ch - (1/4),median_4ch + (1/4)])
        X1chMIN = median_1ch - (Yrange/2)
        X1chMAX = median_1ch + (Yrange/2)
        X2chMIN = median_2ch - (Yrange/2)
        X2chMAX = median_2ch + (Yrange/2)
        X3chMIN = median_3ch - (Yrange/2)
        X3chMAX = median_3ch + (Yrange/2)
        arg1ch = []
        arg2ch = []
        arg3ch = []
        for i in range(len(df_print[0]['1ch'])):
            if df_print[0]['1ch'][i] < X1chMIN:
                arg1ch.append(i)
            if df_print[0]['1ch'][i] > X1chMAX:
                arg1ch.append(i)
            if df_print[0]['2ch'][i] < X2chMIN:
                arg2ch.append(i)
            if df_print[0]['2ch'][i] > X2chMAX:
                arg2ch.append(i)
            if df_print[0]['3ch'][i] < X3chMIN:
                arg3ch.append(i)
            if df_print[0]['3ch'][i] > X3chMAX:
                arg3ch.append(i)
        arg1ch.reverse()
        arg2ch.reverse()
        arg3ch.reverse()
        for i in arg1ch:
            df_print[0]['1ch'].pop(i)
            df_print[1]['1ch'].pop(i)
        for i in arg2ch:
            df_print[0]['2ch'].pop(i)
            df_print[1]['2ch'].pop(i)
        for i in arg3ch:
            df_print[0]['3ch'].pop(i)
            df_print[1]['3ch'].pop(i)
        #### plot Y axis limit ####
        median_1ch = np.median(df_print[1]['1ch'])
        median_2ch = np.median(df_print[1]['2ch'])
        median_3ch = np.median(df_print[1]['3ch'])
        # median_4ch = np.median(df_print[1]['4ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        # ax_4ch.set_ylim([median_4ch - (1/4),median_4ch + (1/4)])
        # Y1chMIN = median_1ch - (Yrange/2)
        # Y1chMAX = median_1ch + (Yrange/2)
        # Y2chMIN = median_2ch - (Yrange/2)
        # Y2chMAX = median_2ch + (Yrange/2)
        # Y3chMIN = median_3ch - (Yrange/2)
        # Y3chMAX = median_3ch + (Yrange/2)
        # arg1ch = []
        # arg2ch = []
        # arg3ch = []
        # for i in range(len(df_print[1]['1ch'])):
        #     if df_print[1]['1ch'][i] < Y1chMIN:
        #         arg1ch.append(i)
        #     if df_print[1]['1ch'][i] > Y1chMAX:
        #         arg1ch.append(i)
        #     if df_print[1]['2ch'][i] < Y2chMIN:
        #         arg2ch.append(i)
        #     if df_print[1]['2ch'][i] > Y2chMAX:
        #         arg2ch.append(i)
        #     if df_print[1]['3ch'][i] < Y3chMIN:
        #         arg3ch.append(i)
        #     if df_print[1]['3ch'][i] > Y3chMAX:
        #         arg3ch.append(i)
        # arg1ch.reverse()
        # arg2ch.reverse()
        # arg3ch.reverse()
        # for i in arg1ch:
        #     df_print[0]['1ch'].pop(i)
        #     df_print[1]['1ch'].pop(i)
        # for i in arg2ch:
        #     df_print[0]['2ch'].pop(i)
        #     df_print[1]['2ch'].pop(i)
        # for i in arg3ch:
        #     df_print[0]['3ch'].pop(i)
        #     df_print[1]['3ch'].pop(i)        
        #### Linear simple regression ####
        clf1ch = linear_model.LinearRegression()
        clf2ch = linear_model.LinearRegression()
        clf3ch = linear_model.LinearRegression()
        # clf4ch = linear_model.LinearRegression()
        df1ch_1 = pd.DataFrame(df_print[0]['1ch'].T)
        df1ch_2 = pd.DataFrame(df_print[1]['1ch'].T)
        df2ch_1 = pd.DataFrame(df_print[0]['2ch'].T)
        df2ch_2 = pd.DataFrame(df_print[1]['2ch'].T)
        df3ch_1 = pd.DataFrame(df_print[0]['3ch'].T)
        df3ch_2 = pd.DataFrame(df_print[1]['3ch'].T)
        # df4ch_1 = pd.DataFrame(df_print[0]['4ch'].T)
        # df4ch_2 = pd.DataFrame(df_print[1]['4ch'].T)

        clf1ch.fit(df1ch_1,df1ch_2)
        clf2ch.fit(df2ch_1,df2ch_2)
        clf3ch.fit(df3ch_1,df3ch_2)
        # clf4ch.fit(df4ch_1,df4ch_2)
        ax_1ch.plot(df1ch_1, clf1ch.predict(df1ch_1), color = 'y')
        ax_2ch.plot(df2ch_1, clf2ch.predict(df2ch_1), color = 'y')
        ax_3ch.plot(df3ch_1, clf3ch.predict(df3ch_1), color = 'y')
        # ax_4ch.plot(df4ch_1, clf4ch.predict(df4ch_1), color = 'y')
        text1ch = "Slope = "+'{:.2f}'.format(clf1ch.coef_[0][0])+"\nR^2 = "+'{:.2f}'.format(clf1ch.score(df1ch_1,df1ch_2))
        text2ch = "Slope = "+'{:.2f}'.format(clf2ch.coef_[0][0])+"\nR^2 = "+'{:.2f}'.format(clf2ch.score(df2ch_1,df2ch_2))
        text3ch = "Slope = "+'{:.2f}'.format(clf3ch.coef_[0][0])+"\nR^2 = "+'{:.2f}'.format(clf3ch.score(df3ch_1,df3ch_2))
        # text1ch = "Slope = "+'{:.2f}'.format(clf1ch.coef_[0][0])+"\nIntercept = "+'{:.2f}'.format(clf1ch.intercept_[0])+"\nR^2 = "+'{:.2f}'.format(clf1ch.score(df1ch_1,df1ch_2))
        # text2ch = "Slope = "+'{:.2f}'.format(clf2ch.coef_[0][0])+"\nIntercept = "+'{:.2f}'.format(clf2ch.intercept_[0])+"\nR^2 = "+'{:.2f}'.format(clf2ch.score(df2ch_1,df2ch_2))
        # text3ch = "Slope = "+'{:.2f}'.format(clf3ch.coef_[0][0])+"\nIntercept = "+'{:.2f}'.format(clf3ch.intercept_[0])+"\nR^2 = "+'{:.2f}'.format(clf3ch.score(df3ch_1,df3ch_2))
        # text4ch = "Regression coefficient = "+'{:.1f}'.format(clf4ch.coef_[0][0])+"\nIntercept = "+'{:.1f}'.format(clf4ch.intercept_[0])+"\nCoefficient of determination = "+'{:.1f}'.format(clf4ch.score(df4ch_1,df4ch_2))
        ##ax.transAxesをつけると、表示位置がAxesの相対位置で指定できる
        ax_1ch.text(0.1, 0.9, text1ch, va='top', ha='left',transform=ax_1ch.transAxes,fontsize='large')
        ax_2ch.text(0.1, 0.9, text2ch, va='top', ha='left',transform=ax_2ch.transAxes,fontsize='large')
        ax_3ch.text(0.1, 0.9, text3ch, va='top', ha='left',transform=ax_3ch.transAxes,fontsize='large')
        # ax_4ch.text(0.1, 0.9, text4ch, va='top', ha='left',transform=ax_4ch.transAxes)

    elif F_flag == "scatterT":
        ax_1ch.scatter(df_print[0]['1ch'], df_print[0]['4ch'], color = 'r')
        ax_2ch.scatter(df_print[0]['2ch'], df_print[0]['4ch'], color = 'b')
        ax_3ch.scatter(df_print[0]['3ch'], df_print[0]['4ch'], color = 'g')
        
    #### plot grid ####
    ax_1ch.xaxis.grid(True)
    ax_2ch.xaxis.grid(True)
    ax_3ch.xaxis.grid(True)
    # ax_4ch.xaxis.grid(True)
 
    if dat_path != '':    
        df_print.to_csv(dat_path)
    # plt.title(title)
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
            print("Error = ", date_numpy[i])
        elif date_numpy[i] > (start_datetime + datetime.timedelta(seconds=sec)):
            diff = date_numpy[i] - (start_datetime + datetime.timedelta(seconds=sec))
            NaN_date.append(start_datetime + datetime.timedelta(seconds=sec))
            sec += (int(diff.total_seconds()) + 1)
            print(date_numpy[i],int(diff.total_seconds()),start_datetime + datetime.timedelta(seconds=sec),date_numpy[i+1])
    return errer_index,NaN_date

def check_goodData(date_numpy,start_datetime):
    good_index = []
    for sec in range(len(date_numpy)):
        now = len(good_index)
        while(now < len(date_numpy)):
            # print(date_numpy[now],(start_datetime + datetime.timedelta(seconds=sec)))
            if date_numpy[now] == (start_datetime + datetime.timedelta(seconds=sec)):
                good_index.append(now)
                break
            now += 1
    return good_index

def fig_plot3(df_print, title, fig_path, F_flag, dat_path = '', Yrange = 0):
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
    ax_7ch.plot(df_print[0]['time'], df_print[1]['1ch'] - df_print[0]['1ch'], color = 'r')
    ax_8ch.plot(df_print[0]['time'], df_print[1]['2ch'] - df_print[0]['2ch'], color = 'b')
    ax_9ch.plot(df_print[0]['time'], df_print[1]['3ch'] - df_print[0]['3ch'], color = 'g')
    
    time_scale = False
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
        # median_7ch = np.median(df_print[1]['1ch'] - df_print[0]['1ch'])
        # median_8ch = np.median(df_print[1]['2ch'] - df_print[0]['2ch'])
        # median_9ch = np.median(df_print[1]['2ch'] - df_print[0]['2ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])
        ax_5ch.set_ylim([median_5ch - (Yrange/2),median_5ch + (Yrange/2)])
        ax_6ch.set_ylim([median_6ch - (Yrange/2),median_6ch + (Yrange/2)])
        # ax_7ch.set_ylim([median_7ch - (Yrange/2),median_7ch + (Yrange/2)])
        # ax_8ch.set_ylim([median_8ch - (Yrange/2),median_8ch + (Yrange/2)])
        # ax_9ch.set_ylim([median_9ch - (Yrange/2),median_9ch + (Yrange/2)])
    
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
    ax_7ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_8ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_9ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    #### plot X label print format ####
    # strings = '%H:%M'
    strings = '%m%d'
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

def Timecode_matching(df):
    rawtime = []
    raw1ch_0 = []
    raw2ch_0 = []
    raw3ch_0 = []
    raw4ch_0 = []
    raw1ch_1 = []
    raw2ch_1 = []
    raw3ch_1 = []
    raw4ch_1 = []
    result = []
    unMatch_count = 0
    for i in range(len(df[0][0])):
        try:
            match_arg = df[1][0].index(df[0][0][i])
            rawtime.append(df[0][0][i])
            raw1ch_0.append(df[0][1][i])
            raw2ch_0.append(df[0][2][i])
            raw3ch_0.append(df[0][3][i])
            raw4ch_0.append(df[0][4][i])
            raw1ch_1.append(df[1][1][match_arg])
            raw2ch_1.append(df[1][2][match_arg])
            raw3ch_1.append(df[1][3][match_arg])
            raw4ch_1.append(df[1][4][match_arg])
        except ValueError:
            unMatch_count += 1
    print("no match count is "+str(unMatch_count))
    result.append(pd.DataFrame({'time':pd.to_datetime(rawtime),'1ch':raw1ch_0,'2ch':raw2ch_0,'3ch':raw3ch_0,'4ch':raw4ch_0}))
    result.append(pd.DataFrame({'time':pd.to_datetime(rawtime),'1ch':raw1ch_1,'2ch':raw2ch_1,'3ch':raw3ch_1,'4ch':raw4ch_1}))
    return result

def Process(fileName,F_flag ,Yrange):
    #### initialize ####
    buff_time = []
    buff_1ch = []
    buff_2ch = []
    buff_3ch = []
    buff_4ch = []
    rawdata_all = [[],[]]
    siteInfo = ""
    for j in range(2):
        siteInfo += crop_str(crop_str(fileName[j][0],"@"),".",mode=1)
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
            # end_time_str = header[0] + ' 01:00:00'
            end_time_str = header[0] + ' 23:59:59'
            rawdata = rawdata_maker(f,start_time_str,end_time_str)
            rawtime = pd.to_datetime(rawdata[0])
            print(rawtime)
            #### errer data delete ver 1 ####
            # errer_index, NaN_date = check_errerData(rawtime,rawtime[0])
            # print("errer index amount = ",len(errer_index))
            # print("NaN index amount = ",len(NaN_date))
            # E = reversed(errer_index)
            # for i in E:
            #     rawdata[0].pop(i)
            #     rawdata[1].pop(i)
            #     rawdata[2].pop(i)
            #     rawdata[3].pop(i)
            #     rawdata[4].pop(i)
            #### errer data delete ver 2 ####
            good_index = check_goodData(rawtime,rawtime[0])
            rawT =[]
            raw1 =[]
            raw2 =[]
            raw3 =[]
            raw4 =[]
            for i in good_index:
                rawT.append(rawdata[0][i])
                raw1.append(rawdata[1][i])
                raw2.append(rawdata[2][i])
                raw3.append(rawdata[3][i])
                raw4.append(rawdata[4][i])
            rawtime = pd.to_datetime(rawT)
            print(rawtime)

            #### joint ####
            buff_time = buff_time + rawT
            buff_1ch = buff_1ch + raw1
            buff_2ch = buff_2ch + raw2
            buff_3ch = buff_3ch + raw3
            buff_4ch = buff_4ch + raw4
        rawdata_all[j].append(buff_time)
        rawdata_all[j].append(buff_1ch)
        rawdata_all[j].append(buff_2ch)
        rawdata_all[j].append(buff_3ch)
        rawdata_all[j].append(buff_4ch)

        # rawtime = pd.to_datetime(buff_time)
        # raw1ch = np.array(buff_1ch)
        # raw2ch = np.array(buff_2ch)
        # raw3ch = np.array(buff_3ch)
        # raw4ch = np.array(buff_4ch)
        buff_time = []
        buff_1ch = []
        buff_2ch = []
        buff_3ch = []
        buff_4ch = []
        # df_print.append(pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch}))
  
    df_print = Timecode_matching(rawdata_all)
    
    fig_dir = './fig/diff/'
    figFileDate = rawtime[0].strftime('%Y-%m-%d_%H%M%S') + rawtime[-1].strftime('-%Y-%m-%d_%H%M%S')
    my_makedirs(fig_dir)
    title = start_time_str + '(UT) magnetic force(nT)' + F_flag + siteInfo
    #### graph print ####
    my_makedirs(fig_dir + str(Yrange) + 'nt/')
    fig_path =fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot3(df_print, title, fig_path,F_flag, Yrange=Yrange)

def countUP_filename(F_str,Num,day):
    if Num == 3:
        F_date = datetime.datetime.strptime(F_str,"Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
    else:    
        F_date = datetime.datetime.strptime(F_str,"1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")

def main():
    File = [
    "1sec_median_MI21-01-16_00h00m00s@inabu_byNo1.csv",
    "1sec_median_MI21-01-16_00h00m00s@inabu_byNo2.csv",
    "Fx21-01-16_00h00m00s@inabu_Flux.csv"]

    File_list1 = []
    File_list2 = []
    File_list3 = []
    for i in range(48):
        File_list1.append(countUP_filename(File[0],1,i))
        File_list2.append(countUP_filename(File[1],2,i))
        File_list3.append(countUP_filename(File[2],3,i))    
    Process([File_list1,File_list3],"median",150)
    Process([File_list2,File_list3],"median",150)
    # for i in range(7):
    #     # try:
    #     # Process([[File_list1[i]],[File_list2[i]]],"scatter",100)
    #     Process([[File_list1[i]],[File_list3[i]]],"scatter",100)
    #     Process([[File_list2[i]],[File_list3[i]]],"scatter",100)
    #     # Process([File_list1,File_list3],"scatter",100)
        # Process([File_list2,File_list3],"scatter",100)
        # except:
        #     print("ERROR ", File_list1[i])
        # try:
        #     Process([[File_list2[i]],[File_list3[i]]],"scatter",100)
        # except:
        #     print("ERROR ", File_list2[i])

if __name__ == '__main__':
    main()