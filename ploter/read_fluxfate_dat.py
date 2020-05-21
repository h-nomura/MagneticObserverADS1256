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

def my_mode(l):
    mode_l = collections.Counter(l).most_common()
    #### found 2 equally ####
    if len(mode_l) == 1:
        return mode_l[0][0]
    if mode_l[0][1] == mode_l[1][1]:
        i = 0
        while(1):
            if i + 1 == len(mode_l):
                break
            if mode_l[i][1] != mode_l[i+1][1]:
                break
            i += 1
        mode_sum = []
        for j in range(i+1):
            mode_sum.append(mode_l[j][0])
        return float(mean(mode_sum))
    else:
        return mode_l[0][0]

def sec_average(op,time_dat,dat1,dat2,dat3,dat4):
    now = eliminate_f(time_dat[0])
    buff1 = []
    buff2 = []
    buff3 = []
    buff4 = []
    i = 0
    ave_t = []
    ave_d1 = []
    ave_d2 = []
    ave_d3 = []
    ave_d4 = []
    while(1):
        buff1.append(dat1[i])
        buff2.append(dat2[i])
        buff3.append(dat3[i])
        buff4.append(dat4[i])
        # print("i = " + str(i+1) + "len =  "+ str(len(time_dat)-1))
        if i+1 == len(time_dat)-1:
            buff1.append(dat1[i+1])
            buff2.append(dat2[i+1])
            buff3.append(dat3[i+1])
            buff4.append(dat4[i+1])
            ave_t.append(now)
            now = eliminate_f(time_dat[i+1])
            if op == 0:
                ave_d1.append(mean(buff1))
                ave_d2.append(mean(buff2))
                ave_d3.append(mean(buff3))
                ave_d4.append(mean(buff4))
            elif op == 1:
                ave_d1.append(median(buff1))
                ave_d2.append(median(buff2))
                ave_d3.append(median(buff3))
                ave_d4.append(median(buff4))
            elif op == 2:
                buff1 = list_round(buff1)
                buff2 = list_round(buff2)
                buff3 = list_round(buff3)
                buff4 = list_round(buff4)
                ave_d1.append(my_mode(buff1))
                ave_d2.append(my_mode(buff2))
                ave_d3.append(my_mode(buff3))
                ave_d4.append(my_mode(buff4))
            return ave_t, ave_d1, ave_d2, ave_d3, ave_d4            

        if now != eliminate_f(time_dat[i+1]):
            ave_t.append(now)
            # print(now)
            # print(len(buff))
            now = eliminate_f(time_dat[i+1])
            if op == 0:
                ave_d1.append(mean(buff1))
                ave_d2.append(mean(buff2))
                ave_d3.append(mean(buff3))
                ave_d4.append(mean(buff4))
            elif op == 1:
                ave_d1.append(median(buff1))
                ave_d2.append(median(buff2))
                ave_d3.append(median(buff3))
                ave_d4.append(median(buff4))
            elif op == 2:
                buff1 = list_round(buff1)
                buff2 = list_round(buff2)
                buff3 = list_round(buff3)
                buff4 = list_round(buff4)
                ave_d1.append(my_mode(buff1))
                ave_d2.append(my_mode(buff2))
                ave_d3.append(my_mode(buff3))
                ave_d4.append(my_mode(buff4))
            buff1 =[]
            buff2 =[]
            buff3 =[]
            buff4 =[]
        i += 1

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


def convert_data(day_str,raw_str):
    out = []
    l = raw_str.split()
    try:
        out.append(day_str+l[0]+':'+l[1]+':'+l[2])#### data time
        out.append(float(l[3])) #### x axis
        out.append(-1 * float(l[5])) #### y axis
        out.append(float(l[4])) #### z axis
    except ValueError:
        return -1
    return out
