CC     = gcc
CFLAGS = -Wall -Wextra -Werror -std=c11 -fsanitize=address,undefined -g

# Cada test_<nome>.c e compilado junto com <nome>.c (lista por wildcard).
TESTS := $(patsubst %.c,%,$(wildcard test_*.c))

.PHONY: test clean

test: $(TESTS)
	@for t in $(TESTS); do \
		echo "== $$t"; ./$$t || exit 1; \
	done
	@echo "Todos os testes de estruturas em C passaram."

test_%: test_%.c %.c %.h
	$(CC) $(CFLAGS) -o $@ test_$*.c $*.c

clean:
	rm -f $(TESTS)
