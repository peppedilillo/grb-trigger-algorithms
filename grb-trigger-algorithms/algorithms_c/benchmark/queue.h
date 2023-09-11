#ifndef GBM_BENCHMARK_QUEUE_H
#define GBM_BENCHMARK_QUEUE_H

#include <stdio.h>

typedef struct queue {
    int head;
    int tail;
    int len;
    int *data; // an array of length len + 1
} Queue;

void queue_init(Queue *q, int len, int *data);

int queue_empty(Queue *q);

int queue_full(Queue *q);

int queue_peek(Queue *q, int h);

void queue_enqueue(Queue *q, int n);

int queue_dequeue(Queue *q);

#endif //GBM_BENCHMARK_QUEUE_H
