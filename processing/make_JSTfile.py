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

def format_to_time(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date.strftime('%H:%M:%S.%f')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%H:%M:%S.%f')  

def format_to_day_T(date_timestamp):
    try:
        date = date_timestamp
        return date.strftime('%Y-%m-%d ')
    except ValueError:
        date = datetime.datetime.strptime(date_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d ')

def UTstr_to_JST(date_str):        
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        date += datetime.timedelta(hours=9)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        date += datetime.timedelta(hours=9)
        return date.strftime('%Y-%m-%d %H:%M:%S.%f')  

def str_dt(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

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
    dataday = format_to_day(start_dataTime_str)
    for row in f:#row is list
        if startFlag == False:
            if str_dt(dataday + eliminate_f(row[0])) >= str_dt(start_dataTime_str):
                #print("START")
                startFlag = True
        if str_dt(dataday + eliminate_f(row[0])) > str_dt(end_dataTime_str):
            #print("END")
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

#ex. start_datetime_str = 2017-08-01 01:00:
def data_process(f1,f2,header1,header2):
    rawtime_JST = []
    rawdata1 = rawdata_maker(f1,header1 + " 15:00:00",header1 + " 23:59:59")
    for i in rawdata1[0]:
        if i[14:19] == "00:00":
            print(UTstr_to_JST(i),i)
        rawtime_JST.append(UTstr_to_JST(i))
    raw1ch = np.array(rawdata1[1])
    raw2ch = np.array(rawdata1[2])
    raw3ch = np.array(rawdata1[3])
    raw4ch = np.array(rawdata1[4])

    rawdata2 = rawdata_maker(f2,header2 + " 00:00:00",header2 + " 14:59:59")
    for i in rawdata2[0]:
        if i[14:19] == "00:00":
            print(UTstr_to_JST(i), i)
        rawtime_JST.append(UTstr_to_JST(i))
    raw1ch = np.append(raw1ch,np.array(rawdata2[1]))
    raw2ch = np.append(raw2ch,np.array(rawdata2[2]))
    raw3ch = np.append(raw3ch,np.array(rawdata2[3]))
    raw4ch = np.append(raw4ch,np.array(rawdata2[4]))


 
    return [rawtime_JST,raw1ch,raw2ch,raw3ch,raw4ch]

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

def cal_time(ProcessTime,mode):
    before = datetime.datetime.strptime(ProcessTime,"%H:%M:%S")
    if mode == "add1m":
        after = before + datetime.timedelta(minutes=1)
    elif mode == "add59s":
        after = before + datetime.timedelta(seconds=59)
    elif mode == "add1s":
        after = before + datetime.timedelta(seconds=1)
    elif mode == "sub1m":
        after = before - datetime.timedelta(minutes=1)
    return after.strftime("%H:%M:%S")


def Process(fileName1,fileName2):
    ###initialize###
    Pass = "/nas5/users/nomura/" + fileName1
    csv_file1 = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f1 = csv.reader(csv_file1, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header1 = next(f1)
    print(header1)
    Pass = "/nas5/users/nomura/" + fileName2
    csv_file2 = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f2 = csv.reader(csv_file2, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header2 = next(f2)
    print(header2)
    ###processing###
    data = data_process(f1,f2, header1[0], header2[0])
    csv_file1.close()
    csv_file2.close()

    wPass = "/nas5/users/nomura/jst_" + fileName2
    rowAmount = len(data[0])
    with open(wPass, 'w', newline="") as fw:
        writer = csv.writer(fw)
        writer.writerow([format_to_day(data[0][0])[0:10],"1ch(nT)","2ch(nT)","3ch(nT)"])
        rowAmount = len(data[0])
        for i in range(rowAmount):
            writer.writerow([format_to_time(data[0][i]),data[1][i],data[2][i],data[3][i],data[4][i]])
        # while(processTime != EndTime):
        #     #print(processTime)
        #     data = data_process(f,header[0] + ' ' + cal_time(processTime,"add1s") ,header[0] + ' ' + cal_time(processTime,"add1m"), F_flag)
        #     rowAmount = len(data[0])
        #     for i in range(rowAmount):
        #         writer.writerow([format_to_time(data[0][i]),data[1][i],data[2][i],data[3][i],data[4][i]])
        #     processTime = cal_time(processTime,"add1m")
    ###finalize###

def countUP_filename(F_str,Num,day):
    if Num == 3:
        F_date = datetime.datetime.strptime(F_str,"1sec_FGM@inabu/Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("1sec_FGM@inabu/Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
    else:    
        F_date = datetime.datetime.strptime(F_str,"1sec_MIM-Pi"+str(Num)+"@inabu/1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("1sec_MIM-Pi"+str(Num)+"@inabu/1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")

def main():
    File = [
    "1sec_MIM-Pi1@inabu/1sec_median_MI21-01-15_00h00m00s@inabu_byNo1.csv",
    "1sec_MIM-Pi2@inabu/1sec_median_MI20-10-04_00h00m00s@inabu_byNo2.csv",
    "1sec_FGM@inabu/Fx20-06-17_00h00m00s@inabu_Flux.csv"
    ]

    for i in range(40):
        try:
            fileName1 = countUP_filename(File[0],1,i)
            fileName2 = countUP_filename(File[0],1,i+1)
            Process(fileName1,fileName2)
        except:
            print("ERROR: "+ countUP_filename(File[0],1,i+1))

    # for i in range(200):
    #     try:
    #         fileName1 = countUP_filename(File[1],2,i)
    #         fileName2 = countUP_filename(File[1],2,i+1)
    #         Process(fileName1,fileName2)
    #     except:
    #         print("ERROR: "+ fileName2)

if __name__ == '__main__':
    main()
