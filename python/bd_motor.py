"""Motor SQL em memória: parser -> catálogo -> planejador -> operadores Volcano.

Integra bd_sql_parser, bd_catalogo, bd_planejador, bd_volcano, bd_joins, bd_agregacao e
bd_bmais (índices). Cada comando é atômico: se falhar, o estado anterior é mantido.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from bd_agregacao import Agrupamento
from bd_bmais import BMais
from bd_catalogo import Catalogo
from bd_joins import JuncaoHash, LoopAninhado
from bd_planejador import Plano, Planejador, ScanIndice, ScanSeq
from bd_serial_linhas import ErroSerializacaoLinha, codificar_linha
from bd_sql_parser import (Apagar, Atualizar, Coluna, CriarTabela, Inserir, Selecionar,
                           contem_agregado, parse)
from bd_volcano import (Distinto, ErroExecucao, Filtro, Limite, Ordenacao, Projecao, Scan,
                        avaliar)


@dataclass
class Resultado:
    colunas: list[str] = field(default_factory=list)
    linhas: list[tuple] = field(default_factory=list)
    afetadas: int = 0
    plano: Optional[Plano] = None


class MotorSQL:
    def __init__(self) -> None:
        self.catalogo = Catalogo()
        self.dados: dict[str, list[tuple]] = {}
        self.indices: dict[tuple[str, str], BMais] = {}

    # ---- infraestrutura ----
    def criar_indice(self, nome: str, tabela: str, coluna: str, unico: bool = False) -> None:
        t = self.catalogo.tabela(tabela)
        pos = t.posicao(coluna)
        if unico:
            vistos = [l[pos] for l in self.dados[t.nome] if l[pos] is not None]
            if len(vistos) != len(set(vistos)):
                raise ErroExecucao("não é possível criar índice único: há valores duplicados")
        self.catalogo.criar_indice(nome, tabela, coluna, unico)
        self._reindexar(t.nome)

    def _reindexar(self, nome: str) -> None:
        t = self.catalogo.tabela(nome)
        t.n_linhas = len(self.dados[nome])
        for ind in t.indices.values():
            arv = BMais(8)
            pos = t.posicao(ind.coluna)
            for i, linha in enumerate(self.dados[nome]):
                v = linha[pos]
                if v is None:
                    continue  # NULL não é indexado
                lst = arv.buscar(v)
                if lst is None:
                    arv.inserir(v, [i])
                else:
                    lst.append(i)
            self.indices[(nome, ind.coluna)] = arv

    def _validar_linha(self, nome: str, linha: list[Any]) -> tuple:
        t = self.catalogo.tabela(nome)
        coerced = [float(v) if c.tipo == "REAL" and isinstance(v, int) and not isinstance(v, bool) else v
                   for c, v in zip(t.colunas, linha)]
        try:
            codificar_linha(t.esquema(), coerced)  # checa tipos e limites
        except ErroSerializacaoLinha as e:
            raise ErroExecucao(str(e)) from e
        if t.chave_primaria and coerced[t.posicao(t.chave_primaria)] is None:
            raise ErroExecucao("chave primária não pode ser NULL")
        return tuple(coerced)

    def _checar_unicos(self, nome: str, linhas: list[tuple]) -> None:
        t = self.catalogo.tabela(nome)
        for ind in t.indices.values():
            if not ind.unico:
                continue
            pos = t.posicao(ind.coluna)
            vals = [l[pos] for l in linhas if l[pos] is not None]
            if len(vals) != len(set(vals)):
                raise ErroExecucao(f"violação de unicidade em {nome}.{ind.coluna}")

    # ---- execução ----
    def executar(self, sql: str) -> Resultado:
        cmd = parse(sql)
        if isinstance(cmd, CriarTabela):
            t = self.catalogo.criar_de_ast(cmd)
            self.dados[t.nome] = []
            self._reindexar(t.nome)
            return Resultado()
        if isinstance(cmd, Inserir):
            return self._inserir(cmd)
        if isinstance(cmd, Selecionar):
            return self._selecionar(cmd)
        if isinstance(cmd, Atualizar):
            return self._atualizar(cmd)
        if isinstance(cmd, Apagar):
            return self._apagar(cmd)
        raise ErroExecucao("comando não suportado")

    def _inserir(self, c: Inserir) -> Resultado:
        t = self.catalogo.tabela(c.tabela)
        nomes = [x.lower() for x in c.colunas] if c.colunas else [col.nome for col in t.colunas]
        if len(set(nomes)) != len(nomes):
            raise ErroExecucao("coluna repetida no INSERT")
        for n in nomes:
            t.posicao(n)
        novas = []
        for exprs in c.linhas:
            if len(exprs) != len(nomes):
                raise ErroExecucao("número de valores diferente do número de colunas")
            linha: list[Any] = [None] * len(t.colunas)
            for n, e in zip(nomes, exprs):
                linha[t.posicao(n)] = avaliar(e, [], ())
            novas.append(self._validar_linha(t.nome, linha))
        candidato = self.dados[t.nome] + novas
        self._checar_unicos(t.nome, candidato)
        self.dados[t.nome] = candidato
        self._reindexar(t.nome)
        return Resultado(afetadas=len(novas))

    def _esquema_tabela(self, nome: str, alias: Optional[str] = None) -> list[tuple[str, str]]:
        t = self.catalogo.tabela(nome)
        return [((alias or t.nome).lower(), c.nome) for c in t.colunas]

    def _atualizar(self, c: Atualizar) -> Resultado:
        t = self.catalogo.tabela(c.tabela)
        esq = self._esquema_tabela(t.nome)
        for col, _ in c.atribuicoes:
            t.posicao(col)
        novas, n = [], 0
        for linha in self.dados[t.nome]:
            if c.where is None or avaliar(c.where, esq, linha) is True:
                nova = list(linha)
                for col, e in c.atribuicoes:
                    nova[t.posicao(col)] = avaliar(e, esq, linha)  # valores lidos da linha antiga
                novas.append(self._validar_linha(t.nome, nova))
                n += 1
            else:
                novas.append(linha)
        self._checar_unicos(t.nome, novas)
        self.dados[t.nome] = novas
        self._reindexar(t.nome)
        return Resultado(afetadas=n)

    def _apagar(self, c: Apagar) -> Resultado:
        t = self.catalogo.tabela(c.tabela)
        esq = self._esquema_tabela(t.nome)
        mantidas = [l for l in self.dados[t.nome]
                    if not (c.where is None or avaliar(c.where, esq, l) is True)]
        n = len(self.dados[t.nome]) - len(mantidas)
        self.dados[t.nome] = mantidas
        self._reindexar(t.nome)
        return Resultado(afetadas=n)

    # ---- SELECT ----
    def _linhas_do_acesso(self, no: Any) -> list[tuple]:
        if isinstance(no, ScanSeq):
            return self.dados[no.tabela]
        arv = self.indices[(no.tabela, no.coluna)]
        saida = []
        for k, posicoes in arv.intervalo(no.lo, no.hi):
            if (not no.lo_incl and k == no.lo) or (not no.hi_incl and k == no.hi):
                continue
            saida.extend(self.dados[no.tabela][i] for i in posicoes)
        return saida

    def _operador(self, no: Any) -> Any:
        if isinstance(no, (ScanSeq, ScanIndice)):
            t = self.catalogo.tabela(no.tabela)
            return Scan(t.nome, [col.nome for col in t.colunas], self._linhas_do_acesso(no), no.alias)
        esq, dir_ = self._operador(no.esq), self._operador(no.dir)
        if no.algoritmo == "hash":
            return JuncaoHash(esq, dir_, no.chave_esq, no.chave_dir, "inner")
        return LoopAninhado(esq, dir_, no.condicao, "inner")

    def _selecionar(self, s: Selecionar) -> Resultado:
        plano = Planejador(self.catalogo).planejar(s)
        op = self._operador(plano.raiz)
        if s.where is not None:
            op = Filtro(op, s.where)
        itens, nomes = self._itens(s, op.esquema)
        agregando = bool(s.group_by) or s.having is not None or any(contem_agregado(e) for e, _ in itens)
        if agregando:
            op = Agrupamento(op, s.group_by, list(zip([e for e, _ in itens], nomes)), s.having)
            if s.order_by:
                op = Ordenacao(op, [(self._chave_ordem(e, itens, nomes), d) for e, d in s.order_by])
        else:
            if s.order_by:
                op = Ordenacao(op, [(self._chave_ordem(e, itens, nomes, True), d) for e, d in s.order_by])
            op = Projecao(op, list(zip([e for e, _ in itens], nomes)))
        if s.distinto:
            op = Distinto(op)
        if s.limite is not None:
            op = Limite(op, s.limite)
        return Resultado([n for n in nomes], op.todas(), plano=plano)

    def _itens(self, s: Selecionar, esquema: list[tuple[str, str]]) -> tuple[list[tuple[Any, Any]], list[str]]:
        itens: list[tuple[Any, Any]] = []
        nomes: list[str] = []
        for n, it in enumerate(s.itens):
            if it.expr is None:
                for tab, col in esquema:
                    itens.append((Coluna(col, tab), None))
                    nomes.append(col)
                continue
            itens.append((it.expr, None))
            if it.alias:
                nomes.append(it.alias.lower())
            elif isinstance(it.expr, Coluna):
                nomes.append(it.expr.nome.lower())
            else:
                nomes.append(f"col{n + 1}")
        return itens, nomes

    @staticmethod
    def _chave_ordem(expr: Any, itens: list[tuple[Any, Any]], nomes: list[str], antes_proj: bool = False) -> Any:
        """ORDER BY por alias ou por expressão idêntica a um item do SELECT.

        Antes da projeção (sem agregação) o alias é trocado pela expressão que ele nomeia;
        depois do agrupamento, a expressão é trocada pelo nome da coluna de saída."""
        if antes_proj:
            if isinstance(expr, Coluna) and expr.tabela is None:
                for (e, _), nome in zip(itens, nomes):
                    if nome == expr.nome.lower() and e != expr:
                        return e
            return expr
        for (e, _), nome in zip(itens, nomes):
            if e == expr:
                return Coluna(nome)
        return expr
