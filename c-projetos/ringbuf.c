#include "ringbuf.h"
#include <stdlib.h>
#include <string.h>

RingBuf *rb_criar(size_t cap) {
    if (cap == 0) return NULL;
    RingBuf *rb = calloc(1, sizeof *rb);
    if (!rb) return NULL;
    rb->dados = malloc(cap);
    if (!rb->dados) { free(rb); return NULL; }
    rb->cap = cap;
    return rb;
}

void rb_liberar(RingBuf *rb) {
    if (!rb) return;
    free(rb->dados);
    free(rb);
}

size_t rb_tamanho(const RingBuf *rb) { return rb->tam; }
size_t rb_livre(const RingBuf *rb) { return rb->cap - rb->tam; }

size_t rb_escrever(RingBuf *rb, const void *src, size_t n) {
    if (n > rb_livre(rb)) n = rb_livre(rb);
    size_t fim = (rb->ini + rb->tam) % rb->cap;
    size_t ate_fim = rb->cap - fim;
    size_t p1 = n < ate_fim ? n : ate_fim;
    if (n) memcpy(rb->dados + fim, src, p1);
    if (n > p1) memcpy(rb->dados, (const unsigned char *)src + p1, n - p1);
    rb->tam += n;
    return n;
}

size_t rb_espiar(const RingBuf *rb, void *dst, size_t n) {
    if (n > rb->tam) n = rb->tam;
    size_t ate_fim = rb->cap - rb->ini;
    size_t p1 = n < ate_fim ? n : ate_fim;
    if (n) memcpy(dst, rb->dados + rb->ini, p1);
    if (n > p1) memcpy((unsigned char *)dst + p1, rb->dados, n - p1);
    return n;
}

size_t rb_ler(RingBuf *rb, void *dst, size_t n) {
    n = rb_espiar(rb, dst, n);
    rb->ini = (rb->ini + n) % rb->cap;
    rb->tam -= n;
    return n;
}
