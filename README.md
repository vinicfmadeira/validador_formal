# Validador Formal em Três Níveis

**Disciplina:** Modelagem Computacional  
**Professor:** Dr. José Jairo de S. e Silva — Universidade Positivo  
**Tema:** Validador de cadastro, fórmulas e integridade (Tema 1)

---

## Descrição

Sistema de validação formal com três reconhecedores, um para cada nível da Hierarquia de Chomsky:

| Nível | Linguagem | Modelo | Problema |
|-------|-----------|--------|----------|
| LR    | Regular   | DFA    | CPF no formato `ddd.ddd.ddd-dd` |
| LLC   | Livre de Contexto | PDA | Parênteses e colchetes balanceados |
| R     | Recursiva | MT     | Cópia de cadeia `L = {w#w \| w ∈ {0,1}*}` |

---

## Estrutura

```
projeto/
├── README.md
├── requirements.txt
├── src/
│   ├── regular.py           # Reconhecedor LR (DFA — CPF)
│   ├── livre_contexto.py    # Reconhecedor LLC (PDA — balanceamento)
│   ├── recursiva.py         # Reconhecedor R (MT — w#w)
│   ├── testes.py            # Bateria integrada de testes
│   ├── gerar_diagramas.py   # Gera diagramas .png/.dot
│   └── gerar_relatorio.py   # Gera relatorio.pdf
├── testes/
│   ├── testes_regular.txt
│   ├── testes_livre_contexto.txt
│   └── testes_recursiva.txt
├── diagramas/
│   ├── dfa_regular.png
│   ├── pda_livre_contexto.png
│   └── mt_recursiva.png
└── relatorio/
    └── relatorio.pdf
```

---

## Instalação

```bash
pip install -r requirements.txt
# Para os diagramas, instalar também o Graphviz no sistema:
# Ubuntu/Debian: sudo apt-get install graphviz
# macOS:         brew install graphviz
# Windows:       winget install graphviz
```

---

## Execução

### Bateria completa de testes (comando único)

```bash
python src/testes.py
```

### Execução individual de cada reconhecedor

```bash
# DFA — CPF
python src/regular.py "123.456.789-00"

# PDA — Balanceamento
python src/livre_contexto.py "((x+y)*z)"

# MT — w#w
python src/recursiva.py "101#101"
```

### Gerar diagramas e relatório

```bash
python src/gerar_diagramas.py
python src/gerar_relatorio.py
```

---

## Exemplos de saída

```
DFA — CPF | Entrada: '123.456.789-00'
Passo  Estado Antes   Símbolo   Estado Depois
1      q0             '1'       q1
...
14     q13            '0'       q14
Passos totais : 14
Resultado     : ACEITA ✓
```

---

## Fundamentos Teóricos

- **DFA** — Aula 3 (5-tupla `D = (Q, Σ, δ, q0, F)`, tabela de transição)
- **PDA** — Aula 6 (7-tupla `P = (Q, Σ, Γ, δ, q0, Z0, F)`, IDs, critério por estado final)
- **MT**  — Aula 7 (7-tupla `M = (Q, Σ, Γ, δ, q0, B, F)`, marcação cruzada para `w#w`)
