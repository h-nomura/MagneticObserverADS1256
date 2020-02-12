# coding: UTF-8
import csv
import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys
import datetime
import statistics

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

def eliminate_f(date_str):
    date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
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

#ex. start_datetime_str = 2017-08-01 01:00:00
def fig_plot(f,start_datetime_str,end_datetime_str,fig_size,rawFlag,ymin,ymax,Yrange):
    rawdata = rawdata_maker(f,start_datetime_str,end_datetime_str)
    # Figureの初期化
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(413)
    ax_2ch = fig.add_subplot(412)
    ax_3ch = fig.add_subplot(411)
    ax_4ch = fig.add_subplot(414)
    if Yrange != 0:
        median_1ch = statistics.median(rawdata[1])
        median_2ch = statistics.median(rawdata[2])
        median_3ch = statistics.median(rawdata[3])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])

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

    df_1ch = pd.DataFrame({'time':pd.to_datetime(rawdata[0]),'1ch':rawdata[1]})
    ax_1ch.plot(df_1ch['time'], df_1ch['1ch'], color = 'r')
    df_2ch = pd.DataFrame({'time':pd.to_datetime(rawdata[0]),'2ch':rawdata[2]})
    ax_2ch.plot(df_2ch['time'], df_2ch['2ch'], color = 'g')
    df_3ch = pd.DataFrame({'time':pd.to_datetime(rawdata[0]),'3ch':rawdata[3]})
    ax_3ch.plot(df_3ch['time'], df_3ch['3ch'], color = 'b')
    df_4ch = pd.DataFrame({'time':pd.to_datetime(rawdata[0]),'4ch':rawdata[4]})
    ax_4ch.plot(df_4ch['time'], df_4ch['4ch'], color = 'k')

    ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)

    # ax.set_title(start_datetime_str + '(JST) to ' + end_datetime_str + '(JST) ' + 'northward component of magnetic force(nT)' + rawFlag + str(dfList[5]))
    ax_3ch.set_title(start_datetime_str + '(JST) magnetic force(nT)' + rawFlag)
    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + fig_size + '_' + 'Magnetic(nT)per5'+rawFlag+str(Yrange)+'.png')
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

def hour_fig_plot(f,reference_date,num,fig_size):
    for i in range(num):
        fig_plot(f,rewrite_day(reference_date,i),rewrite_day(reference_date,i+1),fig_size,'',0,0,0)

def Process(fileName,StartTime,EndTime,rawFlag,ymin,ymax,Yrange):
    Pass = "..\\logger\\data\\" + fileName
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    fig_plot(f,header[0] + ' ' + StartTime ,header[0] + ' ' + EndTime,'l', rawFlag, ymin, ymax ,Yrange)

def main():
    File = [
    "MI20-02-12_00h00m00s.csv",
    "MI20-02-12_18h06m58s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    #Process(File[0],"00:00:00","00:01:00","OVER",0,0,1000)
    Process(File[1],"18:19:00","18:20:00","OVER",0,0,200)
    print('test')



if __name__ == '__main__':
    main()