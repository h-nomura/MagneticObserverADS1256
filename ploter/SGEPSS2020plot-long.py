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

def add_day(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    date = date + datetime.timedelta(days=1)
    return date.strftime('%Y-%m-%d ')


def format_to_day(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date.strftime('%Y-%m-%d ')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%Y-%m-%d ')  

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

def fig_plot(df_print, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(411)
    ax_2ch = fig.add_subplot(412)
    ax_3ch = fig.add_subplot(413)
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
    ax_4ch.set_ylabel('Temperature [nT]', fontsize=18)

    if F_flag == "FFT":
        N = len(df_print['time'])
        dt = 1
        # dt = (60*60*24) / len(df_print['time'])#sampling freq
        print("sampling = " + str(1 / dt))
        F1 = np.fft.fft(df_print['1ch'])
        F2 = np.fft.fft(df_print['2ch'])
        F3 = np.fft.fft(df_print['3ch'])
        F_abs1 = np.abs(F1)
        F_abs2 = np.abs(F2)
        F_abs3 = np.abs(F3)
        F_abs_amp1 = F_abs1 / N * 2
        F_abs_amp2 = F_abs2 / N * 2
        F_abs_amp3 = F_abs3 / N * 2
        F_abs_amp1[0] = F_abs_amp1[0] / N
        F_abs_amp2[0] = F_abs_amp2[0] / N
        F_abs_amp3[0] = F_abs_amp3[0] / N
        F_abs_amp1 = np.sqrt(F_abs_amp1) * 1000
        F_abs_amp2 = np.sqrt(F_abs_amp2) * 1000
        F_abs_amp3 = np.sqrt(F_abs_amp3) * 1000
        fq = np.linspace(0,1.0/dt,N)
        # ax_1ch.set_ylim(1,1000)
        # ax_2ch.set_ylim(1,1000)
        # ax_3ch.set_ylim(1,1000)
        # ax_1ch.set_xlim(0.01,1000)
        # ax_2ch.set_xlim(0.01,1000)
        # ax_3ch.set_xlim(0.01,1000)
        ax_1ch.set_xscale('log')
        ax_2ch.set_xscale('log')
        ax_3ch.set_xscale('log')
        ax_1ch.set_yscale('log')
        ax_2ch.set_yscale('log')
        ax_3ch.set_yscale('log')
        ax_1ch.xaxis.grid(which = "both")
        ax_2ch.xaxis.grid(which = "both")
        ax_3ch.xaxis.grid(which = "both")
        y_axis_np = np.array([1,10**1,10**2,10**3,10**4])
        ax_1ch.set_yticks(y_axis_np)
        ax_2ch.set_yticks(y_axis_np)
        ax_3ch.set_yticks(y_axis_np)
        # ax_1ch.yaxis.grid(which = "both")
        # ax_2ch.yaxis.grid(which = "both")
        # ax_3ch.yaxis.grid(which = "both")
        yLimit = [1,10**4]
        # yLimit = [1,10**3]
        ax_1ch.set_ylim(yLimit)
        ax_2ch.set_ylim(yLimit)
        ax_3ch.set_ylim(yLimit)
        xLimit = [10**(-5),1]
        # xLimit = [10**(-4),1]
        ax_1ch.set_xlim(xLimit)
        ax_2ch.set_xlim(xLimit)
        ax_3ch.set_xlim(xLimit)
        ax_1ch.plot(fq[:int(N/2)+1], F_abs_amp1[:int(N/2)+1], color = 'r')
        ax_2ch.plot(fq[:int(N/2)+1], F_abs_amp2[:int(N/2)+1], color = 'b')
        ax_3ch.plot(fq[:int(N/2)+1], F_abs_amp3[:int(N/2)+1], color = 'g')
    else:
        #### plot line color ####
        ax_1ch.plot(df_print['time'], df_print['1ch'], color = 'r')
        ax_2ch.plot(df_print['time'], df_print['2ch'], color = 'b')
        ax_3ch.plot(df_print['time'], df_print['3ch'], color = 'g')
        ax_4ch.plot(df_print['time'], df_print['4ch'], color = 'k')
        #### plot grid ####
        ax_1ch.xaxis.grid(True)
        ax_2ch.xaxis.grid(True)
        ax_3ch.xaxis.grid(True)
        ax_4ch.xaxis.grid(True)
        #### plot Y axis limit ####
        if Yrange != 0:
            median_1ch = np.median(df_print['1ch'])
            median_2ch = np.median(df_print['2ch'])
            median_3ch = np.median(df_print['3ch'])
            median_4ch = np.median(df_print['4ch'])
            ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
            ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
            ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
            ax_4ch.set_ylim([median_4ch - (1/4),median_4ch + (1/4)])
        
        #### plot X axis justified ####
        ax_1ch.set_xlim([df_print['time'][0],df_print['time'][len(df_print['time'])-1]])
        ax_2ch.set_xlim([df_print['time'][0],df_print['time'][len(df_print['time'])-1]])
        ax_3ch.set_xlim([df_print['time'][0],df_print['time'][len(df_print['time'])-1]])
        ax_4ch.set_xlim([df_print['time'][0],df_print['time'][len(df_print['time'])-1]])
        #### plot X label print format ####
        # ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
        # ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
        ax_4ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%m-%d'))
        # x = []
        # x_axis = ['00:00:00','03:00:00','06:00:00','09:00:00','12:00:00','15:00:00','18:00:00','21:00:00']
        # print(":type:"+ str(type(df_print['time'][0])))
        # for s in x_axis:
        #     x.append(format_to_day_T(df_print['time'][0]) + s)
        # x.append(add_day(format_to_day_T(df_print['time'][0]) + '00:00:00'))
        # x_axis_np = pd.to_datetime(np.array(x))
        # ax_4ch.set_xticks(x_axis_np)
        # ax_1ch.xaxis.set_major_locator(mpl.ticker.FixedLocator(x_axis_np))
    #### show only X label of bottom graph #### 
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)

    if dat_path != '':    
        df_print.to_csv(dat_path)
    ax_1ch.set_title(title)
    fig.tight_layout()    #文字が重ならないよう調整
    fig.align_labels()    #軸ラベルを揃える
    plt.savefig(fig_path)
    plt.close()

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

def crop_str(str1,target,mode=0):
    for i in range(len(str1)):
        if str1[i] == target:
            if mode == 0:
                return str1[i+1:len(str1)]
            else:
                return str1[0:i]

def check_errerData(date_numpy,start_datetime):
    errer_index = []
    NaN_date = []
    sec = 0
    for i in range(len(date_numpy)):
        # print([date_numpy[i], (start_datetime + datetime.timedelta(seconds=sec))])
        if date_numpy[i] == (start_datetime + datetime.timedelta(seconds=sec)):
            sec += 1
        elif date_numpy[i] < (start_datetime + datetime.timedelta(seconds=sec)):
            errer_index.append(i)
        elif date_numpy[i] > (start_datetime + datetime.timedelta(seconds=sec)):
            diff = date_numpy[i] - (start_datetime + datetime.timedelta(seconds=sec))
            NaN_date.append(start_datetime + datetime.timedelta(seconds=sec))
            sec += int(diff.total_seconds()) + 1
            print(int(diff.total_seconds()))
    return errer_index,NaN_date

def Process(fileName,F_flag ,Yrange):
    #### initialize ####
    buff_time = []
    buff_1ch = []
    buff_2ch = []
    buff_3ch = []
    buff_4ch = []
    for i in range(len(fileName)):
        Pass = "../logger/data/" + fileName[i]
        siteInfo = crop_str(crop_str(fileName[0],"@"),".",mode=1)
        csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
        f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        header = next(f)
        print(header)
        start_time_str = header[0] + ' 00:00:00'
        end_time_str = header[0] + ' 23:59:59'
        rawdata = rawdata_maker(f,start_time_str,end_time_str)
        rawtime = pd.to_datetime(rawdata[0])
        # print(rawtime)
        errer_index, NaN_date = check_errerData(rawtime,rawtime[0])
        print("errer index amount = ",len(errer_index))
        print("NaN index amount = ",len(NaN_date))
        errer_index.reverse()
        for i in errer_index:
            rawdata[0].pop(i)
            rawdata[1].pop(i)
            rawdata[2].pop(i)
            rawdata[3].pop(i)
            rawdata[4].pop(i)
        rawtime = pd.to_datetime(rawdata[0])
        # print(rawtime)
        #### joint ####
        buff_time = buff_time + rawdata[0]
        buff_1ch = buff_1ch + rawdata[1]
        buff_2ch = buff_2ch + rawdata[2]
        buff_3ch = buff_3ch + rawdata[3]
        buff_4ch = buff_4ch + rawdata[4]
    rawtime = pd.to_datetime(buff_time)
    raw1ch = np.array(buff_1ch)
    raw2ch = np.array(buff_2ch)
    raw3ch = np.array(buff_3ch)
    raw4ch = np.array(buff_4ch)

    df_print = pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch})

    fig_date = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    fig_dir = './fig/SGEPSS_all/'
    figFileDate = rawtime[0].strftime('%Y-%m-%d_%H%M%S') + rawtime[-1].strftime('-%Y-%m-%d_%H%M%S')
    my_makedirs(fig_dir)
    title = start_time_str + '(UT) magnetic force(nT)' + F_flag + siteInfo
    #### graph print ####
    my_makedirs(fig_dir + str(Yrange) + 'nt/')
    fig_path = fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,title, fig_path,F_flag,Yrange=int(Yrange))
    
    Yrange = int(Yrange / 2)
    my_makedirs(fig_dir + str(Yrange) + 'nt/')
    fig_path = fig_dir + str(Yrange) + 'nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,title, fig_path,F_flag,Yrange=int(Yrange))

    Yrange = 0
    my_makedirs(fig_dir + str(Yrange) + 'nt/')
    fig_path = fig_dir + '0nt/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,title, fig_path,F_flag, Yrange=0)

def countUP_filename(F_str,Num,day):
    if Num == 3:
        F_date = datetime.datetime.strptime(F_str,"Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("Fx%y-%m-%d_%Hh%Mm%Ss@inabu_Flux.csv")
    else:    
        F_date = datetime.datetime.strptime(F_str,"1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")
        F_date += datetime.timedelta(days=day)
        return F_date.strftime("1sec_median_MI%y-%m-%d_%Hh%Mm%Ss@inabu_byNo"+str(Num)+".csv")

def main():
    File = [
    "1sec_median_MI20-10-25_00h00m00s@inabu_byNo1.csv",
    "1sec_median_MI20-10-25_00h00m00s@inabu_byNo2.csv",
    "Fx20-10-04_00h00m00s@inabu_Flux.csv"]
    File_list1 = []
    File_list2 = []
    File_list3 = []
    for i in range(8):
        File_list1.append(countUP_filename(File[0],1,i))
        File_list2.append(countUP_filename(File[1],2,i))
        File_list3.append(countUP_filename(File[2],3,i))    
    Process(File_list1,"median",200)
    Process(File_list2,"median",200)
    # Process(File_list3,"median",200)

if __name__ == '__main__':
    main()