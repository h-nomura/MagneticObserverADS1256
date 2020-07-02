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
from control.matlab import * #### pip install control // pip install slycot
from decimal import Decimal, ROUND_HALF_UP
import collections

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

def eliminate_f(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
        return date.strftime('%H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d %H:%M:%S')

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
            df_list_raw['ch2'].append(-1 * float(row[2]))
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

def fig_plot(df_print, title, fig_path, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(411)
    ax_2ch = fig.add_subplot(412)
    ax_3ch = fig.add_subplot(413)
    # ax_4ch = fig.add_subplot(414)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    # ax_4ch.yaxis.grid(True)
    ax_1ch.tick_params(labelsize=18)
    ax_2ch.tick_params(labelsize=18)
    ax_3ch.tick_params(labelsize=18)
    # ax_4ch.tick_params(labelsize=18)
    ax_1ch.set_ylabel('X [nT]', fontsize=18)
    ax_2ch.set_ylabel('Y [nT]', fontsize=18)
    ax_3ch.set_ylabel('Z [nT]', fontsize=18)
    # ax_4ch.set_ylabel('Totol [nT]', fontsize=18)

    ax_1ch.plot(df_print['time'], df_print['1ch'], color = 'r')
    ax_2ch.plot(df_print['time'], df_print['2ch'], color = 'b')
    ax_3ch.plot(df_print['time'], df_print['3ch'], color = 'g')
    # ax_4ch.plot(df_print['time'], df_print['4ch'], color = 'c')

    if Yrange != 0:
        median_1ch = np.median(df_print['1ch'])
        median_2ch = np.median(df_print['2ch'])
        median_3ch = np.median(df_print['3ch'])
        # median_4ch = np.median(df_print['4ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        # ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])

    ax_3ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    time_scale = False
    if time_scale == True:
        x = []
        # x_axis = ['03:00:00','09:00:00','15:00:00','21:00:00']
        x_axis = ['15:00:00','15:20:00','15:40:00','16:00:00','16:20:00','16:40:00','17:00:00',]
        print(":type:"+ str(type(df_print['time'][0])))
        for s in x_axis:
            x.append(format_to_day_T(df_print['time'][0]) + s)
        x_axis_np = pd.to_datetime(np.array(x))
        ax_1ch.set_xticks(x_axis_np)
        ax_2ch.set_xticks(x_axis_np)
        ax_3ch.set_xticks(x_axis_np)
        # ax_4ch.set_xticks(x_axis_np)
    
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    # plt.setp(ax_3ch.get_xticklabels(),visible=False)
    if dat_path != '':    
        df_print.to_csv(dat_path)
    ax_1ch.set_title(title)
    plt.savefig(fig_path)
    plt.close()

#ex. start_datetime_str = 2017-08-01 01:00:
def data_process(f,start_datetime_str,end_datetime_str,F_flag,Yrange):
    rawdata = rawdata_maker(f,start_datetime_str,end_datetime_str)
    rawtime = pd.to_datetime(rawdata[0])
    raw1ch = np.array(rawdata[1])
    raw2ch = np.array(rawdata[2])
    raw3ch = np.array(rawdata[3])
    # raw4ch = np.array(rawdata[4])

    df_print = pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch})

    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')  
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    title = start_datetime_str + '(UT) magnetic force(nT)' + F_flag
    fig_path = './fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + str(Yrange)+F_flag+'_jpgu.png'
    fig_plot(df_print,title, fig_path,Yrange=int(Yrange))
    
    Yrange = Yrange / 2
    fig_path = './fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + str(Yrange)+F_flag+'_jpgu.png'
    fig_plot(df_print,title, fig_path,Yrange=int(Yrange))

    Yrange = 0
    fig_path = './fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + str(Yrange)+F_flag+'_jpgu.png'
    fig_plot(df_print,title, fig_path)

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

def Process(fileName,StartTime,EndTime, F_flag ,Yrange):
    Pass = "../logger/data/" + fileName
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    data_process(f,header[0] + ' ' + StartTime ,header[0] + ' ' + EndTime, F_flag ,Yrange)

