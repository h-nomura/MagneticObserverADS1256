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

from sklearn.decomposition import FastICA
from sklearn.decomposition import PCA

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

def Signal_plot(x,y, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(12, 8))
    ax_1ch = fig.add_subplot(911)
    ax_2ch = fig.add_subplot(912)
    ax_3ch = fig.add_subplot(913)
    ax_4ch = fig.add_subplot(914)
    ax_5ch = fig.add_subplot(915)
    ax_6ch = fig.add_subplot(916)
    ax_7ch = fig.add_subplot(917)
    ax_8ch = fig.add_subplot(918)
    ax_9ch = fig.add_subplot(919)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_5ch.yaxis.grid(True)
    ax_6ch.yaxis.grid(True)
    ax_7ch.yaxis.grid(True)
    ax_8ch.yaxis.grid(True)
    ax_9ch.yaxis.grid(True)

    ax_1ch.tick_params(labelsize=18)
    ax_2ch.tick_params(labelsize=18)
    ax_3ch.tick_params(labelsize=18)
    ax_4ch.tick_params(labelsize=18)
    ax_5ch.tick_params(labelsize=18)
    ax_6ch.tick_params(labelsize=18)
    ax_7ch.tick_params(labelsize=18)
    ax_8ch.tick_params(labelsize=18)
    ax_9ch.tick_params(labelsize=18)

    # ax_1ch.set_ylabel('X of No1[nT]', fontsize=18)
    # ax_2ch.set_ylabel('Y of No1[nT]', fontsize=18)
    # ax_3ch.set_ylabel('Z of No1[nT]', fontsize=18)
    # ax_4ch.set_ylabel('X of No2[nT]', fontsize=18)
    # ax_5ch.set_ylabel('Y of No2[nT]', fontsize=18)
    # ax_6ch.set_ylabel('Z of No2[nT]', fontsize=18)

    #### plot line color ####
    ax_1ch.plot(x, y[0])
    ax_2ch.plot(x, y[1])
    ax_3ch.plot(x, y[2])
    ax_4ch.plot(x, y[3])
    ax_5ch.plot(x, y[4])
    ax_6ch.plot(x, y[5])
    ax_7ch.plot(x, y[6])
    ax_8ch.plot(x, y[7])
    ax_9ch.plot(x, y[8])
    #### plot grid ####
    ax_1ch.xaxis.grid(True)
    ax_2ch.xaxis.grid(True)
    ax_3ch.xaxis.grid(True)
    ax_4ch.xaxis.grid(True)
    ax_5ch.xaxis.grid(True)
    ax_6ch.xaxis.grid(True)
    ax_7ch.xaxis.grid(True)
    ax_8ch.xaxis.grid(True)
    ax_9ch.xaxis.grid(True)

    #### plot X axis justified ####
    ax_1ch.set_xlim([x[0],x[len(x)-1]])
    ax_2ch.set_xlim([x[0],x[len(x)-1]])
    ax_3ch.set_xlim([x[0],x[len(x)-1]])
    ax_4ch.set_xlim([x[0],x[len(x)-1]])
    ax_5ch.set_xlim([x[0],x[len(x)-1]])
    ax_6ch.set_xlim([x[0],x[len(x)-1]])
    ax_7ch.set_xlim([x[0],x[len(x)-1]])
    ax_8ch.set_xlim([x[0],x[len(x)-1]])
    ax_9ch.set_xlim([x[0],x[len(x)-1]])

    #### plot X label print format ####
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    ax_9ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H'))
    #### show only X label of bottom graph #### 
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)
    plt.setp(ax_4ch.get_xticklabels(),visible=False)
    plt.setp(ax_5ch.get_xticklabels(),visible=False)
    plt.setp(ax_6ch.get_xticklabels(),visible=False)
    plt.setp(ax_7ch.get_xticklabels(),visible=False)
    plt.setp(ax_8ch.get_xticklabels(),visible=False)

    ax_1ch.set_title(title)
    plt.savefig(fig_path)
    plt.close()
def test_plot(x):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(611)
    ax_2ch = fig.add_subplot(612)
    ax_3ch = fig.add_subplot(613)
    ax_4ch = fig.add_subplot(614)
    ax_5ch = fig.add_subplot(615)
    ax_6ch = fig.add_subplot(616)
    ax_1ch.plot(x[0], color = 'r')
    ax_2ch.plot(x[1], color = 'b')
    ax_3ch.plot(x[2], color = 'g')
    ax_4ch.plot(x[3], color = 'm')
    ax_5ch.plot(x[4], color = 'c')
    ax_6ch.plot(x[5], color = 'y')
    fig.tight_layout()
    plt.show()

