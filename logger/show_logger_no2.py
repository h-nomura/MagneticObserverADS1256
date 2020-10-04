import sys
import os
from ADS1256_definitions import *
from pipyadc import ADS1256

import time, datetime
from datetime import timedelta, timezone
import csv

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")
# Input pin for the potentiometer on the Waveshare Precision ADC board:
Diff0_1 = POS_AIN0|NEG_AIN1
Diff2_3 = POS_AIN2|NEG_AIN3
Diff4_5 = POS_AIN4|NEG_AIN5
Diff6_7 = POS_AIN6|NEG_AIN7
CH_SEQUENCE = (Diff0_1,Diff2_3,Diff4_5,Diff6_7)
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
    #1007B:1029A:1024A:LM60
    slope = [6.041297912, 6.032822234, 6.024782582, 1.004970735]
    intercept = [-15.21584595, -15.20405742, -15.17129194, -0.000415594]
    transform = [0.16*0.001, 0.16*0.001, 0.16*0.001, 6.25*0.001]
    off_set = [0,0,0,424*0.001]

    while True:
        now = datetime.datetime.now(timezone.utc)#get time
        today = '{0:%Y-%m-%d}'.format(now)

        counter = 0
        while True:            
            now = datetime.datetime.now(timezone.utc)
            # get data
            # raw_channels = ads.read_sequence(CH_SEQUENCE)
            raw_channels = ads.read_continue(CH_SEQUENCE)
            #voltages     = [(i * ads.v_per_digit * 6.970260223 - 15.522769516) for i in raw_channels]
            #MagneticF     = [(i * 1000 / 0.16) for i in voltages]
            voltages = [i * ads.v_per_digit for i in raw_channels]
            # voltages = [2.5,2.5,2.5,0]
            voltages_15 = [(voltages[i] * slope[i] + intercept[i]) for i in range(4)]
            # voltages_15 = [0,0,0,0]
            MagneticF = [(voltages_15[i] - off_set[i])/ transform[i] for i in range(4)]
            # MagneticF = [voltages[i] for i in range(4)]
            
            print('{0:%Y-%m-%d  %H:%M:%S}'.format(now))
            print('X [nT]= ' + '{:.4f}'.format(MagneticF[0]))
            print('Y [nT]= ' + '{:.4f}'.format(MagneticF[1]))
            print('Z [nT]= ' + '{:.4f}'.format(MagneticF[2]))
            print('Temperature [C]= ' + '{:.2f}'.format(MagneticF[3]))
            print ("\33[6A")
            counter += 1
            if '{0:%Y-%m-%d}'.format(now) != today:
                break
            today = '{0:%Y-%m-%d}'.format(now)

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