#esse arquivo vai implementa uma MT para decidir a linguagem L = { w#w | w ∈ {0,1}* }"
#mt = ( q , sigma, gamma, delta, q0, b, f)"
#sigma = {0, 1, #} e gamma = {sigma, X, Y, B}, b = B"

#Estados:"
#q0    busca digito nao-marcado (esquerda)"
#m0    marcou x; indo ate o '#'"
#m1    marcou y; indo ate o '#'"
#n0    cruzou '#' - procura '0' na direita"
#n1    cruzou '#' - procura '1' na direita"
#verifica que a direita esta toda marcada"
#ret   retornando pro inicio"
#qACEIT, qREJ  estados finais (decisor sempre vai chega em um deles)"


import sys

Q = {'q0', 'm0', 'm1', 'n0', 'n1', 'v', 'ret', 'qACEIT', 'qREJ'}
SIGMA = {'0', '1', '#'}
GAMMA = {'0', '1', '#', 'X', 'Y', 'B'}
B = 'B'
q0 = 'q0'
F = {'qACEIT', 'qREJ'}
L, R, S = 'L', 'R', 'S' #delta pode mover a cabeca para esquerda, direita ou ficar no lugar

delta = {
    #q0    busca digito nao-marcado (esquerda)"
    ('q0', '0'): ('m0', 'X', R),
    ('q0', '1'): ('m1', 'Y', R),
    ('q0', 'X'): ('q0', 'X', R),
    ('q0', 'Y'): ('q0', 'Y', R),
    ('q0', '#'): ('v',  '#', R),
    ('q0', 'B'): ('qREJ', 'B', S),

    #m0    marcou x; indo ate o '#'"
    ('m0', '0'): ('m0', '0', R),
    ('m0', '1'): ('m0', '1', R),
    ('m0', 'X'): ('m0', 'X', R),
    ('m0', 'Y'): ('m0', 'Y', R),
    ('m0', '#'): ('n0', '#', R),
    ('m0', 'B'): ('qREJ', 'B', S),

    #m1    marcou y; indo ate o '#'"
    ('m1', '0'): ('m1', '0', R),
    ('m1', '1'): ('m1', '1', R),
    ('m1', 'X'): ('m1', 'X', R),
    ('m1', 'Y'): ('m1', 'Y', R),
    ('m1', '#'): ('n1', '#', R),
    ('m1', 'B'): ('qREJ', 'B', S),

    #n0    cruzou '#' - procura '0' na direita"
    ('n0', 'X'): ('n0', 'X', R),
    ('n0', 'Y'): ('n0', 'Y', R),
    ('n0', '0'): ('ret', 'X', L),
    ('n0', '1'): ('qREJ', '1', S),
    ('n0', 'B'): ('qREJ', 'B', S),
    ('n0', '#'): ('qREJ', '#', S),

    #n1    cruzou '#' - procura '1' na direita"
    ('n1', 'X'): ('n1', 'X', R),
    ('n1', 'Y'): ('n1', 'Y', R),
    ('n1', '1'): ('ret', 'Y', L),
    ('n1', '0'): ('qREJ', '0', S),
    ('n1', 'B'): ('qREJ', 'B', S),
    ('n1', '#'): ('qREJ', '#', S),

    #ret   retornando pro inicio"
    ('ret', '0'): ('ret', '0', L),
    ('ret', '1'): ('ret', '1', L),
    ('ret', 'X'): ('ret', 'X', L),
    ('ret', 'Y'): ('ret', 'Y', L),
    ('ret', '#'): ('ret', '#', L),
    ('ret', 'B'): ('q0',  'B', R),   # esta na borda esquerda

    #verifica que a direita esta toda marcada"
    ('v', 'X'): ('v', 'X', R),
    ('v', 'Y'): ('v', 'Y', R),
    ('v', '0'): ('qREJ', '0', S),
    ('v', '1'): ('qREJ', '1', S),
    ('v', 'B'): ('qACEIT', 'B', S),
    ('v', '#'): ('qREJ', '#', S),
}


def reconhecer(entrada: str) -> dict:
    #Simula a MT e devolve aceita - passos - trace - estado_final- fita_final.
    fita = {i: c for i, c in enumerate(entrada)}
    cabeca = 0
    estado = q0
    passos = 0
    trace  = []

    MAX_PASSOS = 50000  # decisor sempre ira para antes disso

    def fita_str(fita, cabeca, estado):
        #Gera a descricao instantanea no formato αq[s]β
        if not fita:
            return f"{estado}B"
        min_pos = min(fita.keys())
        max_pos = max(fita.keys())
        min_pos = min(min_pos, cabeca)
        max_pos = max(max_pos, cabeca)
        esq = ''.join(fita.get(i, 'B') for i in range(min_pos, cabeca))
        sim = fita.get(cabeca, 'B')
        dir_ = ''.join(fita.get(i, 'B') for i in range(cabeca + 1, max_pos + 1))
        return f"{esq}{estado}[{sim}]{dir_}"

    while estado not in F and passos < MAX_PASSOS:
        simbolo_lido = fita.get(cabeca, B)
        chave = (estado, simbolo_lido)

        trace.append({
            'passo'       : passos + 1,
            'id'          : fita_str(fita, cabeca, estado),
            'estado'      : estado,
            'cabeca'      : cabeca,
            'simbolo_lido': simbolo_lido,
        })

        if chave not in delta:
            estado = 'qREJ'
            break

        novo_estado, simbolo_escrito, direcao = delta[chave]

        # executa um passo: escreve, move cabeca, troca estado
        fita[cabeca] = simbolo_escrito
        if direcao == R:
            cabeca += 1
        elif direcao == L:
            cabeca -= 1
        # S = fica no lugar

        estado = novo_estado
        passos += 1

    trace.append({
        'passo'       : passos + 1,
        'id'          : fita_str(fita, cabeca, estado),
        'estado'      : estado,
        'cabeca'      : cabeca,
        'simbolo_lido': fita.get(cabeca, B),
    })

    aceita = (estado == 'qACEIT')

    return {
        'aceita'      : aceita,
        'passos'      : passos,
        'trace'       : trace,
        'estado_final': estado,
        'fita_final'  : fita,
    }


def exibir_execucao(entrada: str, max_trace: int = 60):
    resultado = reconhecer(entrada)
    print(f"\n{'='*72}")
    print(f"MT — w#w  |  Entrada: '{entrada}'")
    print(f"{'='*72}")
    print(f"{'Passo':<7} {'Estado':<10} {'Lê':<5} {'Descrição Instantânea (ID)'}")
    print(f"{'-'*72}")
    for t in resultado['trace'][:max_trace]:
        print(f"{t['passo']:<7} {t['estado']:<10} {repr(t['simbolo_lido']):<5} {t['id']}")
    if len(resultado['trace']) > max_trace:
        omitidos = len(resultado['trace']) - max_trace
        print(f"  ... ({omitidos} passos omitidos) ...")
    print(f"{'-'*72}")
    print(f"Estado final  : {resultado['estado_final']}")
    print(f"Passos totais : {resultado['passos']}")
    print(f"Resultado     : {'ACEITA ✓' if resultado['aceita'] else 'REJEITA ✗'}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/recursiva.py \"<cadeia>\"")
        print("Exemplo: python src/recursiva.py \"101#101\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