def fig_plot(df_print,labelList, title, fig_path, F_flag, dat_path = '', Yrange = 0):
    fig = plt.figure(figsize=(12, 12))
    ax_1ch = fig.add_subplot(611)
    ax_2ch = fig.add_subplot(612)
    ax_3ch = fig.add_subplot(613)
    ax_4ch = fig.add_subplot(614)
    ax_5ch = fig.add_subplot(615)
    ax_6ch = fig.add_subplot(616)

    ax_1ch.yaxis.grid(True)
    ax_2ch.yaxis.grid(True)
    ax_3ch.yaxis.grid(True)
    ax_4ch.yaxis.grid(True)
    ax_5ch.yaxis.grid(True)
    ax_6ch.yaxis.grid(True)
    # ax_1ch.tick_params(labelsize=18)
    # ax_2ch.tick_params(labelsize=18)
    # ax_3ch.tick_params(labelsize=18)
    # ax_4ch.tick_params(labelsize=18)
    # ax_5ch.tick_params(labelsize=18)
    # ax_6ch.tick_params(labelsize=18)
    if len(labelList) != 6:
        labelList = ['X of No1[nT]','Y of No1[nT]','Z of No1[nT]','X of No2[nT]','Y of No2[nT]','Z of No2[nT]']
    ax_1ch.set_ylabel(labelList[0])
    ax_2ch.set_ylabel(labelList[1])
    ax_3ch.set_ylabel(labelList[2])
    ax_4ch.set_ylabel(labelList[3])
    ax_5ch.set_ylabel(labelList[4])
    ax_6ch.set_ylabel(labelList[5])
    # ax_1ch.set_ylabel('X of No1[nT]', fontsize=18)
    # ax_2ch.set_ylabel('Y of No1[nT]', fontsize=18)
    # ax_3ch.set_ylabel('Z of No1[nT]', fontsize=18)
    # ax_4ch.set_ylabel('X of No2[nT]', fontsize=18)
    # ax_5ch.set_ylabel('Y of No2[nT]', fontsize=18)
    # ax_6ch.set_ylabel('Z of No2[nT]', fontsize=18)

    #### plot line color ####
    ax_1ch.plot(df_print[0]['time'], df_print[0]['1ch'], color = 'r')
    ax_2ch.plot(df_print[0]['time'], df_print[0]['2ch'], color = 'b')
    ax_3ch.plot(df_print[0]['time'], df_print[0]['3ch'], color = 'g')
    ax_4ch.plot(df_print[1]['time'], df_print[1]['1ch'], color = 'm')
    ax_5ch.plot(df_print[1]['time'], df_print[1]['2ch'], color = 'c')
    ax_6ch.plot(df_print[1]['time'], df_print[1]['3ch'], color = 'y')
    #### plot grid ####
    ax_1ch.xaxis.grid(True)
    ax_2ch.xaxis.grid(True)
    ax_3ch.xaxis.grid(True)
    ax_4ch.xaxis.grid(True)
    ax_5ch.xaxis.grid(True)
    ax_6ch.xaxis.grid(True)
    #### plot Y axis limit ####
    if Yrange != 0:
        median_1ch = np.median(df_print[0]['1ch'])
        median_2ch = np.median(df_print[0]['2ch'])
        median_3ch = np.median(df_print[0]['3ch'])
        median_4ch = np.median(df_print[1]['1ch'])
        median_5ch = np.median(df_print[1]['2ch'])
        median_6ch = np.median(df_print[1]['3ch'])
        ax_1ch.set_ylim([median_1ch - (Yrange/2),median_1ch + (Yrange/2)])
        ax_2ch.set_ylim([median_2ch - (Yrange/2),median_2ch + (Yrange/2)])
        ax_3ch.set_ylim([median_3ch - (Yrange/2),median_3ch + (Yrange/2)])
        ax_4ch.set_ylim([median_4ch - (Yrange/2),median_4ch + (Yrange/2)])
        ax_5ch.set_ylim([median_5ch - (Yrange/2),median_5ch + (Yrange/2)])
        ax_6ch.set_ylim([median_6ch - (Yrange/2),median_6ch + (Yrange/2)])
    
    ax_1ch.get_yaxis().get_major_formatter().set_useOffset(False)# X軸の数字をオフセットを使わずに表現する
    ax_2ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_3ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_4ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_5ch.get_yaxis().get_major_formatter().set_useOffset(False)
    ax_6ch.get_yaxis().get_major_formatter().set_useOffset(False)
 
    #### plot X axis justified ####
    ax_1ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_2ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_3ch.set_xlim([df_print[0]['time'][0],df_print[0]['time'][len(df_print[0]['time'])-1]])
    ax_4ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_5ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    ax_6ch.set_xlim([df_print[1]['time'][0],df_print[1]['time'][len(df_print[1]['time'])-1]])
    #### plot X label print format ####
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))
    ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    # ax_6ch.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H'))
    #### show only X label of bottom graph #### 
    plt.setp(ax_1ch.get_xticklabels(),visible=False)
    plt.setp(ax_2ch.get_xticklabels(),visible=False)
    plt.setp(ax_3ch.get_xticklabels(),visible=False)
    plt.setp(ax_4ch.get_xticklabels(),visible=False)
    plt.setp(ax_5ch.get_xticklabels(),visible=False)

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

