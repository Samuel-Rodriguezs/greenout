# Fila de temas da rotina diária

Cada linha é uma frente de ~20 commits (um por exercício, com testes). A rotina
diária pega as **5 primeiras linhas não marcadas** (`[ ]`), executa e marca `[x]`
no mesmo PR. Se a fila acabar ou algum teste falhar, a rotina para e avisa.

Regras de qualidade (valem para todas as frentes):

- um commit por exercício, só com os arquivos dele;
- testes passando antes de cada commit (`python -m unittest discover -s tests`,
  `node --test`, `go test`, `make test`, conforme a pasta);
- nada de código repetido: conferir `ls` da pasta antes e não repetir nomes;
- nada de placeholders, nada de commits vazios, nada de datas alteradas.

Formato: `- [ ] pasta/prefixo — descrição`

## Python (`python/` + `tests/`)

- [x] python/bio_ — bioinformática: DNA/RNA, tradução de códons, conteúdo GC, complemento reverso, Needleman-Wunsch, Smith-Waterman, distância de Hamming, motivos, FASTA parser
- [x] python/geo_ — geometria computacional: área de polígono, ponto em polígono, convex hull, interseção de segmentos, par de pontos mais próximo, triangulação simples, distância haversine
- [x] python/fin_ — mercado financeiro: SMA, EMA, RSI, MACD, Bollinger, drawdown, Sharpe, volatilidade, retorno acumulado, backtest simples de cruzamento de médias
- [x] python/img_ — processamento de imagem em matrizes: convolução, blur, Sobel, histograma, equalização, limiar de Otsu, rotação, redimensionamento, PGM/PPM parser
- [x] python/sig_ — sinais: FFT, DFT inversa, filtros FIR/IIR, janelas, geração de ondas, detecção de picos, correlação, média móvel, codificação Manchester
- [x] python/ecs_ — motor de jogo: ECS, colisão AABB e círculos, quadtree, física de partículas, máquina de estados de IA, pathfinding em grade, câmera, tilemap
- [x] python/bd_ — mini banco de dados: B-tree, WAL, índices hash, parser SQL, planner simples, transações com MVCC simplificado, LSM-tree simplificada
- [x] python/rede_ — redes: CIDR e subnetting, parser de IP/MAC, checksums, máquina de estados TCP, DNS parser, ARP simulado, roteamento por prefixo mais longo
- [x] python/so_ — sistemas operacionais: escalonadores (FCFS, SJF, RR, prioridade), paginação (FIFO, LRU, Clock), alocador buddy, semáforos simulados, deadlock detection
- [x] python/comp_ — compiladores: lexer, parser descendente, AST, constant folding, análise de escopo, geração de código para a VM, pretty printer, verificador de tipos simples
- [x] python/tipos_ — sistemas de tipos: unificação, Hindley-Milner mínimo, cálculo lambda (redução, Church), combinadores SKI, tipos algébricos, pattern matching
- [x] python/fp_ — programação funcional: monads (Maybe, Either, Writer, State), lenses, transducers, memoização, composição, currying, streams preguiçosos
- [x] python/gen_ — geradores de dados fictícios com seed: nomes, endereços, CPF/CNPJ válidos, e-mails, lorem, séries temporais, grafos aleatórios
- [x] python/puz_ — puzzles: nonograma, quebra-cabeça de 15, kakuro, KenKen, torre de cubos, cavalo de Euler, labirinto de Hanói
- [ ] python/rel_ — relatórios: geradores de tabelas Markdown/HTML/CSV, gráficos ASCII de barras/linhas, templates, formatação numérica pt-BR, paginação de texto

## Go

- [x] go-bd/ — módulo novo: key-value com WAL, B-tree, LSM simplificado, índices, parser de comandos, snapshots
- [x] go-net/ — módulo novo: CIDR, parser de IP, DNS, protocolo binário próprio (encode/decode), codec com checksum, simulador de roteamento
- [x] go-comp/ — módulo novo: lexer, parser, AST, interpretador e VM de uma linguagem pequena

## JavaScript

- [x] js-geo/ — geometria e mapas: haversine, polígonos, hull, quadtree, projeção, geohash, rotas
- [x] js-img/ — imagem em matrizes: convolução, bordas, histogramas, dithering, paletas, redimensionamento
- [ ] js-fp/ — programação funcional: lenses, transducers, monads, parser combinators, Either/Maybe

## C

- [x] c-os/ — alocadores (buddy, slab), escalonadores, tabela de páginas, pilha de chamadas simulada
- [ ] c-net/ — parser de IP/CIDR, checksums, codificação TLV, máquina de estados de protocolo

## Outros

- [ ] lua-games/ — jogos de tabuleiro e cartas em Lua com testes
- [ ] shell-lib/ — utilitários POSIX sh (sem bash) com testes via Python
- [ ] sql/energia — energia: usinas, medições, consumo por faixa, picos, tarifa (SQLite)
- [ ] sql/esportes — esportes: campeonato, jogos, classificação, artilharia, sequências (SQLite)
- [ ] sql/clima — clima: estações, medições, médias móveis, anomalias, recordes (SQLite)
- [ ] sql/seguros — seguros: apólices, sinistros, prêmios, sinistralidade, renovações (SQLite)
- [ ] sql/rede_social — rede social: usuários, posts, seguidores, grafo de amizade com CTE recursiva (SQLite)
