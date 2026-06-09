"""
livre_contexto.py — Reconhecedor de Linguagem Livre de Contexto (Nível LLC)
============================================================================
Tema 1: Verificador de parênteses e colchetes balanceados em expressão simbólica.

Modelo computacional: PDA (Autômato com Pilha — Pushdown Automaton)
Definição formal   : P = (Q, Sigma, Gamma, delta, q0, Z0, F)

Fundamentação teórica — Aula 6 (Prof. Jairo):
  • PDA é uma 7-tupla P = (Q, Σ, Γ, δ, q0, Z0, F)
  • δ : Q × (Σ ∪ {ε}) × Γ → P(Q × Γ*)
  • Notação de transição: a, X/α  (lê a, desempilha X, empilha α)
  • Descrição Instantânea (ID): (q, w, γ)
  • Passo ⊢P : (q, aw, Xβ) ⊢P (p, w, αβ)  se (p, α) ∈ δ(q, a, X)
  • Aceitação por estado final: L(P) = {w | (q0,w,Z0) ⊢* (q,ε,α), q ∈ F}
  • Um passo = uma aplicação da função de transição δ

Linguagem:
  L = { w ∈ {(,),[,]}* | w tem delimitadores balanceados }
  Σ = {(, ), [, ]}   Γ = {Z0, PAREN, COLCH}

Representação da pilha: lista Python de tokens string.
  Topo = último elemento da lista (índice -1).
  A transição a, X/α empilha os tokens de α da DIREITA para ESQUERDA
  (convenção HMU: primeiro token de α fica no topo após o push).

Exemplos aceitos  : ((x+y)*z)   [a+b]   ([]())   ε (vazia)
Exemplos rejeitados: ((a+b)      )(      ([)]
"""

import sys

# ---------------------------------------------------------------------------
# 1. DEFINIÇÃO FORMAL DO PDA  P = (Q, Sigma, Gamma, delta, q0, Z0, F)
# ---------------------------------------------------------------------------

Q     = {'q0', 'qACEIT', 'qERR'}
SIGMA = {'(', ')', '[', ']'}
GAMMA = {'Z0', 'PAREN', 'COLCH'}
Z0    = 'Z0'
q0    = 'q0'
F     = {'qACEIT'}

# Caracteres de expressão que o PDA ignora (não pertencem a Σ)
IGNORADOS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789 +-*/=_,;:<>!@#$%^&|~`"\'\\?.'
)

# ---------------------------------------------------------------------------
# Função de transição δ declarada como dicionário de dados estruturados.
#
# Chave  : (estado, simbolo_entrada, topo_pilha)
#           simbolo_entrada pode ser um char de SIGMA
# Valor  : lista de pares (novo_estado, lista_tokens_a_empilhar)
#           lista_tokens_a_empilhar: tokens em ordem de topo→fundo a serem
#           colocados na pilha APÓS desempilhar o topo atual.
#           Ex: ['PAREN', 'Z0'] → PAREN no topo, Z0 embaixo.
#
# Semântica de uma transição  a, X / [t1, t2, ...]:
#   1. Lê a da entrada
#   2. Desempilha X (o topo)
#   3. Empilha t1, t2, ... (t1 fica no topo)
#
# Transições:
#   (q0, '(', X)     → (q0, [PAREN, X])  para qualquer X ∈ Γ
#   (q0, '[', X)     → (q0, [COLCH, X])
#   (q0, ')', PAREN) → (q0, [])          ← pop PAREN: match
#   (q0, ')', COLCH) → (qERR, [COLCH])   ← mismatch
#   (q0, ')', Z0)    → (qERR, [Z0])      ← underflow
#   (q0, ']', COLCH) → (q0, [])          ← pop COLCH: match
#   (q0, ']', PAREN) → (qERR, [PAREN])   ← mismatch
#   (q0, ']', Z0)    → (qERR, [Z0])      ← underflow
# ---------------------------------------------------------------------------

def _construir_delta():
    delta = {}

    # Abrir parêntese: empilha PAREN sobre qualquer topo
    for topo in GAMMA:
        delta[('q0', '(', topo)] = [('q0', ['PAREN', topo])]

    # Abrir colchete: empilha COLCH sobre qualquer topo
    for topo in GAMMA:
        delta[('q0', '[', topo)] = [('q0', ['COLCH', topo])]

    # Fechar parêntese ')' — só casa com PAREN no topo
    delta[('q0', ')', 'PAREN')] = [('q0',   [])]           # match: pop
    delta[('q0', ')', 'COLCH')] = [('qERR', ['COLCH'])]    # mismatch
    delta[('q0', ')', 'Z0')]    = [('qERR', ['Z0'])]        # underflow

    # Fechar colchete ']' — só casa com COLCH no topo
    delta[('q0', ']', 'COLCH')] = [('q0',   [])]           # match: pop
    delta[('q0', ']', 'PAREN')] = [('qERR', ['PAREN'])]    # mismatch
    delta[('q0', ']', 'Z0')]    = [('qERR', ['Z0'])]        # underflow

    # qERR absorve qualquer coisa
    for s in SIGMA:
        for topo in GAMMA:
            delta[('qERR', s, topo)] = [('qERR', [topo])]

    return delta

