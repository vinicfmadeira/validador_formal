"""
regular.py — Reconhecedor de Linguagem Regular (Nível LR)
=========================================================
Tema 1: Validador de CPF no formato textual  ddd.ddd.ddd-dd
         (apenas formato; dígitos verificadores NÃO são checados)

Modelo computacional: DFA (Autômato Finito Determinístico)
Definição formal   : D = (Q, Sigma, delta, q0, F)

Fundamentação teórica — Aula 3 (Prof. Jairo):
  • DFA é uma 5-tupla D = (Q, Σ, δ, q0, F)
  • δ : Q × Σ → Q   (função de transição total)
  • Aceitação: δ̂(q0, w) ∈ F
  • Um passo = uma aplicação de δ sobre um símbolo da entrada

Linguagem:
  L = { w ∈ Σ* | w corresponde ao padrão  d d d . d d d . d d d - d d }
  onde d ∈ {0,1,...,9}  e  Σ = {0-9, '.', '-'}

Exemplos aceitos  : 123.456.789-00   000.000.000-00   999.999.999-99
Exemplos rejeitados: 12.34.56-78      123.456.789-0    abc.def.ghi-jk
"""

import sys

# ---------------------------------------------------------------------------
# 1. DEFINIÇÃO FORMAL DO DFA  D = (Q, Sigma, delta, q0, F)
# ---------------------------------------------------------------------------

# Conjunto de estados Q
# Cada estado representa quantos caracteres do padrão já foram consumidos.
# Estado 'qERR' é o estado de rejeição (poço/dead state).
# O padrão tem 14 caracteres: d d d . d d d . d d d - d d
#   pos:                       0 1 2 3 4 5 6 7 8 9 10 11 12 13
# q0..q13 = lendo posição 0..13; q14 = cadeia completamente aceita.

Q = {f'q{i}' for i in range(15)} | {'qERR'}

# Alfabeto de entrada Σ
SIGMA = set('0123456789.-')

# Estado inicial
q0 = 'q0'

# Conjunto de estados finais F
F = {'q14'}

# Função de transição δ : Q × Σ → Q
# Construída explicitamente como dicionário de dados estruturados.
# Posições esperadas do padrão  d d d . d d d . d d d - d d
#                                0 1 2 3 4 5 6 7 8 9 10 11 12 13
DIGITOS = set('0123456789')

def _construir_delta():
    """Constrói a tabela de transição δ como dicionário."""
    delta = {}

    # Posições que esperam um dígito: 0,1,2, 4,5,6, 8,9,10, 12,13
    posicoes_digito = [0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13]
    # Posições que esperam '.'  : 3, 7
    posicoes_ponto  = [3, 7]
    # Posição que espera '-'    : 11
    posicoes_hifen  = [11]

    for pos in posicoes_digito:
        estado_atual  = f'q{pos}'
        proximo_estado = f'q{pos + 1}'
        for c in DIGITOS:
            delta[(estado_atual, c)] = proximo_estado
        # qualquer outro símbolo → qERR
        for c in SIGMA - DIGITOS:
            delta[(estado_atual, c)] = 'qERR'

    for pos in posicoes_ponto:
        estado_atual   = f'q{pos}'
        proximo_estado = f'q{pos + 1}'
        delta[(estado_atual, '.')] = proximo_estado
        for c in SIGMA - {'.'}:
            delta[(estado_atual, c)] = 'qERR'

    for pos in posicoes_hifen:
        estado_atual   = f'q{pos}'
        proximo_estado = f'q{pos + 1}'
        delta[(estado_atual, '-')] = proximo_estado
        for c in SIGMA - {'-'}:
            delta[(estado_atual, c)] = 'qERR'

    # Estado final q14: qualquer símbolo adicional → qERR
    for c in SIGMA:
        delta[('q14', c)] = 'qERR'

    # qERR absorve tudo (estado poço)
    for c in SIGMA:
        delta[('qERR', c)] = 'qERR'

    return delta

delta = _construir_delta()

# ---------------------------------------------------------------------------
# 2. SIMULADOR DO DFA — aplica δ símbolo a símbolo
# ---------------------------------------------------------------------------

def reconhecer(entrada: str) -> dict:
    """
    Simula o DFA sobre a cadeia `entrada`.

    Retorna um dicionário com:
      - 'aceita' : bool
      - 'passos' : int  (número de aplicações de δ)
      - 'trace'  : list de tuplas (estado_antes, simbolo, estado_depois)
      - 'estado_final': str
    """
    estado_atual = q0
    passos = 0
    trace = []

    for simbolo in entrada:
        # Símbolo fora do alfabeto → rejeita imediatamente
        if simbolo not in SIGMA:
            estado_depois = 'qERR'
            trace.append((estado_atual, simbolo, estado_depois))
            passos += 1          # conta a transição para qERR
            estado_atual = 'qERR'
            break

        # Aplica δ(estado_atual, simbolo) — 1 passo formal
        estado_depois = delta.get((estado_atual, simbolo), 'qERR')
        trace.append((estado_atual, simbolo, estado_depois))
        passos += 1
        estado_atual = estado_depois

    aceita = (estado_atual in F)

    return {
        'aceita'      : aceita,
        'passos'      : passos,
        'trace'       : trace,
        'estado_final': estado_atual,
    }

# ---------------------------------------------------------------------------
# 3. EXECUÇÃO PASSO A PASSO (saída detalhada)
# ---------------------------------------------------------------------------

def exibir_execucao(entrada: str):
    """Imprime a execução passo a passo de uma cadeia."""
    resultado = reconhecer(entrada)
    print(f"\n{'='*60}")
    print(f"DFA — CPF  |  Entrada: '{entrada}'")
    print(f"{'='*60}")
    print(f"{'Passo':<6} {'Estado Antes':<14} {'Símbolo':<9} {'Estado Depois'}")
    print(f"{'-'*50}")
    for i, (qa, s, qd) in enumerate(resultado['trace'], start=1):
        print(f"{i:<6} {qa:<14} {repr(s):<9} {qd}")
    print(f"{'-'*50}")
    print(f"Estado final  : {resultado['estado_final']}")
    print(f"Passos totais : {resultado['passos']}")
    print(f"Resultado     : {'ACEITA ✓' if resultado['aceita'] else 'REJEITA ✗'}")

# ---------------------------------------------------------------------------
# 4. PONTO DE ENTRADA AUTÔNOMO
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/regular.py \"<cadeia>\"")
        print("Exemplo: python src/regular.py \"123.456.789-00\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
