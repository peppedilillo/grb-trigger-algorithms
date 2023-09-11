#ifndef GBM_BENCHMARK_TRIGGER_H
#define GBM_BENCHMARK_TRIGGER_H

#include <stdlib.h>
#include "queue.h"

#define FORE_LEN    256
#define QUEUE_LEN   (FORE_LEN + 1)
#define MAX_TEST    256

typedef enum status {
    ACQUIRING = 0,
    RUNNING = 1
} Status;

typedef struct trigger {
    int accumulator;
    int phase_counter;
    double maximum_significance;
    int time_offset;
    Queue *queue;
} Trigger;

void trigger_init(Trigger *trigger, Queue *queue);

void trigger_step(Trigger *trigger, int x_t, double b_t);

#endif //GBM_BENCHMARK_TRIGGER_H