delta = _construir_delta()

# ---------------------------------------------------------------------------
# 2. SIMULADOR DO PDA — pilha como lista de tokens
# ---------------------------------------------------------------------------

def reconhecer(entrada: str) -> dict:
    """
    Simula o PDA sobre a cadeia `entrada`.

    Retorna dicionário com:
      - 'aceita' : bool
      - 'passos' : int  (cada transição ⊢P = 1 passo formal)
      - 'trace'  : lista de registros de passo
      - 'estado_final': str
    """
    estado = q0
    pilha  = [Z0]       # fundo da pilha = Z0
    passos = 0
    trace  = []

    for simbolo in entrada:
        # Ignora caracteres de expressão (não são do Σ do PDA)
        if simbolo in IGNORADOS:
            continue

        if simbolo not in SIGMA:
            estado = 'qERR'
            trace.append({
                'passo'    : passos + 1,
                'estado'   : estado,
                'simbolo'  : simbolo,
                'topo'     : pilha[-1] if pilha else '∅',
                'acao'     : 'símbolo fora do alfabeto Σ → qERR',
                'pilha_pos': list(pilha),
            })
            passos += 1
            break

        topo  = pilha[-1] if pilha else 'Z0'
        chave = (estado, simbolo, topo)
        transicoes = delta.get(chave)

        id_pilha = list(pilha)

        if transicoes is None:
            estado = 'qERR'
            trace.append({
                'passo'    : passos + 1,
                'estado'   : estado,
                'simbolo'  : simbolo,
                'topo'     : topo,
                'acao'     : f'sem transição para ({estado},{repr(simbolo)},{topo})',
                'pilha_pos': id_pilha,
            })
            passos += 1
            break

        # Pega a primeira transição (PDA determinístico aqui)
        novo_estado, empilhar = transicoes[0]

        acao = (
            f"δ(q={estado}, a={repr(simbolo)}, X={topo}) → "
            f"(q'={novo_estado}, empilha={empilhar if empilhar else ['ε']})"
        )

        # Executa: desempilha topo; empilha tokens de 'empilhar' (topo primeiro)
        pilha.pop()
        for tok in reversed(empilhar):   # reversed: o primeiro token fica no topo
            pilha.append(tok)

        trace.append({
            'passo'    : passos + 1,
            'estado'   : estado,
            'simbolo'  : simbolo,
            'topo'     : topo,
            'acao'     : acao,
            'pilha_pos': list(pilha),
        })
        passos += 1
        estado = novo_estado

        if estado == 'qERR':
            break

    # Transição ε: se chegamos ao fim da entrada em q0 com pilha = [Z0] → aceita
    if estado == 'q0' and pilha == [Z0]:
        trace.append({
            'passo'    : passos + 1,
            'estado'   : 'qACEIT',
            'simbolo'  : 'ε',
            'topo'     : 'Z0',
            'acao'     : 'entrada esgotada, pilha=[Z0], q0 → qACEIT',
            'pilha_pos': [Z0],
        })
        passos += 1
        estado = 'qACEIT'

    aceita = (estado in F)

    return {
        'aceita'      : aceita,
        'passos'      : passos,
        'trace'       : trace,
        'estado_final': estado,
        'pilha_final' : pilha,
    }

# ---------------------------------------------------------------------------
# 3. EXECUÇÃO PASSO A PASSO (saída detalhada)
# ---------------------------------------------------------------------------

def exibir_execucao(entrada: str):
    resultado = reconhecer(entrada)
    print(f"\n{'='*72}")
    print(f"PDA — Balanceamento  |  Entrada: '{entrada}'")
    print(f"{'='*72}")
    print(f"{'Passo':<6} {'Estado':<10} {'Símbolo':<9} {'Ação'}")
    print(f"{'-'*72}")
    for t in resultado['trace']:
        print(f"{t['passo']:<6} {t['estado']:<10} {repr(t['simbolo']):<9} {t['acao']}")
    print(f"{'-'*72}")
    print(f"Estado final  : {resultado['estado_final']}")
    print(f"Pilha final   : {resultado['pilha_final']}")
    print(f"Passos totais : {resultado['passos']}")
    print(f"Resultado     : {'ACEITA ✓' if resultado['aceita'] else 'REJEITA ✗'}")

# ---------------------------------------------------------------------------
# 4. PONTO DE ENTRADA AUTÔNOMO
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/livre_contexto.py \"<expressão>\"")
        print("Exemplo: python src/livre_contexto.py \"((x+y)*z)\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
