#include "palindromo.h"

#include <ctype.h>
#include <string.h>

bool eh_palindromo(const char *s) {
    size_t i = 0;
    size_t j = strlen(s);
    while (i < j) {
        if (!isalnum((unsigned char)s[i])) {
            i++;
        } else if (!isalnum((unsigned char)s[j - 1])) {
            j--;
        } else {
            if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j - 1])) {
                return false;
            }
            i++;
            j--;
        }
    }
    return true;
}