def day_1hour(File, f_type, Yrange):
        Process(File,"00:00:00","01:00:00",f_type,Yrange)
        Process(File,"01:00:00","02:00:00",f_type,Yrange)
        Process(File,"02:00:00","03:00:00",f_type,Yrange)
        Process(File,"03:00:00","04:00:00",f_type,Yrange)
        Process(File,"04:00:00","05:00:00",f_type,Yrange)
        Process(File,"05:00:00","06:00:00",f_type,Yrange)
        Process(File,"06:00:00","07:00:00",f_type,Yrange)
        Process(File,"07:00:00","08:00:00",f_type,Yrange)
        Process(File,"08:00:00","09:00:00",f_type,Yrange)
        Process(File,"09:00:00","10:00:00",f_type,Yrange)
        Process(File,"10:00:00","11:00:00",f_type,Yrange)
        Process(File,"11:00:00","12:00:00",f_type,Yrange)
        Process(File,"12:00:00","13:00:00",f_type,Yrange)
        Process(File,"13:00:00","14:00:00",f_type,Yrange)
        Process(File,"14:00:00","15:00:00",f_type,Yrange)
        Process(File,"15:00:00","16:00:00",f_type,Yrange)
        Process(File,"16:00:00","17:00:00",f_type,Yrange)
        Process(File,"17:00:00","18:00:00",f_type,Yrange)
        Process(File,"18:00:00","19:00:00",f_type,Yrange)
        Process(File,"19:00:00","20:00:00",f_type,Yrange)
        Process(File,"20:00:00","21:00:00",f_type,Yrange)
        Process(File,"21:00:00","22:00:00",f_type,Yrange)
        Process(File,"22:00:00","23:00:00",f_type,Yrange)
        Process(File,"23:00:00","23:59:59",f_type,Yrange)

def main():
    File = [
    "1sec_median_MI20-06-17_01h52m20s.csv",
    "1sec_median_MI20-06-18_00h00m00s.csv",
    "1sec_median_MI20-06-19_00h00m00s.csv",
    "1sec_median_MI20-06-20_00h00m00s.csv",
    "1sec_median_MI20-06-21_00h00m00s.csv",
    "1sec_median_MI20-06-22_00h00m00s.csv",
    "1sec_median_MI20-06-23_00h00m00s.csv",
    "1sec_median_MI20-06-24_00h00m00s.csv",
    "1sec_median_MI20-06-25_00h00m00s.csv",
    "UT_MI20-02-14_00h00m00s.csv",
    "MI20-06-03_01h02m06s.csv",
    "MI20-05-27_00h00m00s.csv",
    "MI20-05-28_00h00m00s.csv",
    "MI20-05-29_00h00m00s.csv",
    "MI20-05-30_00h00m00s.csv",
    "MI20-05-31_00h00m00s.csv",
    "MI20-05-26_06h09m32s.csv",
    "MI20-04-17_00h00m00s.csv",
    "MI20-04-18_00h00m00s.csv",
    "MI20-04-19_00h00m00s.csv",
    "MI20-04-20_00h00m00s.csv",
    "MI20-04-21_00h00m00s.csv",
    "MI20-04-22_00h00m00s.csv",
    "MI20-04-23_00h00m00s.csv",
    "MI20-04-24_00h00m00s.csv",
    "MI20-04-25_00h00m00s.csv",
    "MI20-04-26_00h00m00s.csv",
    "MI20-04-27_00h00m00s.csv",
    "MI20-04-28_00h00m00s.csv",
    "MI20-04-29_00h00m00s.csv",
    "MI20-04-15_09h45m40s.csv",
    "UT_MI20-02-14_00h00m00s.csv",
    "UT_MI20-02-15_00h00m00s.csv",
    "UT_MI20-02-16_00h00m00s.csv",
    "UT_MI20-02-17_00h00m00s.csv",
    "UT_MI20-02-18_00h00m00s.csv",
    "UT_MI20-02-19_00h00m00s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    # Process(File[0],"07:00:00","07:10:00","median",40)
    Process(File[0],"02:00:00","23:59:59","median",80)
    # day_1hour(File[0],"median",20)
    for i in [1,2,3,4,5,6,7,8]:
        # day_1hour(File[i],"median",20)
        Process(File[i],"00:00:00","23:59:59","median",80)


if __name__ == '__main__':
    main()
