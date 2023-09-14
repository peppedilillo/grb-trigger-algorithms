#include <math.h>
#include <assert.h>
#include <stdio.h>
#include <limits.h>
#include "pfocus.h"

static Curve NULL_CURVE = (Curve) {0};
static Curve TAIL_CURVE = (Curve) {INT_MAX, 0., 0, 0.};

void stack_init(Stack *s, int capacity, Curve *arr) {
    s->head = 0;
    s->tail = 0;
    s->capacity = capacity;
    s->arr = arr;
}

int stack_empty(Stack *s) {
    return s->head == s->tail;
}

int stack_full(Stack *s) {
    return s->head == s->capacity ? s->tail == 0 : s->head + 1 == s->tail;
}

void stack_push(Stack *s, Curve *q) {
    if (stack_full(s)) {
        s->tail == s->capacity ? s->tail = 0 : s->tail++;
        *(s->arr + s->tail) = TAIL_CURVE;
    }
    *(s->arr + s->head) = *q;
    s->head == s->capacity ? s->head = 0 : s->head++;
}

Curve *stack_pop(Stack *s) {
    assert(!stack_empty(s));
    s->head == 0 ? s->head = s->capacity : s->head--;
    return s->arr + s->head;
}

Curve *stack_peek(Stack *s) {
    assert(!stack_empty(s));
    return s->arr + (s->head == 0 ? s->capacity - 1 : s->head - 1);
}

void stack_reset(Stack *s) {
    s->head = 0;
    s->tail = 0;
}

double curve_max(Curve *c, Curve *acc) {
    int x = (acc->x - c->x);
    double b = (acc->b - c->b);
    assert(x > b);
    return x * log(x / b) - (x - b);
}

int curve_dominate(Curve *p, Curve *q, Curve *acc) {
    if ((acc->x - p->x) * (acc->b - q->b) - (acc->x - q->x) * (acc->b - p->b) > 0)
        return +1;
    return -1;
}

void focus_init(Focus *f, Stack *s, double threshold, double mu_min) {
    assert(!(mu_min < 1));
    f->maximum = 0.;
    f->time_offset = 0;
    f->curves = s;
    f->threshold = threshold * threshold / 2;
    f->ab_critical = (mu_min == 1. ? 1.0 : (mu_min - 1) / log(mu_min));

    stack_push(s, &TAIL_CURVE);
    stack_push(s, &NULL_CURVE);
}

void focus_maximize(Focus *f, Curve *p, Curve *acc) {
    Stack *curves = f->curves;
    double m = acc->m - p->m;
    int i = curves->head;
    while (m + p->m >= f->threshold) {
        if (m >= f->threshold) {
            f->maximum = m;
            f->time_offset = acc->t - p->t;
            break;
        }
        i == 0 ? i = curves->capacity : i--;
        p = (curves->arr + i);
        m = curve_max(p, acc);
    }
}

void focus_step(Focus *f, int x_t, double b_t) {
    Stack *curves = f->curves;
    Curve *p = stack_pop(curves);
    Curve acc = {p->x + x_t, p->b + b_t, p->t + 1, p->m};
    while (curve_dominate(p, stack_peek(curves), &acc) < 0)
        p = stack_pop(curves);

    if ((acc.x - p->x) > f->ab_critical * (acc.b - p->b)) {
        double m = curve_max(p, &acc);
        acc.m = p->m + m;
        focus_maximize(f, p, &acc);
        stack_push(curves, p);
        stack_push(curves, &acc);
    } else {
        stack_reset(curves);
        stack_push(curves, &TAIL_CURVE);
        stack_push(curves, &NULL_CURVE);
    }
}

void focus_print(size_t t, int x_t, double b_t, Focus *f) {
    Curve *q, *acc = stack_pop(f->curves);
    printf("t = %zu, x = %d, b = %.2f, max = %.2f, toff = %d, curves: ",
           t, x_t, b_t, f->maximum, -f->time_offset);
    int i = f->curves->tail == f->curves->capacity ? 0 : f->curves->tail + 1;
    while (i != f->curves->head) {
        q = (f->curves->arr + i);
        printf("(%d, %.2f, %d, %.2f) ",
               +(acc->x - q->x),
               -(acc->b - q->b),
               -(acc->t - q->t),
               q->m);
        i == f->curves->capacity ? i = 0 : i++;
    }
    printf("\n");
    stack_push(f->curves, acc);
}

Changepoint focus_interface(double threshold, double mu_min, int *xs, double *bs, size_t len) {
    Curve curve_buffer[STACK_LEN];
    Stack curves;
    Focus focus;
    stack_init(&curves, FOCUS_MAXCURVES, curve_buffer);
    focus_init(&focus, &curves, threshold, mu_min);

    size_t t;
    for (t = 0; t < len; t++) {
        focus_step(&focus, xs[t], bs[t]);
#ifndef NDEBUG
        focus_print(t, xs[t], bs[t], &focus);
#endif
        if (focus.maximum)
            break;
    }
    Changepoint c = {t, t - focus.time_offset + 1, sqrt(2 * focus.maximum)};
    return c;
}
