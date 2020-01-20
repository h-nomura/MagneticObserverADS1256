# coding: UTF-8
import csv
import datetime
from operator import itemgetter

filename = "crop_MI19-11-11_19h58m31s.csv"
cutoff = 2
def eliminate_f(date_str):
    date = datetime.datetime.strptime(date_str, '%H:%M:%S.%f')
    return date.strftime('%H:%M:%S')

def cleaner(f,header):
    writePass = "..\\logger\\data\\clean_per"+ str(cutoff) + filename
    with open(writePass,'w', newline="") as wf:
        writer = csv.writer(wf)
        writer.writerow([header[0],header[1]])
        dataBox = []
        counter = 0
        watching_time = ''

        for row in f:
            if watching_time != '':
                if watching_time != eliminate_f(row[0]):
                    sorted_dataBox = sorted(dataBox, key=itemgetter(1),reverse=True)
                    median = sorted_dataBox[int(counter/2)][1]
                    print(median)
                    cutoff_Amount = int(counter * cutoff /100)
                    print(cutoff_Amount)
                    write_dataBox = []
                    for i in range(counter - cutoff_Amount):
                        write_dataBox.append(sorted_dataBox[i])
                    writer.writerows(sorted(write_dataBox))
                    # reset
                    dataBox = []
                    counter = 0     
            print(row[0])
            dataBox.append([row[0],row[1]])
            counter += 1
            watching_time = eliminate_f(row[0])


def main():
    Pass = "..\\logger\\data\\" + filename
    csv_file = open(Pass,"r",encoding = "ms932",errors = "", newline = "")
    f = csv.reader(csv_file, delimiter=",",doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(f)
    print(header)
    cleaner(f,header)

if __name__ == '__main__':
    main()