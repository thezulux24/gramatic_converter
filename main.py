import streamlit as st
from collections import defaultdict
import copy
import sys
sys.setrecursionlimit(10000)

def parse_grammar(input_text):
    grammar = defaultdict(list)
    input_text = input_text.replace("→", "->").replace("ε", "*")
    for line in input_text.strip().split('\n'):
        if '->' in line:
            head, prods = line.split('->')
            head = head.strip()
            for prod in prods.split('|'):
                prod = prod.strip()
                grammar[head].append(prod)
    return dict(grammar)

def find_nullable(grammar):
    nullable = set()
    changed = True
    while changed:
        changed = False
        for head, prods in grammar.items():
            for p in prods:
                if p == '*' or all(symbol in nullable for symbol in p):
                    if head not in nullable:
                        nullable.add(head)
                        changed = True
    return nullable

def remove_epsilon(grammar, start):
    nullable = find_nullable(grammar)
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        for prod in prods:
            if prod != '*':
                indices = [i for i, s in enumerate(prod) if s in nullable]
                for mask in range(1 << len(indices)):
                    s = list(prod)
                    for bit, idx in enumerate(indices):
                        if mask & (1 << bit):
                            s[idx] = ''
                    new_prod = ''.join(c for c in s if c)
                    if new_prod:
                        new_grammar[head].append(new_prod)
                    else:
                        if head == start:
                            new_grammar[head].append('*')
            else:
                pass
    if start in nullable and '*' not in new_grammar[start]:
        new_grammar[start].append('*')
    return {h: list(set(ps)) for h, ps in new_grammar.items()}

def remove_unit(grammar, start):
    new_grammar = defaultdict(list)
    for head in grammar:
        stack = [head]
        seen = set(stack)
        while stack:
            cur = stack.pop()
            for prod in grammar[cur]:
                if prod in grammar:
                    if prod not in seen:
                        seen.add(prod)
                        stack.append(prod)
                else:
                    new_grammar[head].append(prod)
        new_grammar[head] = list(set(new_grammar[head]))
    return dict(new_grammar)

def remove_useless(grammar, start):
    reachable = set([start])
    changed = True
    while changed:
        changed = False
        for head in list(reachable):
            for prod in grammar.get(head, []):
                for s in prod:
                    if s.isupper() and s not in reachable:
                        reachable.add(s)
                        changed = True
    productive = set()
    changed = True
    while changed:
        changed = False
        for head, prods in grammar.items():
            for prod in prods:
                if all((not c.isupper()) or c in productive for c in prod) and head not in productive:
                    productive.add(head)
                    changed = True
    valid = reachable & productive
    return {h: [p for p in prods if all((not c.isupper()) or c in valid for c in p)]
            for h, prods in grammar.items() if h in valid}

def to_cnf(grammar, start):
    G = remove_useless(remove_unit(remove_epsilon(grammar, start), start), start)
    counters = {'X': 0}
    mapping = {}
    letter_mapping = {0: 'C', 1: 'D', 2: 'E', 3: 'F', 4: 'G', 5: 'H', 6: 'I', 7: 'J', 8: 'K'}
    cnf = defaultdict(list)
    for head, prods in G.items():
        for prod in prods:
            if prod != '*':
                if len(prod) > 1:
                    new_prod = []
                    for c in prod:
                        if c.islower():
                            if c not in mapping:
                                if c == 'a':
                                    mapping[c] = 'D'
                                    cnf['D'] = [c]
                                elif c == 'b':
                                    mapping[c] = 'C'
                                    cnf['C'] = [c]
                                else:
                                    counters['X'] += 1
                                    next_letter = letter_mapping.get(counters['X'], f"X{counters['X']}")
                                    mapping[c] = next_letter
                                    cnf[next_letter] = [c]
                            new_prod.append(mapping[c])
                        else:
                            new_prod.append(c)
                    cnf[head].append(''.join(new_prod))
                else:
                    cnf[head].append(prod)
            else:
                if head == start:
                    cnf[head].append('*')
    final_cnf = defaultdict(list)
    split_mapping = {}
    split_counter = 1
    for head, prods in cnf.items():
        for prod in prods:
            if prod == '*' or len(prod) <= 2:
                final_cnf[head].append(prod)
            else:
                current_prod = prod
                while len(current_prod) > 2:
                    A = current_prod[0]
                    rest = current_prod[1:]
                    if rest in split_mapping:
                        X = split_mapping[rest]
                    else:
                        split_counter += 1
                        X = letter_mapping.get(split_counter, f"X{split_counter}")
                        split_mapping[rest] = X
                        final_cnf[X] = [rest]
                    current_prod = A + X
                final_cnf[head].append(current_prod)
    return {h: list(set(ps)) for h, ps in final_cnf.items()}
