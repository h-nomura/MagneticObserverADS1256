import sys
import os
from ADS1256_definitions import *
from pipyadc import ADS1256


if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")
# Input pin for the potentiometer on the Waveshare Precision ADC board:
POTI = POS_AIN0|NEG_AINCOM
# Light dependant resistor of the same board:
LDR  = POS_AIN1|NEG_AINCOM
# The other external input screw terminals of the Waveshare board:
EXT2, EXT3, EXT4 = POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM, POS_AIN4|NEG_AINCOM
EXT5, EXT6, EXT7 = POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

# You can connect any pin as well to the positive as to the negative ADC input.
# The following reads the voltage of the potentiometer with negative polarity.
# The ADC reading should be identical to that of the POTI channel, but negative.
POTI_INVERTED = POS_AINCOM|NEG_AIN0

# For fun, connect both ADC inputs to the same physical input pin.
# The ADC should always read a value close to zero for this.
SHORT_CIRCUIT = POS_AIN0|NEG_AIN0

# Specify here an arbitrary length list (tuple) of arbitrary input channel pair
# eight-bit code values to scan sequentially from index 0 to last.
# Eight channels fit on the screen nicely for this example..
# CH_SEQUENCE = (POTI, LDR, EXT2, EXT3, EXT4, EXT7, POTI_INVERTED, SHORT_CIRCUIT)
################################################################################
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
    ads.drate = DRATE_1000
    # gainの設定
    ads.pga_gain = 1
    ### STEP 2: Gain and offset self-calibration:
    ads.cal_self()

    while True:
        ### STEP 3: Get data:
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        voltages     = [(i * ads.v_per_digit * 6.970260223 - 15.522769516) for i in raw_channels]
        MagneticF     = [(i * 1000 / 0.16) for i in voltages]
        print(voltages)
        print(MagneticF)

        ### STEP 4: DONE. Have fun!
        # nice_output(raw_channels, voltages)

### END EXAMPLE ###


#############################################################################
# Format nice looking text output:
def nice_output(digits, volts):
    sys.stdout.write(
          "\0337" # Store cursor position
        +
"""
These are the raw sample values for the channels:
Poti_CH0,  LDR_CH1,     AIN2,     AIN3,     AIN4,     AIN7, Poti NEG, Short 0V
"""
        + ", ".join(["{: 8d}".format(i) for i in digits])
        +
"""

These are the sample values converted to voltage in V for the channels:
Poti_CH0,  LDR_CH1,     AIN2,     AIN3,     AIN4,     AIN7, Poti NEG, Short 0V
"""
        + ", ".join(["{: 8.3f}".format(i) for i in volts])
        + "\n\033[J\0338" # Restore cursor position etc.
    )


# Start data acquisition
try:
    print("\033[2J\033[H") # Clear screen
    print(__doc__)
    print("\nPress CTRL-C to exit.")
    do_measurement()

except (KeyboardInterrupt):
    print("\n"*8 + "User exit.\n")
    sys.exit(0)