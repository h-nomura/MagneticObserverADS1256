# coding: UTF-8
import csv
import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys
import datetime

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

def df_maker(f,start_dataTime_str,end_dataTime_str,rawFlag):
    num = 1
    df_list = {'dataTime':[],'data':[]}
    df_list_raw = {'dataTime':[],'data':[]}
    SAMdata = 0
    NUMdata = 0
    NOWdate = ''
    SPrate = 0
    startFlag = False
    endFlagNum = False
    dataday = format_to_day(start_dataTime_str)
    average = 0
    for row in f:#row is list
        # print(eliminate_f(row[0]))
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
        
        if rawFlag == 'RAW':
            if startFlag == True:
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[num]))
                average += float(row[num])
                average /= 2
        elif rawFlag == '':
            if startFlag == True:
                SAMdata += float(row[num])
                NUMdata += 1
            if NOWdate != '':
                if startFlag == True:
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        average += (SAMdata / NUMdata)
                        average /= 2
                        SAMdata = float(row[num])
                        SPrate = NUMdata
                        NUMdata = 1
            NOWdate = eliminate_f(row[0])
        elif rawFlag == 'OVER':
            if startFlag == True:
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[num]))
                average += float(row[num])
                average /= 2

                SAMdata += float(row[num])
                NUMdata += 1
            if NOWdate != '':
                if startFlag == True:
                    if NOWdate != eliminate_f(row[0]):
                        print(dataday + NOWdate + " srate = "+ str(NUMdata))
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[num])
                        SPrate = NUMdata
                        NUMdata = 1
            NOWdate = eliminate_f(row[0])

    if rawFlag == '' or rawFlag == 'OVER':
        print(SPrate)

    return df_list['dataTime'],df_list['data'],df_list_raw['dataTime'],df_list_raw['data'],average,SPrate

#ex. start_datetime_str = 2017-08-01 01:00:00
def fig_plot(f,start_datetime_str,end_datetime_str,fig_size,rawFlag,ymin,ymax,Yrange):
    dfList = df_maker(f,start_datetime_str,end_datetime_str,rawFlag)
    # Figureの初期化
    if fig_size == 's':
        fig = plt.figure(figsize=(12, 8))
    elif fig_size == 'm':
        fig = plt.figure(figsize=(8, 4.5))
    else:
        fig = plt.figure(figsize=(7, 5))
    # Figure内にAxesを追加()
    ax = fig.add_subplot(111) #...2
    if Yrange != 0:
        ax.set_xlim([dfList[4] - (Yrange/2),dfList[4] + (Yrange/2)])
    if ymin != 0:
        ax.set_xlim(ymin,ymax)
    ax.yaxis.grid(True)
    ax.xaxis.grid(True)
    ax.set_yscale('log')
    if rawFlag == 'RAW' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time raw':pd.to_datetime(dfList[2]),
            'Magnetic force raw':dfList[3]
        })
        ax.hist(df['Magnetic force raw'],bins=100, color='g')
    if rawFlag == '' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time':pd.to_datetime(dfList[0]),
            'Magnetic force':dfList[1]
        })
        ax.hist(df['Magnetic force'],bins=20, color='r')
    ax.tick_params(labelsize=18)
    plt.xticks( [9605, 9610, 9615] )
    ax.set_title(start_datetime_str + 'to ' + end_datetime_str + '(JST) ' + 'Histogram')
    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + fig_size + '_' + 'Histogram2'+rawFlag+str(Yrange)+'.png')
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
    "MI2019-11-14_22h31m46s.csv",
    "MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,0)
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,1000)
    # Process(File[2],"03:00:00","04:00:00","OVER",0,0,1000)
    Process(File[1],"20:10:00","20:11:00","OVER",0,0,0)
    # Process(File[1],"00:00:00","23:59:59","OVER",0,0,0)
    # Process(File[2],"00:00:00","23:59:59","OVER",0,0,0)
    # Process(File[0],"03:00:00","04:00:00","OVER",0,0,1000)
    # Process(File[0],"03:00:00","04:00:00","OVER",0,0,200)
    # Process(File[0],"03:00:00","03:10:00","OVER",0,0,200)
    # Process(File[0],"03:00:00","03:01:00","OVER",0,0,200)
    # Process(File[0],"00:00:00","00:10:00","OVER",0,0,3000)
    # Process(File[1],"17:31:00","17:32:00","OVER",0,0,200)
    # Process(File[2],"15:57:00","16:07:00","",0,0,5000)
    # Process(File[3],"16:11:00","16:21:00","",0,0,5000)
    # Process(File[4],"16:24:00","16:34:00","",0,0,5000)
    # Process(File[5],"16:40:00","16:50:00","",0,0,5000)


if __name__ == '__main__':
    main()