def dat_reader(filename):

    day = filename[0:4]+'-'+filename[4:6]+'-'+filename[6:8]+' '
    print(day)
    dat_t = []
    dat_1 = []
    dat_2 = []
    dat_3 = []
    with open('../logger/data/' + filename) as f:
        reader = csv.reader(f)
        # i = 0
        for row in reader:
            # if i > 100:
            #     break
            # i += 1
            dat = convert_data(day,row[0])
            if dat != -1:
                dat_t.append(dat[0])
                dat_1.append(dat[1])
                dat_2.append(dat[2])
                dat_3.append(dat[3])
    out = [dat_t,dat_1,dat_2,dat_3]
    return out
                
def fig_plot(df_print, title, fig_path, Yrange = 0, dat_path = ''):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(411)
    ax_2ch = fig.add_subplot(413)
    ax_3ch = fig.add_subplot(412)
    ax_4ch = fig.add_subplot(414)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_1ch.tick_params(labelsize=18)
    ax_2ch.tick_params(labelsize=18)
    ax_3ch.tick_params(labelsize=18)
    ax_4ch.tick_params(labelsize=18)
    ax_1ch.set_ylabel('X [nT]', fontsize=18)
    ax_2ch.set_ylabel('Y [nT]', fontsize=18)
    ax_3ch.set_ylabel('Z [nT]', fontsize=18)
    ax_4ch.set_ylabel('Totol [nT]', fontsize=18)

    ax_1ch.plot(df_print['time'], df_print['1ch'], color = 'r')
    ax_2ch.plot(df_print['time'], df_print['2ch'], color = 'b')
    ax_3ch.plot(df_print['time'], df_print['3ch'], color = 'g')
    ax_4ch.plot(df_print['time'], df_print['4ch'], color = 'c')

    if Yrange != 0:
        median_1ch = np.median(df_print['1ch'])
        median_2ch = np.median(df_print['2ch'])
        median_3ch = np.median(df_print['3ch'])
        median_4ch = np.median(df_print['4ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])

    ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    
    x = []
    x_axis = ['03:00:00','09:00:00','15:00:00','21:00:00']
    for s in x_axis:
        x.append(format_to_day(str(df_print['time'][0])) + s)
    x_axis_np = pd.to_datetime(np.array(x))
    ax_1ch.set_xticks(x_axis_np)
    ax_2ch.set_xticks(x_axis_np)
    ax_3ch.set_xticks(x_axis_np)
    ax_4ch.set_xticks(x_axis_np)
    
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)
    if dat_path != '':    
        df_print.to_csv(dat_path)
    ax_1ch.set_title(title)
    plt.savefig(fig_path)

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
def data_process(filename,F_flag,Yrange):
    rawdata = dat_reader(filename)
    rawtime = pd.to_datetime(rawdata[0])
    raw1ch = np.array(rawdata[1])
    raw2ch = np.array(rawdata[2])
    raw3ch = np.array(rawdata[3])
    raw4ch = np.sqrt(np.square(raw1ch) + np.square(raw2ch) + np.square(raw3ch))
    df_print = pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch})
    fig_dir = datetime.datetime.strptime(filename[0:8], '%Y%m%d')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    title = filename[0:8] + '(UT) magnetic force(nT)' + F_flag
    # fig_path = './fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d') + '_' + str(Yrange)+F_flag+'.png'
    fig_path = './fig/'  + fig_dir.strftime('%Y-%m-%d') + '_' + str(Yrange)+F_flag+'.png'
    fig_plot(df_print, title, fig_path,Yrange)

def main():
    l = [
    "20200214-1Hz.dat",
    "20200215-1Hz.dat",
    "20200216-1Hz.dat",
    "20200217-1Hz.dat",
    "20200218-1Hz.dat",
    "20200219-1Hz.dat",
    "20200214-1Hz.dat",
    "UT_MI20-02-18_00h00m00s.csv",
    "UT_MI20-02-19_00h00m00s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    for i in range(6):
        data_process(l[i],'flux',80)
        data_process(l[i],'flux',40)
        data_process(l[i],'flux',20)
        data_process(l[i],'flux',0)

if __name__ == '__main__':
    main()