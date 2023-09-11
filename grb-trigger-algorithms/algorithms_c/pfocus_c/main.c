#include <stdio.h>
#include <stdlib.h>

#include "pfocus.h"

#define LINEIN_MAXSIZE 100

char char_buffer[LINEIN_MAXSIZE];

size_t get_events_number(FILE *fp) {
    // Count Lines
    int cr = 0;
    int iscomment = 0;
    size_t length = 0;

    while (cr != EOF) {
        if (cr == '#')
            iscomment = 1;
        if (cr == '\n') {
            if (!iscomment)
                length++;
            else
                iscomment = 0;
        }
        cr = getc(fp);
    }
    rewind(fp);
    return length;
}

int get_lambda(double *lambda, FILE *fp) {
    if (fgets(char_buffer, LINEIN_MAXSIZE, fp) == NULL) {
        perror("fscanf ");
        return 1;
    }
    if (*char_buffer != '#') {
        perror("background");
        return 2;
    }
    *lambda = strtod(char_buffer + 1, NULL);
    return 0;
}

int get_count(int *n, FILE *fp) {
    if (fgets(char_buffer, LINEIN_MAXSIZE, fp) == NULL) {
        perror("fscanf ");
        return 1;
    }
    *n = (int) strtol(char_buffer, NULL, 10);
    return 0;
}

int main(int argc, char *argv[]) {
    size_t len;
    double true_rate;

    // reads file
    if (argc == 1) {
        perror("input ");
        return 1;
    }
    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror("fopen ");
        return 2;
    }
    len = get_events_number(fp);
    get_lambda(&true_rate, fp);
    int x;
    int *xs = (int *) malloc(len * sizeof(int));
    double *bs = (double *) malloc(len * sizeof(double));

    for (size_t i = 0; i < len; i++) {
        get_count(&x, fp);
        xs[i] = x;
        bs[i] = true_rate;
    }
    fclose(fp);

    double threshold = 5.0, mu_min = 1.1;
    Changepoint c;
    c = focus_interface(threshold, mu_min, xs, bs, len);
    printf("significance: %.2f, change time: %zu, trigger time: %zu\n",
           c.significance,
           c.start_time,
           c.trigger_time);
}
