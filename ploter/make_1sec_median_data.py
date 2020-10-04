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

def BODE_print(b,a):
    bessel = tf(b,a)
    #bode(bessel,[0.1,1000])
    bode(bessel)
    plt.savefig("./fig/bode.png")

#ex. start_datetime_str = 2017-08-01 01:00:
def data_process(f,start_datetime_str,end_datetime_str,F_flag):
    rawdata = rawdata_maker(f,start_datetime_str,end_datetime_str)
    rawtime = pd.to_datetime(rawdata[0])
    raw1ch = np.array(rawdata[1])
    raw2ch = np.array(rawdata[2])
    raw3ch = np.array(rawdata[3])
    raw4ch = np.array(rawdata[4])

    if F_flag == "LPF" or F_flag == "LPF+median" or F_flag == 'ave' or F_flag == 'median' or F_flag == 'mode':
        print('Low Pass Filter')
        f = get_Srate(rawdata[0]) #### Sampling frequency[Hz]
        fn = f / 2 #### Nyquist frequency[Hz]
        fs = 10 #### Stopband edge frequency[Hz]
        #### Normalization ####
        Ws = fs/fn

        N = 5 #### order of the filter
        bessel_b, bessel_a = signal.bessel(N, Ws, "low")
        # BODE_print(bessel_b, bessel_a)

        raw1ch = signal.filtfilt(bessel_b, bessel_a, raw1ch)
        raw2ch = signal.filtfilt(bessel_b, bessel_a, raw2ch)
        raw3ch = signal.filtfilt(bessel_b, bessel_a, raw3ch)
        raw4ch = signal.filtfilt(bessel_b, bessel_a, raw4ch)
    if F_flag == "LPF+median" or F_flag == 'ave':
        print('Median Filter')
        win_size = 61
        raw1ch = signal.medfilt(raw1ch, kernel_size= win_size)
        raw2ch = signal.medfilt(raw2ch, kernel_size= win_size)
        raw3ch = signal.medfilt(raw3ch, kernel_size= win_size)
        raw4ch = signal.medfilt(raw4ch, kernel_size= win_size)
        #raw4ch = np.sqrt(raw1ch **2 + raw2ch **2 + raw3ch **3)
    if F_flag == 'ave':
        print('1s mean')
        ave_dat = sec_average(0,rawdata[0],raw1ch.tolist(),raw2ch.tolist(),raw3ch.tolist(),raw4ch.tolist())
        rawtime = pd.to_datetime(ave_dat[0])
        raw1ch = np.array(ave_dat[1])
        raw2ch = np.array(ave_dat[2])
        raw3ch = np.array(ave_dat[3])
        raw4ch = np.array(ave_dat[4])
        #raw4ch = np.sqrt(raw1ch **2 + raw2ch **2 + raw3ch **2)
    
    if F_flag == 'median':
        print('1s median')
        med_dat = sec_average(1,rawdata[0],raw1ch.tolist(),raw2ch.tolist(),raw3ch.tolist(),raw4ch.tolist())
        rawtime = med_dat[0]
        raw1ch = np.array(med_dat[1])
        raw2ch = np.array(med_dat[2])
        raw3ch = np.array(med_dat[3])
        raw4ch = np.array(med_dat[4])

        
    if F_flag == 'mode':
        print('1s mode')
        mod_dat = sec_average(2,rawdata[0],raw1ch.tolist(),raw2ch.tolist(),raw3ch.tolist(),raw4ch.tolist())
        rawtime = pd.to_datetime(mod_dat[0])
        raw1ch = np.array(mod_dat[1])
        raw2ch = np.array(mod_dat[2])
        raw3ch = np.array(mod_dat[3])
        raw4ch = np.array(mod_dat[4])

    print(format_to_day(rawtime[0])[0:10] + "!!")
    print(rawtime[0])
    return [rawtime,raw1ch,raw2ch,raw3ch,raw4ch]

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

def Process(fileName,StartTime,EndTime, F_flag):
    Pass = "../logger/data/" + fileName
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    data = data_process(f,header[0] + ' ' + StartTime ,header[0] + ' ' + EndTime, F_flag)
    wPass = "../logger/data/1sec_median_" + fileName
    rowAmount = len(data[0])
    with open(wPass, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([format_to_day(data[0][0])[0:10],"1ch(nT)","2ch(nT)","3ch(nT)"])
        for i in range(rowAmount):
            writer.writerow([format_to_time(data[0][i]),data[1][i],data[2][i],data[3][i],data[4][i]])


def main():
    File = [
    "MI20-10-03_04h56m47s@inabu_byNo1.csv",
    "MI20-10-03_04h55m55s@inabu_byNo2.csv"]

    Process(File[0],"09:00:00","23:59:59","median")


if __name__ == '__main__':
    main()
