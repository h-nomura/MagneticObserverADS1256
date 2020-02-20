# coding: UTF-8
import csv
import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys
import datetime
from statistics import median
from statistics import mean


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
            df_list_raw['ch1'].append(-1 * float(row[1]))
            df_list_raw['ch2'].append(float(row[2]))
            df_list_raw['ch3'].append(-1 * float(row[3]))
            df_list_raw['ch4'].append(float(row[4]))
    return df_list_raw['Time'],df_list_raw['ch1'],df_list_raw['ch2'],df_list_raw['ch3'],df_list_raw['ch4']
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
            arg.append(j)
    #### eliminate ####
    for j in arg:
        if j == 0:
            data[j] = (data[j+1] + data[j+2]) / 2
        else:
            data[j] = (data[j+1] + data[j-1]) / 2
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

#ex. start_datetime_str = 2017-08-01 01:00:
def fig_plot(f,start_datetime_str,end_datetime_str,fig_size,rawFlag,ymin,ymax,Yrange):
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
        ax_4ch.set_ylim([median_4ch - (10),median_4ch + (10)])

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

    filterFlag = False
    if filterFlag == True:
            buf = medianFilter(rawdata[0],rawdata[1],3)
            t_1ch = buf[0]
            d_1ch = buf[1]
            buf = medianFilter(rawdata[0],rawdata[2],3)
            t_2ch = buf[0]
            d_2ch = buf[1]
            buf = medianFilter(rawdata[0],rawdata[3],3)
            t_3ch = buf[0]
            d_3ch = buf[1]
            buf = medianFilter(rawdata[0],rawdata[4],0.1)
            t_4ch = buf[0]
            d_4ch = buf[1]
            ax_1ch.plot(pd.to_datetime(t_1ch, utc=True), d_1ch, color='r')
            ax_2ch.plot(pd.to_datetime(t_2ch, utc=True), d_2ch, color='g')
            ax_3ch.plot(pd.to_datetime(t_3ch, utc=True), d_3ch, color='b')
            ax_4ch.plot(pd.to_datetime(t_4ch, utc=True), d_4ch, color='k')
    else:
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
    if filterFlag == True:
        plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + fig_size + '_' + 'Magnetic(nT)filterON'+rawFlag+str(Yrange)+'.png') 
    else:
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
    "MI20-02-19_00h00m00s.csv",
    "MI20-02-13_08h32m24s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "clean_per2crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    #Process(File[0],"00:00:00","00:01:00","OVER",0,0,1000)
    Process(File[0],"00:00:00","23:59:59","OVER",0,0,100)
    #Process(File[1],"09:50:00","09:50:01","OVER",0,0,50)
    print('test')



if __name__ == '__main__':
    main()