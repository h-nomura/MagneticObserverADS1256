#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include "HPADDAlib/HPADDAlibrary.h"
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

int main(void){
    while(1){
     initHPADDAboard();                       
     ADS1256_SetSampleRate(10);  //[samples / s / inputnum]
     ADS1256_SetGain(1);
     ADS1256_PrintAllReg();
     logger();
     closeHPADDAboard();
     break;   
    }
    return 0;
}
int logger(){
    while(1){
        FILE *fp;
        char timeData[64];
        time_t t = time(NULL);
        strftime(timeData, sizeof(timeData), "./data/MI%Y-%m-%d_%Hh%Mm%Ss.csv", localtime(&t));
        const char *fname = timeData;

        fp = fopen(fname,"w");
        if(fp == NULL){
            printf("%s file open errer!!\n",fname);
            return -1;
        }
        uint8_t i;
        int32_t adval[4];
        for (i = 0 ; i < 4 ; i ++){
            adval[i] = ADS1256_GetAdcDiff( 2 * i , 2 * i + 1 );
            printf("%d-%d : %8d \t(%10f[V])\n",2 * i, 2 * i + 1 ,adval, ADS1256_ValueToVolt(adval,  5.0 ) );
        }
        printf("write!!\n");
        fprintf(fp,"name,data,data,data\n");
        fclose(fp);

        struct timeval _time;
  
        gettimeofday(&_time, NULL);    
        //UNIX時間の1970年1月1日からの経過秒数
        long sec = _time.tv_sec;
        //マイクロ秒　0から999999までの値を取り、一杯になると秒がカウントアップされていく
        long usec = _time.tv_usec;
        printf("%ld %ld\n",sec,usec);
        
		
		
        break;
    }
    return 0;
}