#### input 6-np array output 6-np array ####
def ICA_process(y1,y2,y3,y4,y5,y6):
    Y = np.vstack([y1,y2,y3,y4,y5,y6]).T
    ica = FastICA(n_components=6,whiten=True)
    ica.fit(Y)
    X = ica.transform(Y)
    x1 = np.array(X.T[0,:])
    x2 = np.array(X.T[1,:])
    x3 = np.array(X.T[2,:])
    x4 = np.array(X.T[3,:])
    x5 = np.array(X.T[4,:])
    x6 = np.array(X.T[5,:])
    return [x1,x2,x3,x4,x5,x6]

def ICA_process2(y1,y2,y3,y4,y5,y6):
    #### Centering #####
    y1mean = np.mean(y1)
    y2mean = np.mean(y2)
    y3mean = np.mean(y3)
    y4mean = np.mean(y4)
    y5mean = np.mean(y5)
    y6mean = np.mean(y6)
    y1 -= y1mean
    y2 -= y2mean
    y3 -= y3mean
    y4 -= y4mean
    y5 -= y5mean
    y6 -= y6mean
    Y = np.vstack([y1,y2,y3,y4,y5,y6]).T
    transformer = FastICA(n_components=6,random_state=0)
    X_transformed = transformer.fit_transform(Y)
    A_ = transformer.mixing_.T  #混合行列

    x = []
    for i in range(6):
        x.append(np.array(X_transformed.T[i,:]))    
    test_plot([x[0],x[1],x[2],x[3],x[4],x[5]])
    print("Noise component amount")
    noize_c_num = int(input())
    print("Noise component number")
    NUM = []
    for i in range(noize_c_num):
        NUM.append(int(input()))
    zero_np = np.zeros(X_transformed.T[0,:].size)
    s = []
    n = []
    choiceNUM = ""
    for i in range(6):
        s.append(X_transformed.T[i,:])
        n.append(zero_np)
    for i in NUM:
        choiceNUM += str(i)
        n[i] = s[i]
        s[i] = zero_np

    S = np.vstack([s[0],s[1],s[2],s[3],s[4],s[5]]).T
    N = np.vstack([n[0],n[1],n[2],n[3],n[4],n[5]]).T
    print(S.shape)
    y1 = np.dot(S,A_)[:,0] + y1mean
    y2 = np.dot(S,A_)[:,1] + y2mean
    y3 = np.dot(S,A_)[:,2] + y3mean
    y4 = np.dot(N,A_)[:,0] + y1mean
    y5 = np.dot(N,A_)[:,1] + y2mean
    y6 = np.dot(N,A_)[:,2] + y3mean
    test_plot([y1,y2,y3,y4,y5,y6])
    return [x[0],x[1],x[2],x[3],x[4],x[5]], [y1,y2,y3,y4,y5,y6,choiceNUM]

def PCA_process_2sig(y1,y2):
    #### Centering #####
    y1mean = np.mean(y1)
    y2mean = np.mean(y2)
    y1 -= y1mean
    y2 -= y2mean
    #### Scaling ####
    y1std = np.std(y1)
    y2std = np.std(y2)
    y1 /= y1std
    y2 /= y2std
    #### PCA ####
    Y = np.vstack([y1,y2]).T
    pca = PCA(n_components=2,whiten=True)
    pca.fit(Y)
    X = pca.transform(Y)
    x1 = np.array(X.T[0,:])
    x2 = np.array(X.T[1,:])
    #### Polarity check ####
    x1 *= ((y1std + y2std)/2)
    x2 *= ((y1std + y2std)/2)
    
    x1_1 = x1 + ((y1mean + y2mean)/2)
    x1_2 = ((y1mean + y2mean)/2) -x1
    diffSUM1 = np.sum((y1+y2)/2 - x1_1)
    diffSUM2 = np.sum((y1+y2)/2 - x1_2)
    if diffSUM1 >= diffSUM2:
        x1 = x1_1
    else:
        x1 = x1_2
    x2 += ((y1mean + y2mean)/2)
    return [x1,x2]

