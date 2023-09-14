#ifndef HERMES_FOCUS_FOCUS_H
#define HERMES_FOCUS_FOCUS_H

#include <stddef.h>

#define FOCUS_MAXCURVES 64
#define STACK_LEN (FOCUS_MAXCURVES + 1)

typedef struct {
    size_t trigger_time;
    size_t start_time;
    double significance;
} Changepoint;

typedef struct {
    int x;
    double b;
    int t;
    double m;
} Curve;

typedef struct {
    int head;
    int tail;
    int capacity;
    Curve *arr;
} Stack;

typedef struct {
    Stack *curves;
    double maximum;
    int time_offset;
    double mu_crit;
    double threshold;
} Focus;

void stack_init(Stack *s, int capacity, Curve *arr);

void focus_init(Focus *f, Stack *s, double threshold, double mu_min);

void focus_step(Focus *f, int x_t, double b_t);

Changepoint focus_interface(double threshold, double mu_min, int *xs, double *bs, size_t len);

void focus_print(size_t t, int x_t, double b_t, Focus *f);

#endif //HERMES_FOCUS_FOCUS_H
