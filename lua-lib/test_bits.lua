local B = require("bits")

-- máscara
assert(B.mascara(1) == 1 and B.mascara(8) == 255 and B.mascara(32) == 0xFFFFFFFF and B.mascara(64) == -1)
assert(not pcall(B.mascara, 0) and not pcall(B.mascara, 65))

-- contar bits
assert(B.contar(0) == 0 and B.contar(1) == 1 and B.contar(255) == 8 and B.contar(0xF0F0) == 8)
assert(B.contar(-1) == 64 and B.contar(math.mininteger) == 1 and B.contar(math.maxinteger) == 63)
assert(not pcall(B.contar, 1.5) and not pcall(B.contar, "1"))

-- testar/definir/limpar/alternar
assert(B.testar(5, 0) and not B.testar(5, 1) and B.testar(5, 2))
assert(B.testar(-1, 63) and B.testar(math.mininteger, 63))
assert(B.definir(0, 3) == 8 and B.definir(8, 3) == 8)
assert(B.limpar(15, 0) == 14 and B.limpar(14, 0) == 14)
assert(B.alternar(5, 1) == 7 and B.alternar(7, 1) == 5)
assert(B.definir(0, 63) == math.mininteger)
assert(not pcall(B.testar, 1, 64) and not pcall(B.definir, 1, -1))

-- potência de dois, bit baixo, paridade
assert(B.potencia_de_dois(1) and B.potencia_de_dois(1024) and not B.potencia_de_dois(0))
assert(not B.potencia_de_dois(6) and not B.potencia_de_dois(-8))
assert(B.bit_baixo(12) == 4 and B.bit_baixo(0) == 0 and B.bit_baixo(7) == 1)
assert(B.paridade(7) == 1 and B.paridade(3) == 0 and B.paridade(0) == 0)

-- rotação
assert(B.girar_esq(0x80000001, 1) == 0x00000003)
assert(B.girar_dir(0x00000003, 1) == 0x80000001)
assert(B.girar_esq(1, 0) == 1 and B.girar_esq(1, 32) == 1 and B.girar_esq(1, 33) == 2)
assert(B.girar_esq(1, 3, 4) == 8)
assert(B.girar_esq(0x81, 1, 8) == 0x03 and B.girar_dir(0x03, 1, 8) == 0x81)
assert(B.girar_esq(1, 1, 64) == 2 and B.girar_esq(math.mininteger, 1, 64) == 1)
assert(B.girar_dir(1, 1, 64) == math.mininteger)
assert(B.girar_dir(B.girar_esq(0xDEADBEEF, 13), 13) == 0xDEADBEEF)
assert(B.girar_esq(-1, 5, 8) == 255)         -- bits acima da largura são descartados

-- inverter
assert(B.inverter(0, 8) == 255 and B.inverter(0xFF, 8) == 0 and B.inverter(0) == 0xFFFFFFFF)
assert(B.inverter(5, 4) == 10)

-- binário
assert(B.para_binario(0) == "0" and B.para_binario(5) == "101" and B.para_binario(5, 8) == "00000101")
assert(B.para_binario(255, 4) == "11111111")
assert(B.para_binario(-1) == string.rep("1", 64) and #B.para_binario(math.mininteger) == 64)
assert(B.de_binario("101") == 5 and B.de_binario("0") == 0 and B.de_binario("00000101") == 5)
assert(B.de_binario(string.rep("1", 64)) == -1)
for _, n in ipairs { 0, 1, 42, 123456789, math.maxinteger, math.mininteger, -7 } do
  assert(B.de_binario(B.para_binario(n)) == n)
end
assert(B.de_binario("") == nil and B.de_binario("102") == nil and B.de_binario(string.rep("1", 65)) == nil)
assert(select(2, B.de_binario("x")) == "binario invalido")

-- empacotar u32
assert(B.empacotar_u32(0x01020304) == "\1\2\3\4")
assert(B.desempacotar_u32("\1\2\3\4") == 0x01020304)
assert(B.desempacotar_u32(B.empacotar_u32(0xFFFFFFFF)) == 0xFFFFFFFF)
assert(B.empacotar_u32(-1) == "\255\255\255\255" and B.empacotar_u32(0x1FFFFFFFF) == "\255\255\255\255")
assert(not pcall(B.desempacotar_u32, "abc"))
print("ok")
