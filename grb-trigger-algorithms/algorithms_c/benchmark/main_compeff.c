#include <stdio.h>
#include <time.h>
#include "trigger.h"

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
    // reads background value
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

    for (size_t i = 0; i < len; i++) {
        get_count(&x, fp);
        xs[i] = x;
    }
    fclose(fp);

    int queue_buffer[QUEUE_LEN] = {0};
    Queue queue;
    Trigger trigger;
    queue_init(&queue, FORE_LEN, queue_buffer);
    trigger_init(&trigger, &queue);

    clock_t start_clk = clock();
    for (size_t i = 0; i < len; i++) {
        trigger_step(&trigger, xs[i], true_rate);
    }
    printf("%Lg s.\n", (clock() - start_clk) / (long double) CLOCKS_PER_SEC);
    return 0;
}
