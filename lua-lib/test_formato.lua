local F = require("formato")

-- bytes
assert(F.bytes(0) == "0 B" and F.bytes(1) == "1 B" and F.bytes(1023) == "1023 B")
assert(F.bytes(1024) == "1 KB" and F.bytes(1536) == "1.5 KB")
assert(F.bytes(1024 * 1024) == "1 MB" and F.bytes(5 * 1024 ^ 3) == "5 GB")
assert(F.bytes(1234567) == "1.18 MB")
assert(F.bytes(1234567, 0) == "1 MB")
assert(F.bytes(1234567, 3) == "1.177 MB")
assert(F.bytes(-2048) == "-2 KB")
assert(F.bytes(1024 ^ 6) == "1024 PB")       -- além da maior unidade
assert(F.bytes(100.7) == "100 B")
assert(not pcall(F.bytes, "x") and not pcall(F.bytes, 0 / 0))

-- duração
assert(F.duracao(0) == "0s" and F.duracao(59) == "59s" and F.duracao(60) == "1m")
assert(F.duracao(3661) == "1h 1m 1s" and F.duracao(3600) == "1h")
assert(F.duracao(90061) == "1d 1h 1m 1s" and F.duracao(86400 * 3) == "3d")
assert(F.duracao(59.9) == "59s" and F.duracao(0.5) == "0s")
assert(not pcall(F.duracao, -1) and not pcall(F.duracao, "1"))

-- análise de duração
assert(F.analisar_duracao("90s") == 90 and F.analisar_duracao("1h30m") == 5400)
assert(F.analisar_duracao("2d 4s") == 172804 and F.analisar_duracao(" 1m ") == 60)
for _, s in ipairs { 0, 5, 3661, 90061, 86400 } do
  assert(F.analisar_duracao(F.duracao(s)) == (s == 0 and 0 or s) or s == 0)
end
local r, e = F.analisar_duracao("")
assert(r == nil and e == "duracao vazia")
assert(select(2, F.analisar_duracao("10")) == "duracao invalida")
assert(select(2, F.analisar_duracao("abc")) == "duracao invalida")
assert(select(2, F.analisar_duracao("1x")) == "duracao invalida")

-- milhares
assert(F.milhares(0) == "0" and F.milhares(12) == "12" and F.milhares(999) == "999")
assert(F.milhares(1000) == "1.000" and F.milhares(1234567) == "1.234.567")
assert(F.milhares(-1234) == "-1.234" and F.milhares(123456) == "123.456")
assert(F.milhares(1234567, ",") == "1,234,567")
assert(F.milhares(1234.5) == "1.234.5")
assert(not pcall(F.milhares, "abc"))

-- percentual
assert(F.percentual(0.256) == "25.6%" and F.percentual(1, 0) == "100%" and F.percentual(0) == "0.0%")
print("ok")
