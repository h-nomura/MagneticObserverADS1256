#include <stdio.h>
#include <time.h>

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
     logger();
     break;   
    }
    return 0;
}
int logger(){
    while(1){
        FILE *fp;
        char timeData[64];
        time_t t = time(NULL);
        strftime(timeData, sizeof(timeData), "MI%Y-%m-%d_%Hh%Mm%Ss.csv", localtime(&t));
        const char *fname = timeData;

        fp = fopen(fname,"w");
        if(fp == NULL){
            printf("%s file open errer!!\n",fname);
            return -1;
        }
        fprintf(fp,"name,data,data,data\n");
        fclose(fp);
        break;
    }
    return 0;
}