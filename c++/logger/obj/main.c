#include <stdio.h>
#include <time.h>

#include <stdlib.h>

#include <string.h>

// #include <cstdio> // for perror
// #include <ctime>

#include <signal.h>     //signal()
#include "ADS1256.h"
#include "stdio.h"
#include <sys/timeb.h>

int logger(void);
void  Handler(int signo);
double get_data(void);
void strTime(char output[32]);

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
    strftime(timeData,sizeof(timeData), "%Y-%m-%d,1ch(nT),2ch(nT),3ch(nT),4ch(nT)\n", localtime(&t));   
    fprintf(fp,timeData);
    int num = 0;
    UBYTE i = 0;
    // double data = 0;
    double ADC[4] = {0,0,0,0};
    printf("ADC1256 setup start!!\n");
    /////////
    DEV_ModuleInit();
    // Exception handling:ctrl + c
    signal(SIGINT, Handler);

    if(ADS1256_init() == 1){
        printf("\r\nEND                  \r\n");
        DEV_ModuleExit();
        exit(0);
    }
    ADS1256_ConfigADC(ADS1256_GAIN_1,ADS1256_10SPS);
    ADS1256_SetMode(1);//Differential mode
    ////////////


    while(num < 100){
        // t = time(NULL);
        // strftime(timeData, sizeof(timeData), "%H:%M:%S.%n", localtime(&t));
        strTime(timeData);
        for(i = 0;i < 4;i++){
            ADC[i] = ADS1256_GetChannalValue(i)*5.0/0x7fffff;
        }
        snprintf(buf,sizeof(buf),",%f,%f,%f,%f\n",ADC[0],ADC[1],ADC[2],ADC[3]);
        strcat(timeData,buf);
        fprintf(fp,timeData);
        num++;
    }
    fclose(fp);
    return 0;
}
void  Handler(int signo){
    //System Exit
    printf("\r\nEND                  \r\n");
    DEV_ModuleExit();

    exit(0);
}

double get_data(void){
    return rand()/10000;
}

void strTime(char output[32]){
    struct timespec ts;
    struct tm t;
    int ret;

    // Get epoch time
    ret = clock_gettime(CLOCK_REALTIME, &ts);
    if (ret < 0) {
        perror("clock_gettime fail");
    }

    // Convert into local and parsed time
    localtime_r(&ts.tv_sec, &t);

    // Create string with strftime
    char buf[32];
    ret = strftime(buf, 32, "%H:%M:%S", &t);
    if (ret == 0) {
        perror("strftime fail");
    }

    // Add milli-seconds with snprintf
    //   char output[32];
    const int microsec = ts.tv_nsec / 1000;
    ret = snprintf(output, 32, "%s.%06d", buf, microsec);
    if (ret == 0) {
        perror("snprintf fail");
    }
}