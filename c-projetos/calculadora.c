#include "calculadora.h"
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define MAX 128

static int prec(char op) {
    switch (op) {
    case '+': case '-': return 1;
    case '*': case '/': return 2;
    case '^': return 3;
    case 'n': return 4; /* negacao unaria */
    }
    return 0;
}

static int direita(char op) { return op == '^' || op == 'n'; }

/* Aplica um operador sobre a pilha de valores. */
static int aplicar(char op, double *val, int *nv) {
    if (op == 'n') {
        if (*nv < 1) return -1;
        val[*nv - 1] = -val[*nv - 1];
        return 0;
    }
    if (*nv < 2) return -1;
    double b = val[--*nv], a = val[*nv - 1], r;
    switch (op) {
    case '+': r = a + b; break;
    case '-': r = a - b; break;
    case '*': r = a * b; break;
    case '/': if (b == 0) return -1; r = a / b; break;
    case '^': r = pow(a, b); break;
    default: return -1;
    }
    val[*nv - 1] = r;
    return 0;
}

int calcular(const char *expr, double *res) {
    double val[MAX]; int nv = 0;
    char ops[MAX]; int no = 0;
    int esperaOperando = 1;
    const char *p = expr;
    while (*p) {
        if (isspace((unsigned char)*p)) { p++; continue; }
        if (isdigit((unsigned char)*p) || *p == '.') {
            if (!esperaOperando || nv >= MAX) return -1;
            char *fim;
            val[nv++] = strtod(p, &fim);
            if (fim == p) return -1;
            p = fim;
            esperaOperando = 0;
        } else if (*p == '(') {
            if (!esperaOperando || no >= MAX) return -1;
            ops[no++] = *p++;
        } else if (*p == ')') {
            if (esperaOperando) return -1;
            while (no > 0 && ops[no - 1] != '(')
                if (aplicar(ops[--no], val, &nv)) return -1;
            if (no == 0) return -1;
            no--; p++;
        } else if (strchr("+-*/^", *p)) {
            char op = *p++;
            if (esperaOperando) {
                if (op != '-') return -1;
                op = 'n';
            } else {
                esperaOperando = 1;
            }
            while (no > 0 && ops[no - 1] != '(' &&
                   (prec(ops[no - 1]) > prec(op) ||
                    (prec(ops[no - 1]) == prec(op) && !direita(op))))
                if (aplicar(ops[--no], val, &nv)) return -1;
            if (no >= MAX) return -1;
            ops[no++] = op;
        } else return -1;
    }
    if (esperaOperando) return -1;
    while (no > 0) {
        if (ops[no - 1] == '(') return -1;
        if (aplicar(ops[--no], val, &nv)) return -1;
    }
    if (nv != 1) return -1;
    *res = val[0];
    return 0;
}
