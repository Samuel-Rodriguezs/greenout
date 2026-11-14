#include "vm.h"
#include <string.h>

static int tem_operando(int op) {
    return op == OP_PUSH || op == OP_JMP || op == OP_JZ;
}

size_t vm_emitir(unsigned char *cod, size_t pos, int op, int operando) {
    cod[pos++] = (unsigned char)op;
    if (tem_operando(op)) {
        unsigned u = (unsigned)operando;
        for (int i = 0; i < 4; i++) cod[pos++] = (unsigned char)(u >> (8 * i));
    }
    return pos;
}

static int le_i32(const unsigned char *p) {
    unsigned u = 0;
    for (int i = 0; i < 4; i++) u |= (unsigned)p[i] << (8 * i);
    return (int)u;
}

VMErro vm_executar(VM *vm, const unsigned char *cod, size_t tam) {
    vm->sp = 0;
    vm->n_saida = 0;
    size_t pc = 0;
    long passos = 0;
    while (1) {
        if (pc >= tam) return VM_FORA_DO_CODIGO;
        if (++passos > 1000000) return VM_LIMITE_PASSOS;
        int op = cod[pc++], arg = 0;
        if (tem_operando(op)) {
            if (pc + 4 > tam) return VM_FORA_DO_CODIGO;
            arg = le_i32(cod + pc);
            pc += 4;
        }
        int a, b;
        switch (op) {
        case OP_PUSH:
            if (vm->sp >= VM_PILHA_MAX) return VM_PILHA_CHEIA;
            vm->pilha[vm->sp++] = arg;
            break;
        case OP_ADD: case OP_SUB: case OP_MUL: case OP_DIV:
        case OP_LT: case OP_EQ:
            if (vm->sp < 2) return VM_PILHA_VAZIA;
            b = vm->pilha[--vm->sp];
            a = vm->pilha[vm->sp - 1];
            if (op == OP_DIV && b == 0) return VM_DIV_ZERO;
            /* soma/sub/mul via unsigned evita overflow indefinido */
            vm->pilha[vm->sp - 1] =
                op == OP_ADD ? (int)((unsigned)a + (unsigned)b) :
                op == OP_SUB ? (int)((unsigned)a - (unsigned)b) :
                op == OP_MUL ? (int)((unsigned)a * (unsigned)b) :
                op == OP_DIV ? (b == -1 ? (int)(0u - (unsigned)a) : a / b) :
                op == OP_LT ? a < b : a == b;
            break;
        case OP_DUP:
            if (vm->sp < 1) return VM_PILHA_VAZIA;
            if (vm->sp >= VM_PILHA_MAX) return VM_PILHA_CHEIA;
            vm->pilha[vm->sp] = vm->pilha[vm->sp - 1];
            vm->sp++;
            break;
        case OP_SWAP:
            if (vm->sp < 2) return VM_PILHA_VAZIA;
            a = vm->pilha[vm->sp - 1];
            vm->pilha[vm->sp - 1] = vm->pilha[vm->sp - 2];
            vm->pilha[vm->sp - 2] = a;
            break;
        case OP_POP:
            if (vm->sp < 1) return VM_PILHA_VAZIA;
            vm->sp--;
            break;
        case OP_JMP:
            if (arg < 0 || (size_t)arg >= tam) return VM_FORA_DO_CODIGO;
            pc = (size_t)arg;
            break;
        case OP_JZ:
            if (vm->sp < 1) return VM_PILHA_VAZIA;
            if (vm->pilha[--vm->sp] == 0) {
                if (arg < 0 || (size_t)arg >= tam) return VM_FORA_DO_CODIGO;
                pc = (size_t)arg;
            }
            break;
        case OP_PRINT:
            if (vm->sp < 1) return VM_PILHA_VAZIA;
            if (vm->n_saida >= VM_SAIDA_MAX) return VM_SAIDA_CHEIA;
            vm->saida[vm->n_saida++] = vm->pilha[--vm->sp];
            break;
        case OP_HALT:
            return VM_OK;
        default:
            return VM_OPCODE_INVALIDO;
        }
    }
}
