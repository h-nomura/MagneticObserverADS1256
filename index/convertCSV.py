import csv

f = open('kp.txt', 'r', encoding='UTF-8')
data = f.read()
f.close()

i = 0
l = []
while(1):
    l.append(data[(56*i):56*(i+1)-1])
    # print(i,data[(56*i):56*(i+1)-1])
    i += 1
    if 56*i-1 >= len(data):
        break

with open('kp_sum.csv', 'w', newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["kp index(JST)","0","3","6","9","12","15","18","21"])
    kp_jst = ["","","","","","","",""]
    for ll in l:
        print(ll[0:8],ll[9:11],ll[11:13],ll[13:15],ll[15:17],ll[17:19],ll[19:21],ll[21:23],ll[23:25])
        kp_jst[3] = ll[10]+ll[9]
        kp_jst[4] = ll[12]+ll[11]
        kp_jst[5] = ll[14]+ll[13]
        kp_jst[6] = ll[16]+ll[15]
        kp_jst[7] = ll[18]+ll[17]
        
        data = [ll[0:8]] + kp_jst
        writer.writerow(data)

        kp_jst[0] = ll[20]+ll[19]
        kp_jst[1] = ll[22]+ll[21]
        kp_jst[2] = ll[24]+ll[23]