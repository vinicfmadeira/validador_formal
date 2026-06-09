#esse arquivo vai implementa um PDA para verificar balanceamento de () e [] em expressoes, ignorando outros caracteres"
#p = (q, sigma, gamme, delta, q0, z0, f)"
#sigma = {(, ), [, ]}, gamma = {Z0, PAREN, COLCH}, "
#f = {qACEIT}"
#pilha: lista python - topo = indice -1"

import sys

Q     = {'q0', 'qACEIT', 'qERR'}
SIGMA = {'(', ')', '[', ']'}
GAMMA = {'Z0', 'PAREN', 'COLCH'}
Z0    = 'Z0'
q0    = 'q0'
F     = {'qACEIT'}

# caracteres que o PDA vai ignora
IGNORADOS = set(
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789 +-*/=_,;:<>!@#$%^&|~`"\'\\?.'
)

# delta(estado, simbolo, topo) - [(novo_estado, tokens_a_empilhar)]
#depois ele vai desempilhar o topo, e empilhar os tokens (obs: o primeira da lista é o topo da pilha)
def _construir_delta():
    delta = {}

    # abertura:
    for topo in GAMMA:
        delta[('q0', '(', topo)] = [('q0', ['PAREN', topo])]
    for topo in GAMMA:
        delta[('q0', '[', topo)] = [('q0', ['COLCH', topo])]

    # fechar ')'
    delta[('q0', ')', 'PAREN')] = [('q0',   [])]           # match
    delta[('q0', ')', 'COLCH')] = [('qERR', ['COLCH'])]    # mismatch
    delta[('q0', ')', 'Z0')]    = [('qERR', ['Z0'])]        # pilha vazia

    # fechar ']'
    delta[('q0', ']', 'COLCH')] = [('q0',   [])]           # match
    delta[('q0', ']', 'PAREN')] = [('qERR', ['PAREN'])]    # mismatch
    delta[('q0', ']', 'Z0')]    = [('qERR', ['Z0'])]        # pilha vazia

    # qERR ira absorver as entrada
    for s in SIGMA:
        for topo in GAMMA:
            delta[('qERR', s, topo)] = [('qERR', [topo])]

    return delta

delta = _construir_delta()


def reconhecer(entrada: str) -> dict:
    """Roda o PDA e devolve aceita/passos/trace/estado_final/pilha_final."""
    estado = q0
    pilha  = [Z0]
    passos = 0
    trace  = []

    for simbolo in entrada:
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

        novo_estado, empilhar = transicoes[0]

        acao = (
            f"δ(q={estado}, a={repr(simbolo)}, X={topo}) → "
            f"(q'={novo_estado}, empilha={empilhar if empilhar else ['ε']})"
        )

        pilha.pop()
        for tok in reversed(empilhar):
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

    # transicao epsilon: entrada esgotada com pilha igual [Z0] ira aceita
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


def exibir_execucao(entrada: str):
    resultado = reconhecer(entrada)
    print(f"\n{'='*72}")
    print(f"PDA — Balanceamento  /  Entrada: '{entrada}'")
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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/livre_contexto.py \"<expressão>\"")
        print("Exemplo: python src/livre_contexto.py \"((x+y)*z)\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
