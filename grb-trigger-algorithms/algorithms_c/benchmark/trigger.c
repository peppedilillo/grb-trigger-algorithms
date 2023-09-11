#include <math.h>
#include <assert.h>
#include <limits.h>

#include "trigger.h"
#include "queue.h"


void trigger_init(Trigger *trigger, Queue *queue) {
    trigger->accumulator = 0;
    trigger->phase_counter = -1;
    trigger->maximum_significance = 0.0;
    trigger->time_offset = 0;
    trigger->queue = queue;
    /*
    * this allows to 1. only check trigger status once per iteration; and 2.
    * to starts maximizing as soon as the recent count queue is full.
    * removing it the algorithm will start running one iteration later.
    */
    queue_enqueue(queue, 0);
}

enum status trigger_status(Trigger *trigger) {
    if (trigger->phase_counter < 0)
        return ACQUIRING;
    return RUNNING;
}

void trigger_rebase(Trigger *trigger) {
    int i = trigger->queue->head;
    int base_value = *(trigger->queue->data + trigger->queue->head);
    while (i != trigger->queue->tail) {
        *(trigger->queue->data + i) -= base_value;
        if (i > trigger->queue->len)
            i = 0;
    }
    trigger->accumulator -= base_value;
}

int trigger_ready(Trigger *trigger) {
    assert(trigger_status(trigger) == ACQUIRING);
    return queue_full(trigger->queue);
}

void trigger_set_running(Trigger *trigger) {
    assert(trigger_status(trigger) == ACQUIRING);
    trigger->phase_counter = 0;
}

void trigger_acquire(Trigger *trigger) {
    assert(trigger_status(trigger) == ACQUIRING);
    queue_enqueue(trigger->queue, trigger->accumulator);
}

void trigger_update(Trigger *trigger) {
    assert(trigger_status(trigger) == RUNNING);
    queue_dequeue(trigger->queue);
    queue_enqueue(trigger->queue, trigger->accumulator);
    trigger->phase_counter = (trigger->phase_counter + 1) % trigger->queue->len;
}

double significance(int n, double b) {
    assert((n >= 0) & (b > 0));

    if (n > b)
        return n * log(n / b) - b * (n / b - 1);
    return 0.0;
}

void trigger_maximize(Trigger *trigger, double b_t) {
    assert(trigger_status(trigger) == RUNNING);
    int sum;
    double s;

    trigger->maximum_significance = 0.;
    trigger->time_offset = 0;
    for (int h = 1; h <= MAX_TEST; h = 2 * h) {
        sum = trigger->accumulator - queue_peek(trigger->queue, h);
        s = significance(sum, b_t * h);
        if (s > trigger->maximum_significance) {
            trigger->maximum_significance = s;
            trigger->time_offset = -h;
        }
        if ((trigger->phase_counter % h) ? 1 : 0)
            break;
    }
}

void trigger_step(Trigger *trigger, int x_t, double b_t) {
    if (trigger->accumulator >= INT_MAX - x_t)
        trigger_rebase(trigger);
    trigger->accumulator += x_t;

    if (trigger_status(trigger) == RUNNING) {
        trigger_maximize(trigger, b_t);
        trigger_update(trigger);
    } else if (trigger_status(trigger) == ACQUIRING) {
        trigger_acquire(trigger);
        if (trigger_ready(trigger))
            trigger_set_running(trigger);
    } else { ;
    }
}
