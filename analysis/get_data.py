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

def df_maker(f,start_dataTime_str,end_dataTime_str,ch_num):
    num = ch_num
    df_list_raw = {'dataTime':[],'data':[]}
    NOWdate = ''
    startFlag = False
    endFlagNum = False
    dataday = format_to_day(start_dataTime_str)
    for row in f:#row is list
        # print(eliminate_f(row[0]))
        if startFlag == False:
            if (dataday + eliminate_f(row[0])) == start_dataTime_str:
                #print("START")
                startFlag = True
        if startFlag == True:
            if (dataday + eliminate_f(row[0])) == end_dataTime_str:
                endFlagNum = True
        if endFlagNum == True:
            if (dataday + eliminate_f(row[0])) != end_dataTime_str:
                #print("END")
                endFlagNum = False
                startFlag = False
                break
        
        if startFlag == True:
            df_list_raw['dataTime'].append(dataday + row[0])
            df_list_raw['data'].append(float(row[num]))
        NOWdate = eliminate_f(row[0])
    median = statistics.median(df_list_raw['data'])

    return df_list_raw['dataTime'],df_list_raw['data'],median

#ex. start_datetime_str = 2017-08-01 01:00:00
def get_median(f,start_datetime_str,end_datetime_str,ch):
    dfList =  df_maker(f,start_datetime_str,end_datetime_str,ch)
    print(start_datetime_str +" to " + end_datetime_str +"ch = "+ str(ch) +" median = "+ str(dfList[2]))


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

def Process(fileName,StartTime,EndTime,ch):
    Pass = "..\\logger\\data\\" + fileName
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    #print(header)
    get_median(f,header[0] + ' ' + StartTime ,header[0] + ' ' + EndTime, ch)

def main():
    File = [
    "MI20-02-11_18h52m00s.csv",
    "crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,0)
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,1000)
    # Process(File[2],"03:00:00","04:00:00","OVER",0,0,1000)
    Process(File[0],"18:52:10","18:52:50",1)
    Process(File[0],"18:52:10","18:52:50",2)
    Process(File[0],"18:52:10","18:52:50",3)
    Process(File[0],"18:54:10","18:54:50",1)
    Process(File[0],"18:54:10","18:54:50",2)
    Process(File[0],"18:54:10","18:54:50",3)
    Process(File[0],"18:56:10","18:56:50",1)
    Process(File[0],"18:56:10","18:56:50",2)
    Process(File[0],"18:56:10","18:56:50",3)
    Process(File[0],"18:58:10","18:58:50",1)
    Process(File[0],"18:58:10","18:58:50",2)
    Process(File[0],"18:58:10","18:58:50",3)
    Process(File[0],"19:00:10","19:00:50",1)
    Process(File[0],"19:00:10","19:00:50",2)
    Process(File[0],"19:00:10","19:00:50",3)
    Process(File[0],"19:02:10","19:02:50",1)
    Process(File[0],"19:02:10","19:02:50",2)
    Process(File[0],"19:02:10","19:02:50",3)
    Process(File[0],"19:04:10","19:04:50",1)
    Process(File[0],"19:04:10","19:04:50",2)
    Process(File[0],"19:04:10","19:04:50",3)


if __name__ == '__main__':
    main()