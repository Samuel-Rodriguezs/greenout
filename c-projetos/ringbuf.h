#ifndef RINGBUF_H
#define RINGBUF_H
#include <stddef.h>

/* Buffer circular de bytes (produtor/consumidor, sem threads). */
typedef struct {
    unsigned char *dados;
    size_t cap, ini, tam;
} RingBuf;

RingBuf *rb_criar(size_t cap);
void rb_liberar(RingBuf *rb);
/* Escreve ate n bytes; retorna quantos couberam. */
size_t rb_escrever(RingBuf *rb, const void *src, size_t n);
/* Le ate n bytes (consome); retorna quantos foram lidos. */
size_t rb_ler(RingBuf *rb, void *dst, size_t n);
/* Espia sem consumir. */
size_t rb_espiar(const RingBuf *rb, void *dst, size_t n);
size_t rb_tamanho(const RingBuf *rb);
size_t rb_livre(const RingBuf *rb);

#endif
