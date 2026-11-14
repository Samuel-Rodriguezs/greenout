import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_hfsm import Estado, HFSM, Transicao


def montar(log):
    def reg(nome):
        return dict(ao_entrar=lambda c: log.append(f"+{nome}"), ao_sair=lambda c: log.append(f"-{nome}"))

    m = HFSM()
    m.adicionar(Estado("vivo", inicial="parado", **reg("vivo"),
                       transicoes=[Transicao("morto", evento="morrer")]))
    m.adicionar(Estado("parado", pai="vivo", **reg("parado"),
                       transicoes=[Transicao("andando", evento="mover")]))
    m.adicionar(Estado("andando", pai="vivo", inicial="devagar", **reg("andando"),
                       transicoes=[Transicao("parado", evento="parar")]))
    m.adicionar(Estado("devagar", pai="andando", **reg("devagar"),
                       transicoes=[Transicao("correndo", evento="acelerar")]))
    m.adicionar(Estado("correndo", pai="andando", **reg("correndo"),
                       transicoes=[Transicao("devagar", condicao=lambda c: c["cansaco"] > 5)]))
    m.adicionar(Estado("morto", **reg("morto")))
    return m


class TestHFSM(unittest.TestCase):
    def test_iniciar_entra_do_pai_ao_filho(self):
        log = []
        m = montar(log)
        m.iniciar("vivo")
        self.assertEqual(log, ["+vivo", "+parado"])
        self.assertEqual(m.caminho(), ["vivo", "parado"])

    def test_transicao_entre_irmaos_preserva_pai(self):
        log = []
        m = montar(log)
        m.iniciar("vivo")
        log.clear()
        self.assertTrue(m.enviar("mover"))
        self.assertEqual(log, ["-parado", "+andando", "+devagar"])
        self.assertEqual(m.atual, "devagar")

    def test_evento_herdado_do_pai(self):
        log = []
        m = montar(log)
        m.iniciar("vivo")
        m.enviar("mover")
        log.clear()
        m.enviar("morrer")  # definido em "vivo", ativo em "devagar"
        self.assertEqual(log, ["-devagar", "-andando", "-vivo", "+morto"])
        self.assertEqual(m.caminho(), ["morto"])

    def test_filho_tem_precedencia(self):
        m = montar([])
        m.adicionar(Estado("zumbi", pai="vivo", transicoes=[Transicao("morto", evento="mover")]))
        m.iniciar("zumbi")
        m.enviar("mover")
        self.assertEqual(m.atual, "morto")

    def test_condicao_em_atualizar(self):
        log = []
        m = montar(log)
        ctx = {"cansaco": 0}
        m.iniciar("vivo", ctx)
        m.enviar("mover", ctx)
        m.enviar("acelerar", ctx)
        self.assertEqual(m.atual, "correndo")
        m.atualizar(ctx)
        self.assertEqual(m.atual, "correndo")
        ctx["cansaco"] = 9
        m.atualizar(ctx)
        self.assertEqual(m.atual, "devagar")

    def test_atualizar_pai_antes_do_filho(self):
        ordem = []
        m = HFSM()
        m.adicionar(Estado("a", inicial="b", ao_atualizar=lambda c, dt: ordem.append(("a", dt))))
        m.adicionar(Estado("b", pai="a", ao_atualizar=lambda c, dt: ordem.append(("b", dt))))
        m.iniciar("a")
        m.atualizar(None, 0.5)
        self.assertEqual(ordem, [("a", 0.5), ("b", 0.5)])

    def test_transicao_para_irmao_do_pai_sai_da_subarvore(self):
        log = []
        m = montar(log)
        m.iniciar("vivo")
        m.enviar("mover")
        log.clear()
        m.enviar("parar")  # andando -> parado (irmão): sai de andando/devagar
        self.assertEqual(log, ["-devagar", "-andando", "+parado"])

    def test_evento_sem_transicao_e_erros(self):
        m = montar([])
        with self.assertRaises(RuntimeError):
            m.enviar("x")
        m.iniciar("vivo")
        self.assertFalse(m.enviar("inexistente"))
        self.assertTrue(m.esta_em("vivo"))
        with self.assertRaises(ValueError):
            m.adicionar(Estado("vivo"))
        with self.assertRaises(ValueError):
            m.adicionar(Estado("x", pai="fantasma"))
        with self.assertRaises(KeyError):
            m.iniciar("nada")


if __name__ == "__main__":
    unittest.main()
