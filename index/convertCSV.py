import csv

f = open('kp.txt', 'r', encoding='UTF-8')
data = f.read()
f.close()

i = 0
l = []
while(1):
    l.append(data[(56*i):56*(i+1)-1])
    print(i,data[(56*i):56*(i+1)-1])
    i += 1
    if 56*i-1 >= len(data):
        break

with open('kp_sum.csv', 'w', newline="") as f:
    writer = csv.writer(f)
    for ll in l:
        writer.writerow([ll[0:8],ll[25:27],ll[27:28]])