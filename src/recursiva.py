"""
recursiva.py — Reconhecedor de Linguagem Recursiva (Nível R)
=============================================================
Tema 1: Verificador de cópia de cadeia  L = { w#w | w ∈ {0,1}* }

Modelo computacional: MT (Máquina de Turing determinística)
Definição formal   : M = (Q, Σ, Γ, δ, q0, B, F)

Fundamentação teórica — Aula 7 (Prof. Jairo):
  • MT é uma 7-tupla M = (Q, Σ, Γ, δ, q0, B, F)
  • δ : (Q ∖ F) × Γ → Q × Γ × D   com  D = {L, R, S}
  • A cada passo: lê símbolo → escreve símbolo → move cabeça → troca estado
  • Descrição Instantânea (ID): αqβ  (estado no meio da fita)
  • Um passo = um ciclo  (lê, escreve, move)  ⊢M
  • A MT é um decisor (sempre para): L ∈ R ⊆ RE

Algoritmo (marcação cruzada — padrão das aulas):
  Fase 1: se a fita está só com '#' → aceita (w = ε, w#w = "#" vazio não é aceito aqui)
  Loop:
    Fase 2: Varre da esquerda; encontra o primeiro '0' ou '1' não-marcado → marca com X ou Y.
            Se encontra '#' sem encontrar dígito → toda a parte esquerda foi marcada.
    Fase 3: Cruza o '#' e localiza o símbolo correspondente na parte direita.
            Se bate (X↔0, Y↔1) → marca com X ou Y.
            Se não bate → rejeita.
    Fase 4: Retorna à posição inicial (esquerda) para o próximo símbolo.
  Fase final: verifica se todos os dígitos à direita de '#' também foram marcados → aceita.

Estados (seguindo nomenclatura da Aula 7):
  q0    : estado inicial / varredura buscando dígito não-marcado (parte esquerda)
  m0    : marcou '0' (X) na parte esquerda; indo para a direita buscar '#'
  m1    : marcou '1' (Y) na parte esquerda; indo para a direita buscar '#'
  n0    : cruzou '#' com X; buscando correspondente '0' na parte direita
  n1    : cruzou '#' com Y; buscando correspondente '1' na parte direita
  v     : verificando que a parte direita está toda marcada (pós-varredura esq.)
  ret   : retornando para o início (esquerda) após marcar na parte direita
  qACEIT: estado de aceitação  ∈ F
  qREJ  : estado de rejeição   ∈ F (decididor — sempre para)

Linguagem:
  L = { w#w | w ∈ {0,1}* }
  Σ = {0, 1, #}
  Γ = {0, 1, #, X, Y, B}   (B = símbolo branco)

Exemplos aceitos  : 101#101   0#0   11#11   #  (w = ε)
Exemplos rejeitados: 101#100   1#0   01#10
"""

import sys

# ---------------------------------------------------------------------------
# 1. DEFINIÇÃO FORMAL DA MT  M = (Q, Sigma, Gamma, delta, q0, B, F)
# ---------------------------------------------------------------------------

# Conjunto de estados Q
Q = {'q0', 'm0', 'm1', 'n0', 'n1', 'v', 'ret', 'qACEIT', 'qREJ'}

# Alfabeto de entrada Σ
SIGMA = {'0', '1', '#'}

# Alfabeto da fita Γ (Σ ∪ {X, Y, B})
GAMMA = {'0', '1', '#', 'X', 'Y', 'B'}

# Símbolo branco
B = 'B'

# Estado inicial
q0 = 'q0'

# Estados finais F  (decisor: aceita OU rejeita, sempre para)
F = {'qACEIT', 'qREJ'}

# Direções
L, R, S = 'L', 'R', 'S'

