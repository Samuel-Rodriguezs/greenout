#include <assert.h>

#include "palindromo.h"

int main(void) {
    assert(eh_palindromo(""));
    assert(eh_palindromo("a"));
    assert(eh_palindromo("arara"));
    assert(eh_palindromo("Socorram-me, subi no onibus em Marrocos"));
    assert(eh_palindromo("A man, a plan, a canal: Panama"));
    assert(!eh_palindromo("python"));
    assert(!eh_palindromo("ab"));
    assert(eh_palindromo("!!!"));
    return 0;
}
