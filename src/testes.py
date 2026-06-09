"""
testes.py — Bateria de Testes Integrada
========================================
Lê os arquivos testes/testes_*.txt e executa os três reconhecedores.
Exibe tabela comparativa: esperado vs. obtido + número de passos.

Formato dos arquivos .txt:
  Cada linha: <cadeia>;<esperado>
  onde <esperado> é  ACEITA  ou  REJEITA
  Linhas começando com '#' são comentários.

Uso:
  python src/testes.py
"""

import os
import sys

# Garante que src/ está no path para importar os módulos
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)

from regular       import reconhecer as dfa_reconhecer
from livre_contexto import reconhecer as pda_reconhecer
from recursiva     import reconhecer as mt_reconhecer

# ---------------------------------------------------------------------------
# Caminhos dos arquivos de teste
# ---------------------------------------------------------------------------

RAIZ = os.path.join(SRC_DIR, '..')
ARQ_REGULAR       = os.path.join(RAIZ, 'testes', 'testes_regular.txt')
ARQ_LLC           = os.path.join(RAIZ, 'testes', 'testes_livre_contexto.txt')
ARQ_RECURSIVA     = os.path.join(RAIZ, 'testes', 'testes_recursiva.txt')

# ---------------------------------------------------------------------------
# Leitor de arquivo de testes
# ---------------------------------------------------------------------------

def ler_casos(caminho: str) -> list:
    """Lê o arquivo e retorna lista de (cadeia, esperado_bool)."""
    casos = []
    with open(caminho, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue
            partes = linha.split(';')
            if len(partes) != 2:
                continue
            cadeia, esperado_str = partes[0], partes[1].strip().upper()
            esperado = (esperado_str == 'ACEITA')
            casos.append((cadeia, esperado))
    return casos

# ---------------------------------------------------------------------------
# Executor de bateria
# ---------------------------------------------------------------------------

def executar_bateria(nome: str, casos: list, reconhecedor) -> dict:
    """
    Executa todos os casos de teste para um reconhecedor.
    Retorna estatísticas e resultados detalhados.
    """
    resultados = []
    acertos    = 0

    print(f"\n{'='*78}")
    print(f"  NÍVEL: {nome}")
    print(f"{'='*78}")
    print(f"{'#':<4} {'Cadeia':<28} {'Esperado':<10} {'Obtido':<10} {'Passos':<8} {'OK?'}")
    print(f"{'-'*78}")

    for i, (cadeia, esperado) in enumerate(casos, start=1):
        res     = reconhecedor(cadeia)
        obtido  = res['aceita']
        passos  = res['passos']
        correto = (obtido == esperado)

        if correto:
            acertos += 1

        esperado_str = 'ACEITA' if esperado else 'REJEITA'
        obtido_str   = 'ACEITA' if obtido   else 'REJEITA'
        ok_str       = '✓' if correto else '✗ ERRO'

        cadeia_exib = repr(cadeia) if len(cadeia) <= 25 else repr(cadeia[:22] + '...')
        print(f"{i:<4} {cadeia_exib:<28} {esperado_str:<10} {obtido_str:<10} {passos:<8} {ok_str}")

        resultados.append({
            'cadeia'  : cadeia,
            'esperado': esperado,
            'obtido'  : obtido,
            'passos'  : passos,
            'correto' : correto,
        })

    print(f"{'-'*78}")
    total   = len(casos)
    erros   = total - acertos
    passos_lista = [r['passos'] for r in resultados]
    media   = sum(passos_lista) / len(passos_lista) if passos_lista else 0

    print(f"  Acertos : {acertos}/{total}   |   Erros: {erros}")
    print(f"  Passos  — mín: {min(passos_lista)}  máx: {max(passos_lista)}  média: {media:.1f}")

    return {
        'nome'        : nome,
        'total'       : total,
        'acertos'     : acertos,
        'erros'       : erros,
        'resultados'  : resultados,
        'passos_min'  : min(passos_lista),
        'passos_max'  : max(passos_lista),
        'passos_media': media,
    }

# ---------------------------------------------------------------------------
# Comparação entre níveis
# ---------------------------------------------------------------------------

def exibir_comparacao(stats: list):
    """Exibe tabela comparativa entre os três níveis."""
    print(f"\n{'='*78}")
    print(f"  COMPARAÇÃO ENTRE OS TRÊS NÍVEIS DA HIERARQUIA DE CHOMSKY")
    print(f"{'='*78}")
    print(f"{'Nível':<30} {'Modelo':<8} {'Acertos':<10} {'Passos Mín':<12} {'Passos Máx':<12} {'Média'}")
    print(f"{'-'*78}")

    modelos = {'DFA — CPF (LR)': 'DFA', 'PDA — Balanceamento (LLC)': 'PDA', 'MT — w#w (R)': 'MT'}

    for s in stats:
        modelo = modelos.get(s['nome'], '?')
        print(f"{s['nome']:<30} {modelo:<8} {s['acertos']}/{s['total']:<7} "
              f"{s['passos_min']:<12} {s['passos_max']:<12} {s['passos_media']:.1f}")

    print(f"\n  Hierarquia confirmada: LR ⊊ LLC ⊊ R")
    print(f"  L(DFA) = L(NFA) = L(ER)  ⊊  L(PDA) = L(GLC)  ⊊  L(MT decisor)")
    print(f"{'='*78}\n")

# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*78)
    print("  VALIDADOR FORMAL EM TRÊS NÍVEIS — Bateria de Testes Completa")
    print("  Disciplina: Modelagem Computacional | Prof. Dr. José Jairo")
    print("="*78)

    todas_ok = True
    stats = []

    # Nível LR — DFA
    try:
        casos_lr = ler_casos(ARQ_REGULAR)
        s = executar_bateria('DFA — CPF (LR)', casos_lr, dfa_reconhecer)
        stats.append(s)
        if s['erros'] > 0:
            todas_ok = False
    except FileNotFoundError:
        print(f"\n[ERRO] Arquivo não encontrado: {ARQ_REGULAR}")
        todas_ok = False

    # Nível LLC — PDA
    try:
        casos_llc = ler_casos(ARQ_LLC)
        s = executar_bateria('PDA — Balanceamento (LLC)', casos_llc, pda_reconhecer)
        stats.append(s)
        if s['erros'] > 0:
            todas_ok = False
    except FileNotFoundError:
        print(f"\n[ERRO] Arquivo não encontrado: {ARQ_LLC}")
        todas_ok = False

    # Nível R — MT
    try:
        casos_r = ler_casos(ARQ_RECURSIVA)
        s = executar_bateria('MT — w#w (R)', casos_r, mt_reconhecer)
        stats.append(s)
        if s['erros'] > 0:
            todas_ok = False
    except FileNotFoundError:
        print(f"\n[ERRO] Arquivo não encontrado: {ARQ_RECURSIVA}")
        todas_ok = False

    if stats:
        exibir_comparacao(stats)

    if todas_ok:
        print("  RESULTADO FINAL: TODOS OS TESTES PASSARAM ✓\n")
        sys.exit(0)
    else:
        print("  RESULTADO FINAL: ALGUNS TESTES FALHARAM ✗\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
