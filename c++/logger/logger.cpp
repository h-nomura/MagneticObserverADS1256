#include <stdio.h>
#include <time.h>

#include <stdlib.h>

#include <string.h>
//////HPADDAlibary//////
// MIT License

// Copyright (c) 2018 shujima

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
int logger(void);
double get_data(void);

int main(void){
    char timeData[64];
    while(1){
        logger();
        time_t t = time(NULL);
        strftime(timeData, sizeof(timeData), "start measurement of MI%Y-%m-%d_%Hh%Mm%Ss.csv\n", localtime(&t));
        printf(timeData);
        break;   
    }
    return 0;
}
int logger(){
    FILE *fp;
    char timeData[1024];
    char buf[64];
    time_t t = time(NULL);
    strftime(timeData, sizeof(timeData), "./data_C_logger/MI%Y-%m-%d_%Hh%Mm%Ss.csv", localtime(&t));
    const char *fname = timeData;
    fp = fopen(fname,"w");
    if(fp == NULL){
        printf("%s file open errer!!\n",fname);
        return -1;
    }
    strftime(timeData,sizeof(timeData), "%Y-%m%d,1ch(nT),2ch(nT),3ch(nT),4ch(nT)\n", localtime(&t));   
    fprintf(fp,timeData);
    int num = 0;
    double data = 0;
    while(num < 100){
        t = time(NULL);
        strftime(timeData, sizeof(timeData), "%H:%M:%S.%f", localtime(&t));
        data = get_data();
        snprintf(buf,sizeof(buf),",%f\n",data);
        strcat(timeData,buf);
        fprintf(fp,timeData);
        num++;
    }
    fclose(fp);
    return 0;
}

double get_data(void){
    return rand()/10000;
}