import csv
import pprint
import datetime
from pytz import timezone

def sec_format(sec_str):
    f = 0 # micro sec
    s = 0
    d = 0
    try:
        [s, f] = sec_str.split('.')
        s = int(s)
        f = int(f[:6])
        d = s // (60 * 60 * 24)
        s %= (60 * 60 * 24)
        return([d,s,f])
    except ValueError:
        return([0,0,0])

def main():
    row_num = 0
    with open('./data/MIMPiTest-2020-09-11_14-41-24.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            row_num += 1
            if row_num <= 9:
                if row_num == 2:
                    time_datetime = datetime.datetime.strptime(row[0], '%Y/%m/%d %H:%M:%S')
                    time_datetime -= datetime.timedelta(hours=9)
                    # print(time_datetime)
                    # print(type(time_datetime))
                    path = './data/DT9824_{0:%y-%m-%d_%Hh%Mm%Ss}.csv'.format(time_datetime)
                    f_write = open(path,'w', newline="")
                    data = ['{0:%Y-%m-%d}'.format(time_datetime),'V_1ch','V_2ch','V_3ch','dummy']
                    writer = csv.writer(f_write)
                    writer.writerow(data)   
                # print(row)
            else:
                t_diff = sec_format(row[0])
                now_datetime = time_datetime + datetime.timedelta(days=t_diff[0], seconds=t_diff[1], microseconds=t_diff[2])
                if (row_num % 10000) == 0:
                    print(now_datetime)
                data = ['{0:%H:%M:%S.%f}'.format(now_datetime),row[1],row[2],row[3],0]
                writer.writerow(data) 
                # if row_num == 100:
                #     break

if __name__ == "__main__":
    main()
    print("SUCCESS!!")