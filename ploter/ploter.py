# coding: UTF-8
import csv
import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys
import datetime

def eliminate_f(date_str):
    date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
    return date.strftime('%H:%M:%S')

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
    SAMdata = 0
    NUMdata = 0
    NOWdate = ''
    SPrate = 0
    startFlag = False
    endFlagNum = False
    for row in f:#row is list
        # print('2019-08-09 ' + eliminate_f(row[0]))
        if startFlag == False:
            if ('2019-08-09 ' + eliminate_f(row[0])) == start_dataTime_str:
                print("START")
                startFlag = True
        if startFlag == True:
            if ('2019-08-09 ' + eliminate_f(row[0])) == end_dataTime_str:
                endFlagNum = True
        if endFlagNum == True:
            if ('2019-08-09 ' + eliminate_f(row[0])) != end_dataTime_str:
                print("END")
                endFlagNum = False
                startFlag = False
                break
        
        if rawFlag == 'RAW':
            if startFlag == True:
                df_list['dataTime'].append('2019-08-09 ' + row[0])
                df_list['data'].append(float(row[1]))
        elif rawFlag == '':
            SAMdata += float(row[1])
            NUMdata += 1
            if NOWdate != '':
                if startFlag == True:
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append('2019-08-09 ' + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[1])
                        SPrate = NUMdata
                        NUMdata = 1
            NOWdate = eliminate_f(row[0])
    print(SPrate)
    df = pd.DataFrame({
        'date time':pd.to_datetime(df_list['dataTime']),
        'Magnetic force':df_list['data']
    })
    return df

#ex. start_datetime_str = 2017-08-01 01:00:00
def fig_plot(f,start_datetime_str,end_datetime_str,fig_size,rawFlag,ymin,ymax):
    df = df_maker(f,start_datetime_str,end_datetime_str,rawFlag)
    df = df.set_index('date time')
    # Figureの初期化
    if fig_size == 's':
        fig = plt.figure(figsize=(12, 8))
    elif fig_size == 'm':
        fig = plt.figure(figsize=(8, 4.5))
    else:
        fig = plt.figure(figsize=(12, 4.5))
    # Figure内にAxesを追加()
    ax = fig.add_subplot(111) #...2
    if ymin != 0:
        ax.set_ylim([ymin,ymax])
    ax.yaxis.grid(True)
    ax.plot(df.index,df['Magnetic force'])
    ax.set_title(start_datetime_str + '(JST) to ' + end_datetime_str + '(JST) ' + 'northward component of magnetic force(nT)' + rawFlag)
    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H_%M_%S') + end_dir.strftime('-%d_%H_%M_%S') + '_' + fig_size + '_' + 'Magnetic(nT)'+rawFlag+'.png')
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
        fig_plot(f,rewrite_day(reference_date,i),rewrite_day(reference_date,i+1),fig_size,'',0,0)

def main():
    print("aa")
    args = sys.argv
    if len(args) != 2:
        print("write ==python ploter.py csvFilePass")
        sys.exit(1)
    csv_file = open(args[1],"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    # hour_fig_plot(f,'2019-06-20 23:30:00',15,'l')
    # fig_plot(f,'2019-08-04 00:00:00','2019-08-04 12:00:00','l','',0,0)
    fig_plot(f,'2019-08-09 20:21:00','2019-08-09 20:23:00','l','RAW',18500,19500)

if __name__ == '__main__':
    main()