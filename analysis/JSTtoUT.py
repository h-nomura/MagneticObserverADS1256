# coding: UTF-8
import csv
#### JST to UCT ####
from pytz import timezone
from datetime import datetime
import datetime
import queue
from dateutil.tz import gettz

def jst_to_ut(date_str):
    datetime_jst = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    datetime_ut = datetime_jst.astimezone(gettz('Etc/GMT'))
    return datetime_ut.strftime('%Y-%m-%d %H:%M:%S.%f')

def eliminate_f(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
        return date.strftime('%H:%M:%S')
    except ValueError:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date.strftime('%H:%M:%S')

def format_to_day(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    return date.strftime('%Y-%m-%d')

def format_to_time(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    return date.strftime('%H:%M:%S.%f')

def datatime_(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    return date

def read_csv(l,path):
    print("read_start")
    csv_file = open(path,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    year_day = header[0] + ' '
    # test = 0
    counter = 0
    for row in f:
        counter += 1
        # test += 1
        # if test == 100:
        #     break
        if year_day == "2020-02-20 " and eliminate_f(row[0]) == "10:00:00":
            break
        # print(jst_to_ut(year_day + row[0]) + " <<==" + year_day + row[0])
        if counter >= 10000 and eliminate_f(row[0]) == '00:00:00':
            break
        l[0].put(jst_to_ut(year_day + row[0]))
        l[1].put(-1 * float(row[1]))
        l[2].put(-1 * float(row[2]))
        l[3].put(-1 * float(row[3]))
        l[4].put(float(row[4]))
    print("read_end")
    return l

def write_csv(l):
    print("write_start")
    end = False
    buff = [0,0,0,0]
    yesterday = format_to_day(l[0].get())
    for i in range(4):
        l[i+1].get()
    while(1):
        now = l[0].get()
        today = format_to_day(now)
        for i in range(4):
            buff[i] = l[i+1].get()
        if today != yesterday:
            print("start is ___today= " + today + " yesterday= " + yesterday)
            w_pass = '../logger/data/UT_MI{0:%y-%m-%d_%Hh%Mm%Ss}.csv'.format(datatime_(now))
            with open(w_pass,'w', newline="") as f:
                data = ['{0:%Y-%m-%d}'.format(datatime_(now)),
                'Magnetic force(nT)Z_1ch','Magnetic force(nT)Y_2ch',
                'Magnetic force(nT)X_3ch','Temperature(C)_4ch']
                writer = csv.writer(f)
                writer.writerow(data)
                data = [format_to_time(now),buff[0],buff[1],buff[2],buff[3]]               
                writer = csv.writer(f)
                writer.writerow(data)
                yesterday = today
                while(1):
                    now = l[0].get()
                    today = format_to_day(now)
                    if today != yesterday:
                        print("end is ___today= " + today + " yesterday= " + yesterday)
                        end = True
                        break
                    data = [format_to_time(now), l[1].get(), l[2].get(), l[3].get(), l[4].get()]
                    writer = csv.writer(f)
                    writer.writerow(data)
            if end == True:
                break
    return 'output file !! to ' + w_pass

def make_csvfile(ref1, ref2):
    #### initialize ####
    Time = queue.Queue()
    ch1 = queue.Queue()
    ch2 = queue.Queue()
    ch3 = queue.Queue()
    ch4 = queue.Queue()
    dat_list = [Time, ch1, ch2, ch3, ch4]
    path1 = "../logger/data/" + ref1
    path2 = "../logger/data/" + ref2
    
    dat_list = read_csv(dat_list,path1)
    dat_list = read_csv(dat_list,path2)

    result = write_csv(dat_list)
    print(result)

def main():
    #make_csvfile("MI20-02-14_00h00m00s.csv","MI20-02-15_00h00m00s.csv") 
    #make_csvfile("MI20-02-15_00h00m00s.csv","MI20-02-16_00h00m00s.csv") 
    #make_csvfile("MI20-02-16_00h00m00s.csv","MI20-02-17_00h00m00s.csv") 
    #make_csvfile("MI20-02-17_00h00m00s.csv","MI20-02-18_00h00m00s.csv") 
    make_csvfile("MI20-02-19_00h00m00s.csv","MI20-02-20_00h00m00s.csv")
    # make_csvfile("MI20-02-13_14h34m47s.csv","MI20-02-14_00h00m00s.csv")
    # make_csvfile("MI20-02-19_00h00m00s.csv","MI20-02-20_00h00m00s.csv") 
    # now = datetime.datetime.now()
    # print(now.strftime('%Y-%m-%d %H:%M:%S.%f'))
    # now_s = jst_to_ut(now.strftime('%Y-%m-%d %H:%M:%S.%f'))
    # print(now_s)

       
    print("end")

if __name__ == '__main__':
    main()
