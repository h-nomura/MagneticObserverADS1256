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

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

def eliminate_f(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
        return date.strftime('%H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%H:%M:%S')

def format_to_day(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
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

def sec_average(mode,time_dat,dat1,dat2,dat3,dat4):
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
            if mode == 0:
                ave_d1.append(mean(buff1))
                ave_d2.append(mean(buff2))
                ave_d3.append(mean(buff3))
                ave_d4.append(mean(buff4))
            elif mode == 1:
                ave_d1.append(median(buff1))
                ave_d2.append(median(buff2))
                ave_d3.append(median(buff3))
                ave_d4.append(median(buff4))
            return ave_t, ave_d1, ave_d2, ave_d3, ave_d4            

        if now != eliminate_f(time_dat[i+1]):
            ave_t.append(now)
            # print(now)
            # print(len(buff))
            now = eliminate_f(time_dat[i+1])
            if mode == 0:
                ave_d1.append(mean(buff1))
                ave_d2.append(mean(buff2))
                ave_d3.append(mean(buff3))
                ave_d4.append(mean(buff4))
            elif mode == 1:
                ave_d1.append(median(buff1))
                ave_d2.append(median(buff2))
                ave_d3.append(median(buff3))
                ave_d4.append(median(buff4))
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

def BODE_print(b,a):
    bessel = tf(b,a)
    #bode(bessel,[0.1,1000])
    bode(bessel)
    plt.savefig("./fig/bode.png")

#ex. start_datetime_str = 2017-08-01 01:00:
def fig_plot(f,start_datetime_str,end_datetime_str,F_flag,Yrange):
    rawdata = rawdata_maker(f,start_datetime_str,end_datetime_str)
    # Figure㝮初期化
    fig = plt.figure(figsize=(20, 12))
    ax_1ch = fig.add_subplot(413)
    ax_2ch = fig.add_subplot(412)
    ax_3ch = fig.add_subplot(411)
    ax_4ch = fig.add_subplot(414)
    if Yrange != 0:
        median_1ch = median(rawdata[1])
        median_2ch = median(rawdata[2])
        median_3ch = median(rawdata[3])
        median_4ch = median(rawdata[4])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/20),median_4ch + (Yrange/20)])

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_1ch.tick_params(labelsize=18)
    ax_2ch.tick_params(labelsize=18)
    ax_3ch.tick_params(labelsize=18)
    ax_4ch.tick_params(labelsize=18)
    ax_1ch.set_ylabel('Z [nT]', fontsize=18)
    ax_2ch.set_ylabel('Y [nT]', fontsize=18)
    ax_3ch.set_ylabel('X [nT]', fontsize=18)
    ax_4ch.set_ylabel('Temperature [C]', fontsize=18)

    rawtime = pd.to_datetime(rawdata[0])
    raw1ch = np.array(rawdata[1])
    raw2ch = np.array(rawdata[2])
    raw3ch = np.array(rawdata[3])
    raw4ch = np.array(rawdata[4])

    if F_flag == "LPF" or F_flag == "LPF+median" or F_flag == 'ave' or F_flag == 'median':
        f = get_Srate(rawdata[0]) #### Sampling frequency[Hz]
        fn = f / 2 #### Nyquist frequency[Hz]
        fs = 27.3 #### Stopband edge frequency[Hz]
        #### Normalization ####
        Ws = fs/fn

        N = 5 #### order of the filter
        bessel_b, bessel_a = signal.bessel(N, Ws, "low")
        # BODE_print(bessel_b, bessel_a)

        raw1ch = signal.filtfilt(bessel_b, bessel_a, raw1ch)
        raw2ch = signal.filtfilt(bessel_b, bessel_a, raw2ch)
        raw3ch = signal.filtfilt(bessel_b, bessel_a, raw3ch)
    if F_flag == "LPF+median" or F_flag == 'ave':
        win_size = 31
        raw1ch = signal.medfilt(raw1ch, kernel_size= win_size)
        raw2ch = signal.medfilt(raw2ch, kernel_size= win_size)
        raw3ch = signal.medfilt(raw3ch, kernel_size= win_size)
        raw4ch = signal.medfilt(raw4ch, kernel_size= win_size)
    if F_flag == 'ave':
        ave_dat = sec_average(0,rawdata[0],raw1ch.tolist(),raw2ch.tolist(),raw3ch.tolist(),raw4ch.tolist())
        rawtime = pd.to_datetime(ave_dat[0])
        raw1ch = np.array(ave_dat[1])
        raw2ch = np.array(ave_dat[2])
        raw3ch = np.array(ave_dat[3])
        raw4ch = np.array(ave_dat[4])
    if F_flag == 'median':
        med_dat = sec_average(1,rawdata[0],raw1ch.tolist(),raw2ch.tolist(),raw3ch.tolist(),raw4ch.tolist())
        rawtime = pd.to_datetime(med_dat[0])
        raw1ch = np.array(med_dat[1])
        raw2ch = np.array(med_dat[2])
        raw3ch = np.array(med_dat[3])
        raw4ch = np.array(med_dat[4])

    df_print = pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch})

    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')  
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
  #  if F_flag == 'ave':    
  #      df_print.to_csv('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + str(Yrange)+F_flag+'.csv')
    ax_1ch.plot(df_print['time'], df_print['1ch'], color = 'r')
    ax_2ch.plot(df_print['time'], df_print['2ch'], color = 'g')
    ax_3ch.plot(df_print['time'], df_print['3ch'], color = 'b')
    ax_4ch.plot(df_print['time'], df_print['4ch'], color = 'k')

    ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)

    # ax.set_title(start_datetime_str + '(JST) to ' + end_datetime_str + '(JST) ' + 'northward component of magnetic force(nT)' + rawFlag + str(dfList[5]))
    ax_3ch.set_title(start_datetime_str + '(UT) magnetic force(nT)' + F_flag)

    plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + str(Yrange)+F_flag+'.png')
    #Splt.show()

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
    fig_plot(f,header[0] + ' ' + StartTime ,header[0] + ' ' + EndTime, F_flag ,Yrange)

