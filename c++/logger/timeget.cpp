#include <iostream>
#include <cstdio> // for perror
#include <ctime>
void strTime(char output[32]);

int main(void) {
    char timedata[32];
    strTime(timedata);
    printf(timedata);
    return 0;
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
    ret = strftime(buf, 32, "%Y/%m/%d %H:%M:%S", &t);
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