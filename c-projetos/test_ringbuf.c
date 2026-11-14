#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "ringbuf.h"

int main(void) {
    RingBuf *rb = rb_criar(8);
    assert(rb && rb_livre(rb) == 8);
    assert(rb_escrever(rb, "abcdef", 6) == 6);
    char buf[16];
    assert(rb_ler(rb, buf, 4) == 4 && memcmp(buf, "abcd", 4) == 0);
    /* Escrita que da a volta no buffer. */
    assert(rb_escrever(rb, "ghijkl", 6) == 6);
    assert(rb_tamanho(rb) == 8 && rb_livre(rb) == 0);
    assert(rb_escrever(rb, "z", 1) == 0); /* cheio */
    assert(rb_espiar(rb, buf, 3) == 3 && memcmp(buf, "efg", 3) == 0);
    assert(rb_tamanho(rb) == 8);
    assert(rb_ler(rb, buf, 16) == 8 && memcmp(buf, "efghijkl", 8) == 0);
    assert(rb_tamanho(rb) == 0 && rb_ler(rb, buf, 1) == 0);

    /* Fluxo longo: dados saem na mesma ordem em que entraram. */
    int prox_in = 0, prox_out = 0;
    for (int r = 0; r < 100; r++) {
        unsigned char in[5], out[5];
        for (int i = 0; i < 5; i++) in[i] = (unsigned char)prox_in++;
        size_t w = rb_escrever(rb, in, 5);
        prox_in -= 5 - (int)w;
        size_t l = rb_ler(rb, out, 3);
        for (size_t i = 0; i < l; i++) assert(out[i] == (unsigned char)prox_out++);
    }
    rb_liberar(rb);
    assert(rb_criar(0) == NULL);
    puts("ringbuf ok");
    return 0;
}
