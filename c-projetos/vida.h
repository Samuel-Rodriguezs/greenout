#ifndef VIDA_H
#define VIDA_H

/* Jogo da vida de Conway em grade toroidal (com wrap nas bordas). */
typedef struct {
    int lin, col;
    unsigned char *cel; /* lin*col celulas: 0 morta, 1 viva */
} Vida;

Vida *vida_criar(int lin, int col);
void vida_liberar(Vida *v);
void vida_set(Vida *v, int l, int c, int viva);
int vida_get(const Vida *v, int l, int c);
/* Avanca uma geracao. */
void vida_passo(Vida *v);
/* Numero de celulas vivas. */
int vida_populacao(const Vida *v);

#endif
