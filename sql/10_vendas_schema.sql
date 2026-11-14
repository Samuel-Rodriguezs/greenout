-- Schema de vendas: clientes, produtos, pedidos e itens_pedido
CREATE TABLE clientes (
    id        INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL,
    cidade    TEXT,
    criado_em TEXT NOT NULL
);

CREATE TABLE produtos (
    id        INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco     REAL NOT NULL
);

CREATE TABLE pedidos (
    id         INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    data       TEXT NOT NULL,
    status     TEXT NOT NULL
);

CREATE TABLE itens_pedido (
    id             INTEGER PRIMARY KEY,
    pedido_id      INTEGER NOT NULL REFERENCES pedidos(id),
    produto_id     INTEGER NOT NULL REFERENCES produtos(id),
    quantidade     INTEGER NOT NULL,
    preco_unitario REAL NOT NULL
);

INSERT INTO clientes (id, nome, cidade, criado_em) VALUES
    (1, 'Ana',    'São Paulo',      '2024-11-10'),
    (2, 'Bruno',  'Rio de Janeiro', '2024-12-05'),
    (3, 'Carla',  'São Paulo',      '2025-01-20'),
    (4, 'Davi',   NULL,             '2025-02-14'),
    (5, 'Eva',    'Curitiba',       '2025-03-01'),
    (6, 'Filipe', 'Rio de Janeiro', '2025-03-15');

INSERT INTO produtos (id, nome, categoria, preco) VALUES
    (1, 'Notebook', 'Informática', 3000),
    (2, 'Mouse',    'Informática', 50),
    (3, 'Teclado',  'Informática', 150),
    (4, 'Cadeira',  'Móveis',      800),
    (5, 'Mesa',     'Móveis',      600),
    (6, 'Caneta',   'Papelaria',   5),
    (7, 'Agenda',   'Papelaria',   30);

INSERT INTO pedidos (id, cliente_id, data, status) VALUES
    (1,  1, '2025-01-05', 'entregue'),
    (2,  1, '2025-02-10', 'entregue'),
    (3,  2, '2025-02-15', 'entregue'),
    (4,  3, '2025-02-20', 'cancelado'),
    (5,  3, '2025-03-03', 'entregue'),
    (6,  1, '2025-03-12', 'pendente'),
    (7,  2, '2025-03-18', 'entregue'),
    (8,  5, '2025-04-02', 'entregue'),
    (9,  2, '2025-04-10', 'pendente'),
    (10, 5, '2025-04-25', 'entregue');

INSERT INTO itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario) VALUES
    (1,  1,  1, 1,  3000),
    (2,  1,  2, 2,  50),
    (3,  2,  3, 1,  150),
    (4,  2,  6, 10, 5),
    (5,  3,  4, 2,  800),
    (6,  4,  5, 1,  600),
    (7,  5,  2, 3,  50),
    (8,  5,  7, 2,  30),
    (9,  6,  1, 1,  3000),
    (10, 7,  5, 1,  600),
    (11, 7,  6, 20, 5),
    (12, 8,  3, 2,  150),
    (13, 8,  2, 1,  50),
    (14, 9,  4, 1,  800),
    (15, 10, 7, 5,  30);
