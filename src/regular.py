"""
regular.py - DFA para CPF no formato ddd.ddd.ddd-dd
So valida o formato; digitos verificadores nao sao checados.

D = (Q, Sigma, delta, q0, F)
  Q = {q0..q14, qERR},  F = {q14}
  Cada estado qi = consumiu i chars do padrao
  Padrao: d d d . d d d . d d d - d d  (14 chars)
"""

#esse arquivo é para implementar um DFA que reconhece CPFs no formato ddd.ddd.ddd-dd, onde d é de 0 a 9. O DFA 
#deve validar apenas o formato, sem verificar os dígitos verificadores.

#D = (q, sigma, delta, q0, f)
#Q = {q0..q14, qERR} - f = {q14}
#Cada estado qi representa que já foram consumidos i caracteres do padrão, são 14 chars no cpf


import sys

# q0 ate q14 rastreiam posicao no padrao; qERR e o estado de rejeicao
Q = {f'q{i}' for i in range(15)} | {'qERR'}

SIGMA = set('0123456789.-')
q0 = 'q0'
F = {'q14'}

DIGITOS = set('0123456789')

def _construir_delta():
    delta = {}

    posicoes_digito = [0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13]
    posicoes_ponto  = [3, 7]
    posicoes_hifen  = [11]

    for pos in posicoes_digito:
        estado_atual  = f'q{pos}'
        proximo_estado = f'q{pos + 1}'
        for c in DIGITOS:
            delta[(estado_atual, c)] = proximo_estado
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

    # qualquer entrada apos q14 e erro (a cadeia esta maior que o padrao)
    for c in SIGMA:
        delta[('q14', c)] = 'qERR'

    # estado poco - vai absorve tudo
    for c in SIGMA:
        delta[('qERR', c)] = 'qERR'

    return delta

delta = _construir_delta()


def reconhecer(entrada: str) -> dict:
    "Roda o DFA e devolve aceita/passos/trace/estado_final."
    estado_atual = q0
    passos = 0
    trace = []

    for simbolo in entrada:
        if simbolo not in SIGMA:
            estado_depois = 'qERR'
            trace.append((estado_atual, simbolo, estado_depois))
            passos += 1
            estado_atual = 'qERR'
            break

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


def exibir_execucao(entrada: str):
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/regular.py \"<cadeia>\"")
        print("Exemplo: python src/regular.py \"123.456.789-00\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
