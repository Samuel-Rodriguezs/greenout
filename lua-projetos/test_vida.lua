local v = require("vida")
-- bloco (natureza morta) permanece
local b = v.de_texto({"....", ".##.", ".##.", "...."})
assert(v.para_texto(v.passo(b)) == v.para_texto(b))
assert(v.populacao(b) == 4)
-- blinker oscila com período 2
local h = v.de_texto({".....", "..#..", "..#..", "..#..", "....."})
local h1 = v.passo(h)
assert(v.para_texto(h1) == ".....\n.....\n.###.\n.....\n.....")
assert(v.para_texto(v.passo(h1)) == v.para_texto(h))
assert(v.para_texto(v.geracoes(h, 10)) == v.para_texto(h))
-- planador: após 4 gerações desloca-se (1,1)
local p = v.de_texto({".#....", "..#...", "###...", "......", "......", "......"})
local p4 = v.geracoes(p, 4)
assert(v.para_texto(p4) == "......\n..#...\n...#..\n.###..\n......\n......")
-- grade vazia e célula solitária morrem
assert(v.populacao(v.passo(v.de_texto({"...", "...", "..."}))) == 0)
assert(v.populacao(v.passo(v.de_texto({"...", ".#.", "..."}))) == 0)
-- zero gerações devolve o mesmo estado
assert(v.para_texto(v.geracoes(h, 0)) == v.para_texto(h))
-- vizinhos nos cantos não estouram
assert(v.vizinhos(b, 1, 1) == 1)
-- linhas irregulares são preenchidas com mortas
local irr = v.de_texto({"#", "###"})
assert(irr.largura == 3 and irr.c[1][3] == false)
print("ok")