def main():
    File = [
    "UT_MI20-02-14_00h00m00s.csv",
    "UT_MI20-02-15_00h00m00s.csv",
    "UT_MI20-02-16_00h00m00s.csv",
    "UT_MI20-02-17_00h00m00s.csv",
    "UT_MI20-02-18_00h00m00s.csv",
    "UT_MI20-02-14_00h00m00s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    #Process(File[0],"00:00:00","00:01:00","OVER",0,0,1000)
    # i = 4
    # Process(File[i],"00:00:00","23:59:59","ave",0)        
    # Process(File[i],"00:00:00","23:59:59","raw",0)
    # Process(File[i],"00:00:00","23:59:59","LPF+median",0)
    # Process(File[i],"00:00:00","23:59:59","ave",80)

    # Process(File[3],"00:00:00","23:59:59","LPF+median",0)
    # Process(File[4],"00:00:00","23:59:59","raw",80)
    # Process(File[0],"00:00:00","23:59:59","median",0)
    for i in range(5):
        Process(File[i],"00:00:00","23:59:59","ave",0)        
        Process(File[i],"00:00:00","23:59:59","raw",80)
        Process(File[i],"00:00:00","23:59:59","raw",0)
        Process(File[i],"00:00:00","23:59:59","LPF+median",80) 
        Process(File[i],"00:00:00","23:59:59","ave",80)
        Process(File[i],"00:00:00","23:59:59","median",80)
        Process(File[i],"00:00:00","23:59:59","median",0)
    #Process(File[1],"09:50:00","09:50:01","OVER",0,0,50)
    print('test')



if __name__ == '__main__':
    main()
