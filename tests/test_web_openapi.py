import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_openapi import documentar, gerar_openapi
from web_roteador import Roteador


class TestWebOpenapi(unittest.TestCase):
    def setUp(self):
        self.r = Roteador()

        @self.r.rota("/usuarios/<int:id>", ("GET", "DELETE"))
        @documentar("Busca usuário", tags=("usuarios",),
                    query={"campos": {"descricao": "campos extras"}},
                    respostas={200: {"descricao": "ok", "schema": {"type": "object"}}, 404: "não achou"})
        def usuario(req, id):
            """Retorna um usuário."""

        @self.r.rota("/usuarios", ("POST",))
        @documentar(corpo={"type": "object", "properties": {"nome": {"type": "string"}}}, deprecated=True)
        def criar(req):
            pass

        @self.r.rota("/sem-doc")
        def simples(req):
            pass

    def test_estrutura(self):
        d = gerar_openapi(self.r, "API", "1.0", servidores=("http://x",))
        self.assertEqual(d["openapi"], "3.0.3")
        self.assertEqual(d["info"], {"title": "API", "version": "1.0"})
        self.assertEqual(d["servers"], [{"url": "http://x"}])
        self.assertEqual(set(d["paths"]), {"/usuarios/{id}", "/usuarios", "/sem-doc"})
        json.dumps(d)  # serializável

    def test_parametros_de_caminho_e_query(self):
        op = gerar_openapi(self.r, "A", "1")["paths"]["/usuarios/{id}"]["get"]
        self.assertEqual(op["parameters"][0],
                         {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}})
        self.assertEqual(op["parameters"][1]["name"], "campos")
        self.assertFalse(op["parameters"][1]["required"])
        self.assertEqual(op["summary"], "Busca usuário")
        self.assertEqual(op["description"], "Retorna um usuário.")
        self.assertEqual(op["tags"], ["usuarios"])

    def test_respostas(self):
        op = gerar_openapi(self.r, "A", "1")["paths"]["/usuarios/{id}"]["delete"]
        self.assertEqual(op["responses"]["404"], {"description": "não achou"})
        self.assertEqual(op["responses"]["200"]["content"]["application/json"]["schema"],
                         {"type": "object"})
        self.assertEqual(op["operationId"], "usuario_delete")

    def test_corpo_e_deprecated(self):
        op = gerar_openapi(self.r, "A", "1")["paths"]["/usuarios"]["post"]
        self.assertTrue(op["deprecated"])
        self.assertEqual(op["requestBody"]["content"]["application/json"]["schema"]["type"], "object")

    def test_rota_sem_doc_tem_padrao(self):
        op = gerar_openapi(self.r, "A", "1")["paths"]["/sem-doc"]["get"]
        self.assertEqual(op["responses"], {"200": {"description": "Sucesso"}})
        self.assertNotIn("parameters", op)

    def test_decorador_preserva_funcao(self):
        self.assertEqual(self.r.rotas[0].manipulador.__name__, "usuario")

    def test_erros(self):
        with self.assertRaises(ValueError):
            gerar_openapi(self.r, "", "1")
        self.r.adicionar("/sem-doc", lambda req: None, nome="dup")
        with self.assertRaises(ValueError):
            gerar_openapi(self.r, "A", "1")


if __name__ == "__main__":
    unittest.main()
