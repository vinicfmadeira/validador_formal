"""
gerar_diagramas.py — Gera os diagramas formais dos três autômatos
=================================================================
Usa a biblioteca graphviz para gerar arquivos .dot e .png
"""

import graphviz
import os

SAIDA = os.path.join(os.path.dirname(__file__), '..', 'diagramas')
os.makedirs(SAIDA, exist_ok=True)

# ---------------------------------------------------------------------------
# Diagrama 1: DFA para CPF  ddd.ddd.ddd-dd
# ---------------------------------------------------------------------------

def gerar_dfa():
    d = graphviz.Digraph(
        name='dfa_cpf',
        comment='DFA — CPF formato ddd.ddd.ddd-dd',
        graph_attr={'rankdir': 'LR', 'fontname': 'Helvetica', 'bgcolor': 'white'},
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '10'},
    )

    # Nó seta de início (invisível)
    d.node('start', shape='none', label='')
    d.edge('start', 'q0')

    # Estados normais (q0..q13)
    for i in range(14):
        d.node(f'q{i}', f'q{i}', shape='circle')

    # Estado final (duplo círculo)
    d.node('q14', 'q14', shape='doublecircle')

    # Estado de erro
    d.node('qERR', 'qERR', shape='circle', style='filled', fillcolor='#ffcccc')

    # Transições agrupadas para legibilidade
    # Grupos de posições que esperam dígito
    grupos_digito = [(0,1),(1,2),(2,3,'.'),(3,4),(4,5),(5,6),(6,7),(7,8,'.'),(8,9),(9,10),(10,11),(11,12,'-'),(12,13),(13,14)]

    for entry in grupos_digito:
        if len(entry) == 2:
            origem, dest = entry
            label = '0-9'
            d.edge(f'q{origem}', f'q{dest}', label=label)
            d.edge(f'q{origem}', 'qERR', label='outro')
        else:
            origem, dest, sym = entry
            d.edge(f'q{origem}', f'q{dest}', label=repr(sym))
            d.edge(f'q{origem}', 'qERR', label='outro')

    # qERR self-loop
    d.edge('qERR', 'qERR', label='Σ')
    # q14 → qERR se receber mais entrada
    d.edge('q14', 'qERR', label='Σ')

    caminho = os.path.join(SAIDA, 'dfa_regular')
    d.render(caminho, format='png', cleanup=True)
    # Salva também o .dot
    with open(caminho + '.dot', 'w') as f:
        f.write(d.source)
    print(f"  ✓ DFA salvo em {caminho}.png e .dot")

# ---------------------------------------------------------------------------
# Diagrama 2: PDA para balanceamento de parênteses e colchetes
# ---------------------------------------------------------------------------

def gerar_pda():
    d = graphviz.Digraph(
        name='pda_balanceamento',
        comment='PDA — Parênteses e colchetes balanceados',
        graph_attr={'rankdir': 'LR', 'fontname': 'Helvetica', 'bgcolor': 'white'},
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    d.node('start', shape='none', label='')
    d.edge('start', 'q0')

    d.node('q0',     'q0',     shape='circle')
    d.node('qACEIT', 'qACEIT', shape='doublecircle')
    d.node('qERR',   'qERR',   shape='circle', style='filled', fillcolor='#ffcccc')

    # Transições principais (notação: a, X/α)
    d.edge('q0', 'q0', label='(, X/PAREN X\n[, X/COLCH X\n(para todo X∈Γ)')
    d.edge('q0', 'q0', label='), PAREN/ε\n], COLCH/ε')
    d.edge('q0', 'qERR', label='), COLCH/COLCH\n), Z0/Z0\n], PAREN/PAREN\n], Z0/Z0')
    d.edge('q0', 'qACEIT', label='ε, Z0/Z0\n(entrada esgotada)')

    caminho = os.path.join(SAIDA, 'pda_livre_contexto')
    d.render(caminho, format='png', cleanup=True)
    with open(caminho + '.dot', 'w') as f:
        f.write(d.source)
    print(f"  ✓ PDA salvo em {caminho}.png e .dot")

# ---------------------------------------------------------------------------
# Diagrama 3: MT para w#w
# ---------------------------------------------------------------------------

def gerar_mt():
    d = graphviz.Digraph(
        name='mt_whasw',
        comment='MT — L = {w#w | w ∈ {0,1}*}',
        graph_attr={'rankdir': 'LR', 'fontname': 'Helvetica', 'bgcolor': 'white',
                    'nodesep': '0.5', 'ranksep': '0.7'},
        node_attr={'fontname': 'Helvetica', 'fontsize': '11'},
        edge_attr={'fontname': 'Helvetica', 'fontsize': '9'},
    )

    d.node('start', shape='none', label='')
    d.edge('start', 'q0')

    estados = ['q0', 'm0', 'm1', 'n0', 'n1', 'v', 'ret']
    for e in estados:
        d.node(e, e, shape='circle')

    d.node('qACEIT', 'qACEIT', shape='doublecircle')
    d.node('qREJ',   'qREJ',   shape='doublecircle',
           style='filled', fillcolor='#ffcccc')

    # Transições agrupadas por destino para legibilidade
    # q0
    d.edge('q0', 'm0', label='0→X, R')
    d.edge('q0', 'm1', label='1→Y, R')
    d.edge('q0', 'v',  label='#→#, R')
    d.edge('q0', 'q0', label='X→X,R\nY→Y,R')
    d.edge('q0', 'qREJ', label='B→B,S')

    # m0 e m1
    d.edge('m0', 'm0', label='0,1,X,Y→manter,R')
    d.edge('m0', 'n0', label='#→#, R')
    d.edge('m0', 'qREJ', label='B→B,S')

    d.edge('m1', 'm1', label='0,1,X,Y→manter,R')
    d.edge('m1', 'n1', label='#→#, R')
    d.edge('m1', 'qREJ', label='B→B,S')

    # n0 e n1
    d.edge('n0', 'n0', label='X,Y→manter,R')
    d.edge('n0', 'ret', label='0→X, L')
    d.edge('n0', 'qREJ', label='1,B,#→manter,S')

    d.edge('n1', 'n1', label='X,Y→manter,R')
    d.edge('n1', 'ret', label='1→Y, L')
    d.edge('n1', 'qREJ', label='0,B,#→manter,S')

    # ret
    d.edge('ret', 'ret', label='0,1,X,Y,#→manter,L')
    d.edge('ret', 'q0', label='B→B, R')

    # v (verificação final)
    d.edge('v', 'v', label='X,Y→manter,R')
    d.edge('v', 'qACEIT', label='B→B,S')
    d.edge('v', 'qREJ', label='0,1,#→manter,S')

    caminho = os.path.join(SAIDA, 'mt_recursiva')
    d.render(caminho, format='png', cleanup=True)
    with open(caminho + '.dot', 'w') as f:
        f.write(d.source)
    print(f"  ✓ MT salvo em {caminho}.png e .dot")

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("Gerando diagramas...")
    gerar_dfa()
    gerar_pda()
    gerar_mt()
    print("Diagramas gerados com sucesso!")
