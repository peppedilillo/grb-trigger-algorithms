#include <assert.h>
#include "queue.h"

void queue_init(Queue *q, int len, int *data) {
    q->head = 0;
    q->tail = 0;
    q->len = len;
    q->data = data; // an array of length `len + 1`
}

int queue_empty(Queue *q) {
    return q->head == q->tail;
}

int queue_full(Queue *q) {
    return (q->tail + 1) % (q->len + 1) == q->head;
}

void queue_enqueue(Queue *q, int n) {
    assert(!queue_full(q));
    q->data[q->tail++] = n;
    if (q->tail > q->len)
        q->tail = 0;
}

int queue_dequeue(Queue *q) {
    assert(!queue_empty(q));
    int t = q->data[q->head++];
    if (q->head > q->len)
        q->head = 0;
    return t;
}

int queue_peek(Queue *q, int h) {
    assert(h > 0);
    assert(h <= q->len);
    int n = (q->head + (q->len - h)) % (q->len + 1);
    return q->data[n];
}