def ICA_process_3sig(y1,y2,y3):
    Y = np.vstack([y1,y2,y3]).T
    ica = FastICA(n_components=3,whiten=True)
    ica.fit(Y)
    X = ica.transform(Y)
    x1 = np.array(X.T[0,:])
    x2 = np.array(X.T[1,:])
    x3 = np.array(X.T[2,:])
    return [x1,x2,x3]

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

def Process(fileName,StartTime,EndTime, F_flag ,Yrange):
    siteInfo = ""
    df_print = []
    for i in range(3):
        Pass = "../logger/data/" + fileName[i]
        siteInfo += crop_str(crop_str(fileName[i],"@"),".",mode=1)
        csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
        f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        header = next(f)
        print(header)
        start_time_str = header[0] + ' ' + StartTime
        end_time_str = header[0] + ' ' + EndTime
        rawdata = rawdata_maker(f,start_time_str,end_time_str)
        csv_file.close()
        rawtime = pd.to_datetime(rawdata[0])
        print(rawtime)
        errer_index, NaN_data = check_errerData(rawtime,rawtime[0])
        errer_index.reverse()
        for i in errer_index:
            rawdata[0].pop(i)
            rawdata[1].pop(i)
            rawdata[2].pop(i)
            rawdata[3].pop(i)
            rawdata[4].pop(i)
        rawtime = pd.to_datetime(rawdata[0])
        raw1ch = np.array(rawdata[1])
        raw2ch = np.array(rawdata[2])
        raw3ch = np.array(rawdata[3])
        raw4ch = np.array(rawdata[4])
        rawdata = []
        df_print.append(pd.DataFrame({'time':rawtime,'1ch':raw1ch,'2ch':raw2ch,'3ch':raw3ch,'4ch':raw4ch}))
    #### ICA ####
    ana_print=[]
    if F_flag == "ICA":
        ana_print2=[]
        ica_result1, ica_result2 = ICA_process2(df_print[0]['1ch'],df_print[0]['2ch'],df_print[0]['3ch'],df_print[1]['1ch'],df_print[1]['2ch'],df_print[1]['3ch'])
        ana_print.append(pd.DataFrame({'time':df_print[0]['time'],'1ch':ica_result1[0],'2ch':ica_result1[1],'3ch':ica_result1[2],'4ch':df_print[0]['4ch']}))
        ana_print.append(pd.DataFrame({'time':df_print[1]['time'],'1ch':ica_result1[3],'2ch':ica_result1[4],'3ch':ica_result1[5],'4ch':df_print[1]['4ch']}))
        ana_print2.append(pd.DataFrame({'time':df_print[0]['time'],'1ch':ica_result2[0],'2ch':ica_result2[1],'3ch':ica_result2[2],'4ch':df_print[0]['4ch']}))
        ana_print2.append(pd.DataFrame({'time':df_print[2]['time'],'1ch':df_print[2]['1ch'],'2ch':df_print[2]['2ch'],'3ch':df_print[2]['3ch'],'4ch':df_print[1]['4ch']}))
    elif F_flag == "PCA":
        ica_result_x = PCA_process_2sig(df_print[0]['1ch'],df_print[1]['1ch'])
        ica_result_y = PCA_process_2sig(df_print[0]['2ch'],df_print[1]['2ch'])
        ica_result_z = PCA_process_2sig(df_print[0]['3ch'],df_print[1]['3ch'])
        ana_print.append(pd.DataFrame({'time':df_print[0]['time'],'1ch':ica_result_x[0],'2ch':ica_result_y[0],'3ch':ica_result_z[0],'4ch':df_print[0]['4ch']}))
        ana_print.append(pd.DataFrame({'time':df_print[1]['time'],'1ch':ica_result_x[1],'2ch':ica_result_y[1],'3ch':ica_result_z[1],'4ch':df_print[1]['4ch']}))
    elif F_flag == "3sigICA":
        ica_result_no1 = ICA_process_3sig(df_print[0]['1ch'],df_print[0]['2ch'],df_print[0]['3ch'])
        ica_result_no2 = ICA_process_3sig(df_print[0]['1ch'],df_print[0]['2ch'],df_print[0]['3ch'])
        ana_print.append(pd.DataFrame({'time':df_print[0]['time'],'1ch':ica_result_no1[0],'2ch':ica_result_no1[1],'3ch':ica_result_no1[2],'4ch':df_print[0]['4ch']}))
        ana_print.append(pd.DataFrame({'time':df_print[1]['time'],'1ch':ica_result_no2[0],'2ch':ica_result_no2[1],'3ch':ica_result_no2[2],'4ch':df_print[1]['4ch']}))

    fig_date = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_dir = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
    fig_dir = './fig/SGEPSS_ICA/' + fig_date.strftime('%Y-%m-%d') + siteInfo
    figFileDate = fig_date.strftime('%Y-%m-%d_%H%M%S') + end_dir.strftime('-%H%M%S')
    my_makedirs(fig_dir)
    title = start_time_str + '(UT) magnetic force(nT)' + F_flag + siteInfo
    #### graph print ####
    if F_flag == 'PCA':
        labelList = ['X [nT]','Y [nT]','Z [nT]','Noise of X [nT]','Noise of Y [nT]','Noise of Z [nT]']
        fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+"_analysis"+siteInfo+'.png'
        fig_plot(ana_print,labelList,title, fig_path,F_flag, Yrange=Yrange)

    if F_flag == 'ICA':
        labelList = ['component1','component2','component3','component4','component5','component6']
        # labelList2 = ['X [nT]','Y [nT]','Z [nT]','Noise of X [nT]','Noise of Y [nT]','Noise of Z [nT]']
        labelList2 = ['X of MIM-Pi No1 [nT]','Y of MIM-Pi No1 [nT]','Z of MIM-Pi No1 [nT]','X of Fluxgate [nT]','Y of Fluxgate [nT]','Z of Fluxgate [nT]']
        fig_path1 = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+"_analysis_component"+siteInfo+'.png'
        fig_path2 = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+"_analysis_Result"+ica_result2[6]+siteInfo+'.png'
        fig_plot(ana_print,labelList,title, fig_path1,F_flag, Yrange=0)
        fig_plot(ana_print2,labelList2,title, fig_path2,F_flag, Yrange=Yrange)

    labelList = [""]
    fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))
    
    Yrange = int(Yrange / 2)
    fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,labelList,title, fig_path,F_flag,Yrange=int(Yrange))

    Yrange = 0
    fig_path = fig_dir + '/' + figFileDate + '_' + str(Yrange)+F_flag+siteInfo+'.png'
    fig_plot(df_print,labelList,title, fig_path,F_flag, Yrange=0)

