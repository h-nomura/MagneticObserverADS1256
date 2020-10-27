# coding: UTF-8
import csv
import datetime
import sys
args = sys.argv
filename = args[1]

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

def crop(f,header,start,end):
    writePass = "..\\logger\\data\\crop_" + filename
    with open(writePass,'w', newline="") as wf:
        writer = csv.writer(wf)
        writer.writerow(header)
        
        startFlag = False
        endFlag = False
        dataday = format_to_day(start)

        for row in f:
            if startFlag == False:
                if (dataday + eliminate_f(row[0])) == start:
                    print("START")
                    startFlag = True
            if startFlag == True:
                if (dataday + eliminate_f(row[0])) == end:
                    endFlag = True
            if endFlag == True:
                if (dataday + eliminate_f(row[0])) != end:
                    print("END")
                    endFlag = False
                    startFlag = False
                    break
            
            if startFlag == True:
                print(row[0])
                writer.writerow(row)

def main():
    Pass = "..\\logger\\data\\" + filename
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    crop(f,header,header[0] + ' 19:10:00', header[0] + ' 19:20:00')

if __name__ == '__main__':
    main()