# ---------------------------------------------------------------------------
# Função de transição δ declarada como dicionário de dados estruturados.
# Chave  : (estado, simbolo_lido)
# Valor  : (novo_estado, simbolo_escrito, direcao)
#
# Tabela completa de transições:
#
# Estado q0 — busca o primeiro dígito não-marcado na parte esquerda
#   q0, 0  → m0, X, R   (marca 0 com X; vai buscar o '#' e depois o par)
#   q0, 1  → m1, Y, R   (marca 1 com Y)
#   q0, X  → q0, X, R   (pula marcas já feitas)
#   q0, Y  → q0, Y, R   (pula marcas já feitas)
#   q0, #  → v,  #, R   (chegou ao '#' sem dígito: vai verificar parte direita)
#
# Estado m0 — marcou X (era 0); avança até o '#'
#   m0, 0  → m0, 0, R
#   m0, 1  → m0, 1, R
#   m0, X  → m0, X, R
#   m0, Y  → m0, Y, R
#   m0, #  → n0, #, R   (cruzou '#'; agora busca '0' na parte direita)
#
# Estado m1 — marcou Y (era 1); avança até o '#'
#   m1, 0  → m1, 0, R
#   m1, 1  → m1, 1, R
#   m1, X  → m1, X, R
#   m1, Y  → m1, Y, R
#   m1, #  → n1, #, R   (cruzou '#'; busca '1' na parte direita)
#
# Estado n0 — procura o '0' correspondente na parte direita
#   n0, X  → n0, X, R   (pula marcas já feitas)
#   n0, Y  → n0, Y, R
#   n0, 0  → ret, X, L  (encontrou o par correto: marca e retorna)
#   n0, 1  → qREJ,1, S  (mismatch: rejeita)
#   n0, B  → qREJ,B, S  (parte direita mais curta: rejeita)
#
# Estado n1 — procura o '1' correspondente na parte direita
#   n1, X  → n1, X, R
#   n1, Y  → n1, Y, R
#   n1, 1  → ret, Y, L  (par correto: marca e retorna)
#   n1, 0  → qREJ,0, S  (mismatch)
#   n1, B  → qREJ,B, S
#
# Estado ret — retorna ao início para o próximo símbolo
#   ret, 0  → ret, 0, L
#   ret, 1  → ret, 1, L
#   ret, X  → ret, X, L
#   ret, Y  → ret, Y, L
#   ret, #  → ret, #, L
#   ret, B  → q0,  B, R  (chegou na borda esquerda; reinicia)
#
# Estado v — verifica que parte direita está toda marcada
#   v, X  → v, X, R
#   v, Y  → v, Y, R
#   v, 0  → qREJ,0, S   (parte direita tem dígito não-marcado: tamanhos diferentes)
#   v, 1  → qREJ,1, S
#   v, B  → qACEIT,B,S  (tudo marcado: aceita!)
# ---------------------------------------------------------------------------

delta = {
    # --- q0: busca dígito não-marcado ---
    ('q0', '0'): ('m0', 'X', R),
    ('q0', '1'): ('m1', 'Y', R),
    ('q0', 'X'): ('q0', 'X', R),
    ('q0', 'Y'): ('q0', 'Y', R),
    ('q0', '#'): ('v',  '#', R),
    ('q0', 'B'): ('qREJ', 'B', S),   # entrada vazia ou malformada

    # --- m0: avança até '#' após marcar X ---
    ('m0', '0'): ('m0', '0', R),
    ('m0', '1'): ('m0', '1', R),
    ('m0', 'X'): ('m0', 'X', R),
    ('m0', 'Y'): ('m0', 'Y', R),
    ('m0', '#'): ('n0', '#', R),
    ('m0', 'B'): ('qREJ', 'B', S),   # sem '#': malformada

    # --- m1: avança até '#' após marcar Y ---
    ('m1', '0'): ('m1', '0', R),
    ('m1', '1'): ('m1', '1', R),
    ('m1', 'X'): ('m1', 'X', R),
    ('m1', 'Y'): ('m1', 'Y', R),
    ('m1', '#'): ('n1', '#', R),
    ('m1', 'B'): ('qREJ', 'B', S),

    # --- n0: procura '0' na parte direita ---
    ('n0', 'X'): ('n0', 'X', R),
    ('n0', 'Y'): ('n0', 'Y', R),
    ('n0', '0'): ('ret', 'X', L),
    ('n0', '1'): ('qREJ', '1', S),
    ('n0', 'B'): ('qREJ', 'B', S),
    ('n0', '#'): ('qREJ', '#', S),

    # --- n1: procura '1' na parte direita ---
    ('n1', 'X'): ('n1', 'X', R),
    ('n1', 'Y'): ('n1', 'Y', R),
    ('n1', '1'): ('ret', 'Y', L),
    ('n1', '0'): ('qREJ', '0', S),
    ('n1', 'B'): ('qREJ', 'B', S),
    ('n1', '#'): ('qREJ', '#', S),

    # --- ret: retorna para o início ---
    ('ret', '0'): ('ret', '0', L),
    ('ret', '1'): ('ret', '1', L),
    ('ret', 'X'): ('ret', 'X', L),
    ('ret', 'Y'): ('ret', 'Y', L),
    ('ret', '#'): ('ret', '#', L),
    ('ret', 'B'): ('q0',  'B', R),   # borda esquerda: reinicia

    # --- v: verifica parte direita toda marcada ---
    ('v', 'X'): ('v', 'X', R),
    ('v', 'Y'): ('v', 'Y', R),
    ('v', '0'): ('qREJ', '0', S),
    ('v', '1'): ('qREJ', '1', S),
    ('v', 'B'): ('qACEIT', 'B', S),
    ('v', '#'): ('qREJ', '#', S),    # segundo '#': malformado
}