def to_gnf(grammar, start):
    pass

def remove_left_recursion(grammar):
    pass


def display_grammar(grammar, container):
    for head, prods in grammar.items():
        productions = []
        for prod in prods:
            if prod == "*":
                productions.append("ε")
            else:
                productions.append(prod)
        productions_str = " | ".join(productions)
        container.markdown(f"**{head}** → {productions_str}")

def main():
    st.set_page_config(page_title="Conversor de Gramáticas", page_icon="🔤", layout="wide")
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 3em;
        color: #E53935;
        margin-bottom: 0.5em;
    }
    .section-header {
        background: #E53935;
        color: white;
        padding: 12px 15px;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .section-header h3 {
        margin: 0;
        font-weight: 500;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .grammar-container {
        background-color: #fff9f9;
        border-left: 3px solid #E53935;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .info-box {
        background-color: #FFEBEE;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #FFCDD2;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Conversor de Gramáticas</h1>', unsafe_allow_html=True)
    with st.sidebar:
        st.header("Acerca de las conversiones")
        st.markdown("""
        ### Gramática Bien Formada
        - Sin producciones epsilon (ε)
        - Sin producciones unitarias (A→B)
        - Sin símbolos inútiles
        """)
        st.markdown("""
        ### Forma Normal de Chomsky
        Todas las producciones tienen la forma:
        - A → BC (donde B y C son no terminales)
        - A → a (donde a es terminal)
        """)
        st.markdown("""
        ### Forma Normal de Greibach
        Todas las producciones tienen la forma:
        - A → aα (donde a es terminal y α es una cadena de no terminales)
        """)
        st.markdown("""
        ### Ejemplo de gramática
        S -> bA | aB
        A -> bAA | aS | a
        B -> aBB | bS | b
        """)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-header"><h3>Ingresa tu gramática</h3></div>', unsafe_allow_html=True)
        st.markdown("""
        Introduce la gramática usando:
        - `->` para las producciones
        - `|` para separar alternativas
        - `*` para representar epsilon/vacío
        """)
        input_grammar = st.text_area("Gramática:", height=200, placeholder="S -> bA | aB\nA -> bAA | aS | a\nB -> aBB | bS | b")
        start_symbol = st.text_input("Símbolo inicial:", value='S')
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        ### Instrucciones
        1. Escribe cada producción en una línea separada
        2. Usa mayúsculas para no terminales
        3. Usa minúsculas para terminales
        4. Define el símbolo inicial
        5. Haz clic en "Convertir"
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        convert_button = st.button("Convertir", type="primary", use_container_width=True)
        if st.button("Limpiar", type="secondary", use_container_width=True):
            st.session_state.input_grammar = ""
            st.session_state.start_symbol = "S"
            st.experimental_rerun()
    if convert_button and input_grammar:
        try:
            grammar = parse_grammar(input_grammar)
            st.markdown('<div class="section-header"><h3>Gramática Original</h3></div>', unsafe_allow_html=True)
            with st.expander("Ver gramática original", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(grammar, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>Gramática Bien Formada</h3></div>', unsafe_allow_html=True)
            well_formed = remove_useless(remove_unit(remove_epsilon(grammar, start_symbol), start_symbol), start_symbol)
            with st.expander("Ver gramática bien formada", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(well_formed, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>Forma Normal de Chomsky</h3></div>', unsafe_allow_html=True)
            cnf = to_cnf(grammar, start_symbol)
            with st.expander("Ver forma normal de Chomsky", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(cnf, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>Forma Normal de Greibach</h3></div>', unsafe_allow_html=True)
            gnf = to_gnf(grammar, start_symbol)
            with st.expander("Ver forma normal de Greibach", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(gnf, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>Descargar resultados</h3></div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            def grammar_to_text(grammar):
                result = []
                for head, prods in grammar.items():
                    result.append(f"{head} -> {' | '.join(prods)}")
                return "\n".join(result)
            with col1:
                st.download_button(label="Descargar Bien Formada", data=grammar_to_text(well_formed), file_name="gramatica_bien_formada.txt", mime="text/plain")
            with col2:
                st.download_button(label="Descargar Chomsky", data=grammar_to_text(cnf), file_name="forma_normal_chomsky.txt", mime="text/plain")
            with col3:
                st.download_button(label="Descargar Greibach", data=grammar_to_text(gnf), file_name="forma_normal_greibach.txt", mime="text/plain")
        except Exception as e:
            st.error(f"Error al procesar la gramática: {str(e)}")
            st.error("Asegúrate de que la gramática esté correctamente formateada.")
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; opacity: 0.7;'>
            Conversor de Gramáticas © 2025
        </div>
    """, unsafe_allow_html=True)


main()