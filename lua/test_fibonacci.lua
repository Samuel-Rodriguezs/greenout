local f = require("fibonacci")
assert(f.fib(0) == 0 and f.fib(1) == 1 and f.fib(2) == 1)
assert(f.fib(10) == 55)
assert(f.fib(50) == 12586269025)   -- rápido graças ao cache
assert(f.fib(90) == 2880067194370816120)
for i = 0, 40 do assert(f.fib(i) == f.fib_iterativo(i)) end
assert(not pcall(f.fib, -1))
assert(not pcall(f.fib, 1.5))
print("ok")
