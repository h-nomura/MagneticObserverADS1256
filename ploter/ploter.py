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
        # print('2019-08-09 ' + eliminate_f(row[0]))
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
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2
        elif rawFlag == '':
            if startFlag == True:
                SAMdata += float(row[1])
                NUMdata += 1
            if NOWdate != '':
                if startFlag == True:
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        average += (SAMdata / NUMdata)
                        average /= 2
                        SAMdata = float(row[1])
                        SPrate = NUMdata
                        NUMdata = 1
            NOWdate = eliminate_f(row[0])
        elif rawFlag == 'OVER':
            if startFlag == True:
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2

                SAMdata += float(row[1])
                NUMdata += 1
            if NOWdate != '':
                if startFlag == True:
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[1])
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
        fig = plt.figure(figsize=(12, 4.5))
    # Figure内にAxesを追加()
    ax = fig.add_subplot(111) #...2
    if Yrange != 0:
        ax.set_ylim([dfList[4] - (Yrange/2),dfList[4] + (Yrange/2)])
    ax.yaxis.grid(True)
    if rawFlag == 'RAW' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time raw':pd.to_datetime(dfList[2]),
            'Magnetic force raw':dfList[3]
        })
        ax.plot(df['date time raw'], df['Magnetic force raw'], color='b')
    if rawFlag == '' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time':pd.to_datetime(dfList[0]),
            'Magnetic force':dfList[1]
        })
        ax.plot(df['date time'], df['Magnetic force'], color='r')
    ax.set_title(start_datetime_str + '(JST) to ' + end_datetime_str + '(JST) ' + 'northward component of magnetic force(nT)' + rawFlag + str(dfList[5]))
    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + fig_size + '_' + 'Magnetic(nT)'+rawFlag+str(Yrange)+'.png')
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
    "MI19-09-24_19h35m06s.csv",
    "MI19-08-28_17h30m25s.csv",
    "MI19-09-03_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,0)
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,1000)
    # Process(File[2],"03:00:00","04:00:00","OVER",0,0,1000)
    Process(File[0],"19:41:00","19:42:00","OVER",0,0,200)
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