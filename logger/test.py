import sys
import os
from ADS1256_definitions import *
from pipyadc import ADS1256

import time, datetime
import csv

import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 100000

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")
# Input pin for the potentiometer on the Waveshare Precision ADC board:
Diff0_1 = POS_AIN0|NEG_AIN1
Diff2_3 = POS_AIN2|NEG_AIN3
Diff4_5 = POS_AIN4|NEG_AIN5
Diff6_7 = POS_AIN6|NEG_AIN7
CH_SEQUENCE = (Diff0_1,Diff2_3,Diff4_5,Diff6_7)
def eliminate_f(date_str):
    date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
    return date.strftime('%H:%M:%S')

def format_to_day(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return date.strftime('%Y-%m-%d ')

def df_maker(f,rawFlag):
    df_list = {'dataTime':[],'data':[]}
    df_list_raw = {'dataTime':[],'data':[]}
    SAMdata = 0
    NUMdata = 0
    NOWdate = ''
    SPrate = 0
    average = 0
    index = 0
    for row in f:#row is list
        if index == 0:
            dataday = row[0]
            index = 1
        else:
            if rawFlag == 'RAW':
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2
            elif rawFlag == '':
                SAMdata += float(row[1])
                NUMdata += 1
                if NOWdate != '':
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
                df_list_raw['dataTime'].append(dataday + row[0])
                df_list_raw['data'].append(float(row[1]))
                average += float(row[1])
                average /= 2

                SAMdata += float(row[1])
                NUMdata += 1
                if NOWdate != '':
                    if NOWdate != eliminate_f(row[0]):
                        df_list['dataTime'].append(dataday + NOWdate)
                        df_list['data'].append(SAMdata / NUMdata)
                        SAMdata = float(row[1])
                        SPrate = NUMdata
                        NUMdata = 1
                NOWdate = eliminate_f(row[0])
            elif rawFlag == 'test':
                print(row)
    if rawFlag == '' or rawFlag == 'OVER':
        print(SPrate)

    return df_list['dataTime'],df_list['data'],df_list_raw['dataTime'],df_list_raw['data'],average,SPrate

#ex. start_datetime_str = 2017-08-01 01:00:00
def fig_plot(f,rawFlag,Yrange):
    dfList = df_maker(f,rawFlag)
    # Figureの初期化
    fig = plt.figure(figsize=(12, 6))
    # Figure内にAxesを追加()
    ax = fig.add_subplot(111) #...2
    if Yrange != 0:
        ax.set_ylim([dfList[4] - (Yrange/2),dfList[4] + (Yrange/2)])
    ax.yaxis.grid(True)
    if rawFlag == 'RAW' or rawFlag == 'OVER':
        ax.plot(pd.to_datetime(dfList[2], utc=True), dfList[3], color='b')
    if rawFlag == '' or rawFlag == 'OVER':
        ax.plot(pd.to_datetime(dfList[0], utc=True), dfList[1], color='r')
    ax.set_title('(JST) ' + 'northward component of magnetic force(nT)' + rawFlag + str(dfList[5]))
    plt.show()

def my_makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def do_measurement():
    ### STEP 1: Initialise ADC object using default configuration:
    # (Note1: See ADS1256_default_config.py, see ADS1256 datasheet)
    # (Note2: Input buffer on means limited voltage range 0V...3V for 5V supply)
    ads = ADS1256()
    # サンプリング・レートの設定
    # REG_DRATE: Sample rate definitions:
    # DRATE_30000     = 0b11110000 # 30,000SPS (default)
    # DRATE_15000     = 0b11100000 # 15,000SPS
    # DRATE_7500      = 0b11010000 # 7,500SPS
    # DRATE_3750      = 0b11000000 # 3,750SPS
    # DRATE_2000      = 0b10110000 # 2,000SPS
    # DRATE_1000      = 0b10100001 # 1,000SPS
    # DRATE_500       = 0b10010010 # 500SPS
    # DRATE_100       = 0b10000010 # 100SPS
    # DRATE_60        = 0b01110010 # 60SPS
    # DRATE_50        = 0b01100011 # 50SPS
    # DRATE_30        = 0b01010011 # 30SPS
    # DRATE_25        = 0b01000011 # 25SPS
    # DRATE_15        = 0b00110011 # 15SPS
    # DRATE_10        = 0b00100011 # 10SPS
    # DRATE_5         = 0b00010011 # 5SPS
    # DRATE_2_5       = 0b00000011 # 2.5SPS
    ads.drate = DRATE_1000
    # gainの設定
    ads.pga_gain = 1
    ### STEP 2: Gain and offset self-calibration:
    ads.cal_self()


    now = datetime.datetime.now()#get time
    data = [['{0:%Y-%m-%d }'.format(now),
    'Magnetic force(nT)_1ch','Magnetic force(nT)_2ch',
    'Magnetic force(nT)_3ch','Magnetic force(nT)_4ch']]
    counter = 0
    while True:            
        now = datetime.datetime.now()
        # get data
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        voltages     = [(i * ads.v_per_digit * 6.970260223 - 15.522769516) for i in raw_channels]
        MagneticF     = [(i * 1000 / 0.16) for i in voltages]

        data.append(['{0:%H:%M:%S.%f}'.format(now), MagneticF[0], MagneticF[1], MagneticF[2], MagneticF[3]])
        if counter == 1000:
            print('{0:%Y-%m-%d  %H:%M:%S}'.format(now) + '  Magnetic force(nT)==' + str(MagneticF[0]))
            fig_plot(data,"OVER",200)
            data.clear()
            now = datetime.datetime.now()#get time
            data = [['{0:%Y-%m-%d }'.format(now),
            'Magnetic force(nT)_1ch','Magnetic force(nT)_2ch',
            'Magnetic force(nT)_3ch','Magnetic force(nT)_4ch']]
            counter = 0
        counter += 1

def main():
    try:
        # print("\033[2J\033[H") # Clear screen
        print(__doc__)
        print("\nPress CTRL-C to exit.")
        do_measurement()

    except (KeyboardInterrupt):
        print("\n"*8 + "User exit.\n")
        sys.exit(0)

if __name__ == '__main__':
	main()