def cal_time(ProcessTime,mode,sec):
    before = datetime.datetime.strptime(ProcessTime,"%H:%M:%S")
    if mode == "add":
        after = before + datetime.timedelta(seconds=sec)
    elif mode == "sub":
        after = before - datetime.timedelta(seconds=sec)
    return after.strftime("%H:%M:%S")

def day_1hour(File, f_type, Yrange):
    ProcessTime = "00:00:00"
    for i in range(24):
        # print(ProcessTime)
        if i != 23:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",60*60),f_type,Yrange)
        else:
            Process(File,ProcessTime,cal_time(ProcessTime,"add",59*60+59),f_type,Yrange)
        ProcessTime = cal_time(ProcessTime,"add",60*60)

def main():
    File = [
    "1sec_median_MI20-10-24_00h00m00s@inabu_byNo1.csv",
    "1sec_median_MI20-10-24_00h00m00s@inabu_byNo2.csv",
    "Fx20-10-24_00h00m00s@inabu_Flux.csv"]
    # Process([File[0],File[1]],"00:00:00","23:59:59","median",200)
    # Process([File[0],File[1]],"00:00:00","03:00:00","median",100)
    # Process([File[0],File[1]],"03:00:00","06:00:00","median",100)
    # Process([File[0],File[1]],"06:00:00","09:00:00","median",100)
    # Process([File[0],File[1]],"09:00:00","12:00:00","median",100)
    # Process([File[0],File[1]],"12:00:00","15:00:00","median",100)
    Process([File[0],File[1],File[2]],"19:00:00","20:00:00","ICA",10)
    # Process([File[0],File[1]],"18:00:00","21:00:00","PCA",10)
    # day_1hour([File[0],File[1]],"PCA",20)

if __name__ == '__main__':
    main()