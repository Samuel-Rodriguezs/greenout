#ifndef VM_H
#define VM_H
#include <stddef.h>

/* VM de pilha com bytecode. Cada instrucao e um byte de opcode; PUSH, JMP
 * e JZ sao seguidos de um operando int32 (little-endian). */
enum {
    OP_PUSH, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_DUP, OP_SWAP, OP_POP,
    OP_LT,   /* a b -> (a < b) */
    OP_EQ,   /* a b -> (a == b) */
    OP_JMP,  /* endereco absoluto */
    OP_JZ,   /* desvia se topo == 0 (consome) */
    OP_PRINT, /* empilha no buffer de saida */
    OP_HALT
};

typedef enum {
    VM_OK, VM_PILHA_VAZIA, VM_PILHA_CHEIA, VM_DIV_ZERO,
    VM_OPCODE_INVALIDO, VM_FORA_DO_CODIGO, VM_SAIDA_CHEIA, VM_LIMITE_PASSOS
} VMErro;

#define VM_PILHA_MAX 256
#define VM_SAIDA_MAX 256

typedef struct {
    int pilha[VM_PILHA_MAX];
    int sp;
    int saida[VM_SAIDA_MAX]; /* valores emitidos por PRINT */
    int n_saida;
} VM;

/* Executa o bytecode ate HALT. Retorna VM_OK ou o erro encontrado. */
VMErro vm_executar(VM *vm, const unsigned char *cod, size_t tam);
/* Auxiliar para montar bytecode: grava op (e operando se houver).
 * Retorna o novo tamanho. */
size_t vm_emitir(unsigned char *cod, size_t pos, int op, int operando);

#endif
