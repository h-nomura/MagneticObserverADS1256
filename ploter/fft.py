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
from scipy import signal
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
def df_maker(f,start_dataTime_str,end_dataTime_str,rawFlag):
    num = 2
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
    NumberOFdata = 0
    NumberOFdataRAW = 0
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
                NumberOFdataRAW += 1
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
                NumberOFdataRAW += 1
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
                        NumberOFdata += 1
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[num])
                        SPrate = NUMdata
                        NUMdata = 1
            NOWdate = eliminate_f(row[0])

    if rawFlag == '' or rawFlag == 'OVER':
        print(SPrate)

    return df_list['dataTime'],df_list['data'],df_list_raw['dataTime'],df_list_raw['data'],average,SPrate,NumberOFdataRAW,NumberOFdata

#ex. start_datetime_str = 2017-08-01 01:00:00
def fig_plot(f,start_datetime_str,end_datetime_str,fig_size,rawFlag,ymin,ymax,Yrange):
    dfList = df_maker(f,start_datetime_str,end_datetime_str,rawFlag)
    # Figureの初期化
    if fig_size == 's':
        fig = plt.figure(figsize=(12, 8))
    elif fig_size == 'm':
        fig = plt.figure(figsize=(8, 4.5))
    else:
        fig = plt.figure(figsize=(7, 8))
        # fig = plt.figure(figsize=(6, 8))
    
    # Figure内にAxesを追加()
    ax = fig.add_subplot(211) #...2
    ax2 = fig.add_subplot(212)


    if Yrange != 0:
        ax.set_ylim([dfList[4] - (Yrange/2),dfList[4] + (Yrange/2)])
    if ymin != 0:
        ax.set_ylim(ymin,ymax)
    ax.yaxis.grid(True)
    ax.tick_params(labelsize=18)
    ax2.tick_params(labelsize=18)
    if rawFlag == 'RAW' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time raw':pd.to_datetime(dfList[2]),
            'Magnetic force raw':dfList[3]
        })
              
        #### LP Filter ####
        f = get_Srate(dfList[2]) #### Sampling frequency[Hz]
        fn = f / 2 #### Nyquist frequency[Hz]
        fs = 27 #### Stopband edge frequency[Hz]
        #### Normalization ####
        Ws = fs/fn

        N = 6 #### order of the filter
        bessel_b, bessel_a = signal.bessel(N, Ws, "low")
        ax.plot(df['date time raw'], df['Magnetic force raw'], color='g')
        df['Magnetic force raw'] = signal.filtfilt(bessel_b, bessel_a, df['Magnetic force raw'])
        ax.plot(df['date time raw'], df['Magnetic force raw'], color='chartreuse') 
        for i in range(2):
            # FTT plot
            N = dfList[6]
            print(N)
            dt = 1 / dfList[5]
            print(dt)
            # t = np.arange(dfList[2])
            if i == 0:
                f = np.array(dfList[3])
            else:
                f = df['Magnetic force raw']
            F = np.fft.fft(f)
            F_abs = np.abs(F)
            F_abs_amp = F_abs / N * 2
            F_abs_amp[0] = F_abs_amp[0] / N
            F_abs_amp = np.sqrt(F_abs_amp) * 1000
            fq = np.linspace(0,1.0/dt,N)
            ax2.set_ylim(1,1000)
            ax2.set_xlim(0.01,1000)
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.xaxis.grid(which = "both")
            ax2.yaxis.grid(which = "both")
            ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
            ax2.set_xlabel("Frequency [Hz]", fontsize=18)
            ax2.set_ylabel("Noise density [pT√Hz]", fontsize=18)
            if i == 0:
                ax2.plot(fq[:int(N/2)+1],F_abs_amp[:int(N/2)+1])
            else:
                ax2.plot(fq[:int(N/2)+1],F_abs_amp[:int(N/2)+1],color='c')

        ax.set_title(start_datetime_str + '(JST) magnetic force(nT)' + rawFlag + str(dfList[5]))
        fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
        end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
        my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
        plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_' + 'Magnetic(nT)2'+rawFlag+'FTTLog2per5' + '.png')

        fig2 = plt.figure(figsize=(12, 8))
        ax3 = fig2.add_subplot(211)
        ax4 = fig2.add_subplot(212)
        ax4.yaxis.grid(True)
        ax3.tick_params(labelsize=18)
        ax4.tick_params(labelsize=18)
        F2 = F
        fc = 1 #Cut off
        F2[((fq > fc)&(fq < (152 - fc)))] = 0
        F2_abs = np.abs(F2)
        F2_abs_amp = F2_abs / N * 2
        F2_abs_amp[0] = F2_abs_amp[0] / 2
        ax3.set_ylim(0,0.3)
        ax3.plot(fq[:int(N/2)+1],F2_abs_amp[:int(N/2)+1])
        # ax3.plot(fq,F2_abs_amp)

        F2_ifft = np.fft.ifft(F2)
        F2_ifft_real = F2_ifft.real
        ax4.set_ylim(9602,9618)
        ax4.plot(df['date time raw'], df['Magnetic force raw'], color='g')
        ax4.plot(df['date time raw'], F2_ifft_real, color='y')

    if rawFlag == '' or rawFlag == 'OVER':
        df = pd.DataFrame({
            'date time':pd.to_datetime(dfList[0]),
            'Magnetic force':dfList[1]
        })
        ax.plot(df['date time'], df['Magnetic force'], color='r')
        # FTT plot
        N = dfList[7]
        dt = 1
        # t = np.arange(dfList[2])
        f = np.array(dfList[1])
        F = np.fft.fft(f)
        F_abs = np.abs(F)
        F_abs_amp = F_abs / N * 2
        F_abs_amp[0] = F_abs_amp[0] / 2
        fq = np.linspace(0,1.0/dt,N)
        # ax2.set_xlim(0.000000001,0.05)
        # ax2.plot(fq[:int(N/2)+1],F_abs_amp[:int(N/2)+1], marker="o")
    # ax.set_title(start_datetime_str + '(JST) to ' + end_datetime_str + '(JST) ' + 'northward component of magnetic force(nT)' + rawFlag + str(dfList[5]))
    ax.set_title(start_datetime_str + '(JST) magnetic force(nT)' + rawFlag + str(dfList[5]))
    fig_dir = datetime.datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    my_makedirs('./fig/' + fig_dir.strftime('%Y-%m-%d'))
    # plt.savefig('./fig/' + fig_dir.strftime('%Y-%m-%d') + '/' + fig_dir.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S') + '_fc' + str(fc) + '_' + 'Magnetic(nT)2'+rawFlag+'FTT2' + '.png')
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
    "clean_per5crop_MI19-11-11_19h58m31s.csv",
    "MI19-11-04_00h00m00s.csv",
    "MI19-09-03_19h21m14s.csv",
    "MI19-08-20_16h23m17s.csv",
    "MI19-09-20_12h39m47s.csv"]
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,0)
    # Process(File[2],"00:00:00","12:00:00","OVER",0,0,1000)
    # Process(File[2],"03:00:00","04:00:00","OVER",0,0,1000)
    Process(File[0],"00:00:00","01:00:00","OVER",0,0,0)
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