# ---------------------------------------------------------------------------
# 2. SIMULADOR DA MT — fita como dicionário {posicao: simbolo}
# ---------------------------------------------------------------------------

def reconhecer(entrada: str) -> dict:
    """
    Simula a MT M sobre a cadeia `entrada`.

    Retorna dicionário com:
      - 'aceita' : bool
      - 'passos' : int   (cada ciclo lê-escreve-move = 1 passo formal ⊢M)
      - 'trace'  : lista de IDs  (descrição instantânea antes de cada passo)
      - 'estado_final': str
    """
    # Inicializa fita: posição 0..len-1 com a entrada; resto é B
    fita = {i: c for i, c in enumerate(entrada)}
    cabeca = 0
    estado = q0
    passos = 0
    trace  = []

    MAX_PASSOS = 50000  # guarda contra loop infinito (não deve ocorrer, MT é decisor)

    def fita_str(fita, cabeca, estado):
        """Gera representação ID: αqβ"""
        if not fita:
            return f"{estado}B"
        min_pos = min(fita.keys())
        max_pos = max(fita.keys())
        # Expande para incluir a posição da cabeça
        min_pos = min(min_pos, cabeca)
        max_pos = max(max_pos, cabeca)
        esq = ''.join(fita.get(i, 'B') for i in range(min_pos, cabeca))
        sim = fita.get(cabeca, 'B')
        dir_ = ''.join(fita.get(i, 'B') for i in range(cabeca + 1, max_pos + 1))
        return f"{esq}{estado}[{sim}]{dir_}"

    while estado not in F and passos < MAX_PASSOS:
        simbolo_lido = fita.get(cabeca, B)
        chave = (estado, simbolo_lido)

        # Registra ID antes do passo
        trace.append({
            'passo'       : passos + 1,
            'id'          : fita_str(fita, cabeca, estado),
            'estado'      : estado,
            'cabeca'      : cabeca,
            'simbolo_lido': simbolo_lido,
        })

        if chave not in delta:
            # Sem transição definida: MT trava → rejeita
            estado = 'qREJ'
            break

        novo_estado, simbolo_escrito, direcao = delta[chave]

        # Executa o passo: escreve, move, muda estado  ← 1 passo formal ⊢M
        fita[cabeca] = simbolo_escrito
        if direcao == R:
            cabeca += 1
        elif direcao == L:
            cabeca -= 1
        # S = fica no lugar

        estado = novo_estado
        passos += 1

    # Registra estado final
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

# ---------------------------------------------------------------------------
# 3. EXECUÇÃO PASSO A PASSO (saída detalhada)
# ---------------------------------------------------------------------------

def exibir_execucao(entrada: str, max_trace: int = 60):
    """Imprime a execução passo a passo de uma cadeia."""
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
        print(f"  ... ({omitidos} passos omitidos para brevidade) ...")
    print(f"{'-'*72}")
    print(f"Estado final  : {resultado['estado_final']}")
    print(f"Passos totais : {resultado['passos']}")
    print(f"Resultado     : {'ACEITA ✓' if resultado['aceita'] else 'REJEITA ✗'}")

# ---------------------------------------------------------------------------
# 4. PONTO DE ENTRADA AUTÔNOMO
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python src/recursiva.py \"<cadeia>\"")
        print("Exemplo: python src/recursiva.py \"101#101\"")
        sys.exit(1)

    entrada = sys.argv[1]
    exibir_execucao(entrada)
    resultado = reconhecer(entrada)
    sys.exit(0 if resultado['aceita'] else 1)
