import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_catalogo import Catalogo, ErroCatalogo
from bd_planejador import JuncaoPlano, Planejador, ScanIndice, ScanSeq, conjuntos, explicar
from bd_sql_parser import parse


def catalogo(n_usuarios=10_000, n_pedidos=50_000):
    c = Catalogo()
    c.criar_tabela("usuarios", [("id", "INT", True), ("nome", "TEXT", False), ("idade", "INT", False)])
    c.criar_tabela("pedidos", [("id", "INT", True), ("uid", "INT", False), ("valor", "REAL", False)])
    c.criar_indice("idx_idade", "usuarios", "idade")
    c.criar_indice("idx_uid", "pedidos", "uid")
    c.tabela("usuarios").n_linhas = n_usuarios
    c.tabela("pedidos").n_linhas = n_pedidos
    return c


def plano(sql, cat=None):
    return Planejador(cat or catalogo()).planejar(parse(sql))


class TestPlanejador(unittest.TestCase):
    def test_conjuntos(self):
        w = parse("SELECT * FROM t WHERE a = 1 AND (b = 2 AND c = 3) AND d = 4").where
        self.assertEqual(len(conjuntos(w)), 4)
        self.assertEqual(conjuntos(None), [])

    def test_igualdade_na_pk_usa_indice(self):
        r = plano("SELECT * FROM usuarios WHERE id = 42").raiz
        self.assertIsInstance(r, ScanIndice)
        self.assertTrue(r.igualdade)
        self.assertEqual((r.indice, r.linhas_est), ("pk_usuarios", 1.0))

    def test_literal_a_esquerda(self):
        r = plano("SELECT * FROM usuarios WHERE 42 = id").raiz
        self.assertIsInstance(r, ScanIndice)
        r = plano("SELECT * FROM usuarios WHERE 18 < idade AND idade <= 20").raiz
        self.assertIsInstance(r, ScanIndice)
        self.assertEqual((r.lo, r.lo_incl, r.hi, r.hi_incl), (18, False, 20, True))

    def test_sem_indice_na_coluna_usa_varredura(self):
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE nome = 'ana'").raiz, ScanSeq)

    def test_intervalo_aberto_largo_prefere_varredura(self):
        # 25% de 10 mil linhas com acesso aleatório (x4) custa mais que ler tudo
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE idade > 30").raiz, ScanSeq)

    def test_intervalo_fechado_estreito_usa_indice(self):
        r = plano("SELECT * FROM usuarios WHERE idade BETWEEN 20 AND 25").raiz
        self.assertIsInstance(r, ScanIndice)
        self.assertEqual((r.lo, r.hi), (20, 25))

    def test_tabela_pequena_prefere_varredura(self):
        r = plano("SELECT * FROM usuarios WHERE idade = 30", catalogo(n_usuarios=5)).raiz
        self.assertIsInstance(r, ScanSeq)

    def test_igualdade_em_nao_unico_estima_mais_linhas_que_unico(self):
        r = plano("SELECT * FROM usuarios WHERE idade = 30").raiz
        self.assertIsInstance(r, ScanIndice)
        self.assertEqual(r.linhas_est, 1000.0)  # 10% de 10 mil
        c = catalogo()
        c.tabela("usuarios").indices["idx_idade"].unico = True
        self.assertEqual(plano("SELECT * FROM usuarios WHERE idade = 30", c).raiz.linhas_est, 1.0)

    def test_or_e_funcoes_impedem_indice(self):
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE id = 1 OR id = 2").raiz, ScanSeq)
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE id + 0 = 1").raiz, ScanSeq)
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE NOT id = 1").raiz, ScanSeq)

    def test_null_e_tipo_incompativel_nao_usam_indice(self):
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE id = NULL").raiz, ScanSeq)
        self.assertIsInstance(plano("SELECT * FROM usuarios WHERE id = 'x'").raiz, ScanSeq)

    def test_predicados_contraditorios_ainda_planejam(self):
        r = plano("SELECT * FROM usuarios WHERE id = 1 AND id = 2").raiz
        self.assertIsInstance(r, ScanIndice)

    def test_escolhe_o_indice_mais_barato(self):
        r = plano("SELECT * FROM usuarios WHERE idade BETWEEN 20 AND 25 AND id = 7").raiz
        self.assertEqual(r.coluna, "id")

    def test_juncao_equi_usa_hash_com_chaves_corretas(self):
        p = plano("SELECT * FROM usuarios u JOIN pedidos p ON p.uid = u.id")
        j = p.raiz
        self.assertIsInstance(j, JuncaoPlano)
        self.assertEqual(j.algoritmo, "hash")
        self.assertEqual((j.chave_esq.tabela, j.chave_dir.tabela), ("u", "p"))

    def test_juncao_nao_equi_usa_loop(self):
        j = plano("SELECT * FROM usuarios u JOIN pedidos p ON p.valor > u.idade").raiz
        self.assertEqual(j.algoritmo, "loop")
        j = plano("SELECT * FROM usuarios u JOIN pedidos p ON p.valor = p.uid").raiz
        self.assertEqual(j.algoritmo, "loop")

    def test_indice_so_na_tabela_base_com_coluna_qualificada(self):
        p = plano("SELECT * FROM usuarios u JOIN pedidos p ON p.uid = u.id WHERE u.id = 5")
        self.assertIsInstance(p.raiz.esq, ScanIndice)
        # coluna ambígua não qualificada não pode ir para o índice
        p = plano("SELECT * FROM usuarios u JOIN pedidos p ON p.uid = u.id WHERE id = 5")
        self.assertIsInstance(p.raiz.esq, ScanSeq)

    def test_erros(self):
        with self.assertRaises(ErroCatalogo):
            plano("SELECT * FROM fantasma")
        with self.assertRaises(ValueError):
            plano("SELECT * FROM usuarios u JOIN pedidos u ON u.id = u.uid")

    def test_explicar(self):
        txt = explicar(plano("SELECT * FROM usuarios u JOIN pedidos p ON p.uid = u.id WHERE u.id = 5"))
        self.assertIn("Junção[hash]", txt)
        self.assertIn("ScanIndice usuarios via pk_usuarios id = 5", txt)
        self.assertIn("ScanSeq pedidos", txt)
        with self.assertRaises(TypeError):
            explicar(object())


if __name__ == "__main__":
    unittest.main()
