import streamlit as st
from collections import defaultdict
import copy
import sys
sys.setrecursionlimit(10000)

# esta funcion parsea la gramatica de un texto de entrada y devuelve un diccionario
# de producciones
def parse_grammar(input_text):
    # crea un diccionario que almacena listas de producciones por cada no terminal
    grammar = defaultdict(list)
    # reemplaza la flecha y la epsilon para facil manejo
    input_text = input_text.replace("→", "->").replace("ε", "*")
    # recorre cada linea de la entrada
    for line in input_text.strip().split('\n'):
        if '->' in line:
            head, prods = line.split('->')
            head = head.strip()
            for prod in prods.split('|'):
                prod = prod.strip()
                grammar[head].append(prod)
    return dict(grammar)

# funcion para encontrar los no terminales que generan cadena vacia
def find_nullable(grammar):
    nullable = set()
    changed = True
    # mientras se siga encontrando algun cambio
    while changed:
        changed = False
        for head, prods in grammar.items():
            for p in prods:
                # si la produccion es vacia o todos los simbolos pertenecen a nullable
                if p == '*' or all(symbol in nullable for symbol in p):
                    if head not in nullable:
                        nullable.add(head)
                        changed = True
    return nullable

# esta funcion elimina las producciones epsilon, excepto si es el simbolo inicial
def remove_epsilon(grammar, start):
    nullable = find_nullable(grammar)
    new_grammar = defaultdict(list)
    for head, prods in grammar.items():
        for prod in prods:
            if prod != '*':
                # obtiene los indices de los simbolos que pueden desaparecer
                indices = [i for i, s in enumerate(prod) if s in nullable]
                # genera todas las combinaciones posibles de remover o no los simbolos
                for mask in range(1 << len(indices)):
                    s = list(prod)
                    for bit, idx in enumerate(indices):
                        if mask & (1 << bit):
                            s[idx] = ''
                    new_prod = ''.join(c for c in s if c)
                    # si la produccion resultante no es vacia se agrega
                    if new_prod:
                        new_grammar[head].append(new_prod)
                    else:
                        # se deja la cadena vacia solo si es el simbolo inicial
                        if head == start:
                            new_grammar[head].append('*')
            else:
                pass
    # si el simbolo inicial es nullable se asegura mantener epsilon
    if start in nullable and '*' not in new_grammar[start]:
        new_grammar[start].append('*')
    return {h: list(set(ps)) for h, ps in new_grammar.items()}

# esta funcion elimina producciones unitarias (reglas del tipo A -> B)
def remove_unit(grammar, start):
    new_grammar = defaultdict(list)
    for head in grammar:
        stack = [head]
        seen = set(stack)
        # se usa una pila para recorrer unidades
        while stack:
            cur = stack.pop()
            for prod in grammar[cur]:
                # si la produccion es no terminal se sigue recorriendo
                if prod in grammar:
                    if prod not in seen:
                        seen.add(prod)
                        stack.append(prod)
                else:
                    new_grammar[head].append(prod)
        new_grammar[head] = list(set(new_grammar[head]))
    return dict(new_grammar)

# esta funcion elimina los simbolos inutiles de la gramatica
def remove_useless(grammar, start):
    # se determina el conjunto de simbolos alcanzables a partir del simbolo inicial
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
    # se determina el conjunto de simbolos productivos
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
    # se retorna la gramatica filtrando producciones con simbolos no validos
    return {h: [p for p in prods if all((not c.isupper()) or c in valid for c in p)]
            for h, prods in grammar.items() if h in valid}

# esta funcion convierte la gramatica a la forma normal de chomsky
def to_cnf(grammar, start):
    G = remove_unit(remove_epsilon(remove_useless(grammar, start), start), start)
    counters = {'X': 0}
    mapping = {}
    # mapa de letras usadas para simbolos temporales
    letter_mapping = {0: 'E', 1: 'F', 2: 'G', 3: 'H', 4: 'I', 5: 'J', 6: 'K'}
    cnf = defaultdict(list)
    for head, prods in G.items():
        for prod in prods:
            if prod != '*':
                if len(prod) > 1:
                    new_prod = []
                    # se convierte terminales en no terminales para cumplir cnf
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
    # se separan producciones con mas de 2 simbolos
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

# esta funcion convierte la gramatica a la forma normal de greibach
def to_gnf(grammar, start):
    # funcion auxiliar: devuelve un simbolo nuevo sin usar
    def get_fresh_symbol(used, candidates="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        for c in candidates:
            if c not in used:
                used.add(c)
                return c
        raise Exception("no hay simbolos frescos disponibles.")

    # -------------------------------
    # paso 1: eliminacion de epsilon
    # -------------------------------
    def remove_epsilon_local(gram, start):
        nullable = set()
        change = True
        while change:
            change = False
            for A, prods in gram.items():
                for prod in prods:
                    if prod == "*" or all(ch in nullable for ch in prod):
                        if A not in nullable:
                            nullable.add(A)
                            change = True
        new_gram = {}
        from itertools import product
        for A, prods in gram.items():
            new_set = set()
            for prod in prods:
                if prod == "*":
                    continue
                indices = [i for i, ch in enumerate(prod) if ch in nullable]
                for mask in product([0,1], repeat=len(indices)):
                    lst = list(prod)
                    for j, bit in enumerate(mask):
                        if bit:
                            lst[indices[j]] = ""
                    cand = "".join(lst)
                    if cand == "":
                        cand = "*"
                    new_set.add(cand)
            if A == start and "*" in gram.get(A, []):
                new_set.add("*")
            new_gram[A] = list(new_set)
        return new_gram

    # -------------------------------
    # paso 2: eliminacion de producciones unitarias
    # -------------------------------
    def remove_unit_local(gram):
        new_gram = {}
        for A in gram:
            new_prods = set()
            stack = [A]
            visited = {A}
            while stack:
                B = stack.pop()
                for prod in gram[B]:
                    if len(prod) == 1 and prod.isupper():
                        if prod not in visited:
                            visited.add(prod)
                            stack.append(prod)
                    else:
                        new_prods.add(prod)
            new_gram[A] = list(new_prods)
        return new_gram

    # -------------------------------
    # paso 3: eliminacion de simbolos inutiles
    # -------------------------------
    def remove_useless_local(gram, start):
        reachable = {start}
        change = True
        while change:
            change = False
            for A in list(reachable):
                for prod in gram.get(A, []):
                    for ch in prod:
                        if ch.isupper() and ch not in reachable:
                            reachable.add(ch)
                            change = True
        productive = set()
        change = True
        while change:
            change = False
            for A, prods in gram.items():
                for prod in prods:
                    if all((not c.isupper()) or c in productive for c in prod):
                        if A not in productive:
                            productive.add(A)
                            change = True
        valid = reachable & productive
        return {A: [p for p in prods if all((not c.isupper()) or c in valid for c in p)]
                for A, prods in gram.items() if A in valid}

    # -------------------------------
    # paso 4: eliminacion de recursividad izquierda inmediata
    # se separa para cada no terminal A
    # -------------------------------
    def remove_left_rec_all(gram):
        new_gram = {}
        used = set(gram.keys())
        for A in gram:
            rec = []
            nonrec = []
            for prod in gram[A]:
                if prod != "*" and prod and prod[0] == A:
                    rec.append(prod[1:])
                else:
                    nonrec.append(prod)
            if rec:
                X = get_fresh_symbol(used)  # se genera un nuevo no terminal
                new_rules_A = nonrec + [beta + X for beta in nonrec if beta != "*"]
                new_rules_X = rec + [gamma + X for gamma in rec]
                new_gram[A] = list(set(new_rules_A))
                new_gram[X] = list(set(new_rules_X))
            else:
                new_gram[A] = gram[A]
        return new_gram

    # -------------------------------
    # paso 5: expansion recursiva para que cada produccion inicie con un terminal
    # -------------------------------
    def expand_prod(prod, gram):
        if prod == "*" or (prod and prod[0].islower()):
            return {prod}
        results = set()
        B = prod[0]
        suffix = prod[1:]
        for gamma in gram.get(B, []):
            tails = expand_prod(suffix, gram) if suffix else {""}
            for t in tails:
                results.add(gamma + t)
        return results

    # -------------------------------
    # paso 6: correccion de producciones con terminales en posiciones posteriores
    # -------------------------------
    def fix_trailing_prods(gram):
        used = set(gram.keys())
        mapping = {}  # mapea terminal a nuevo no terminal
        def get_fresh(mapping):
            return get_fresh_symbol(used)
        fixed_gram = {}
        for A, prods in gram.items():
            fixed = set()
            for prod in prods:
                if prod == "*" or len(prod) == 1:
                    fixed.add(prod)
                else:
                    new_prod = prod[0]  # se conserva el primer simbolo
                    for ch in prod[1:]:
                        if ch.islower():
                            if ch not in mapping:
                                mapping[ch] = get_fresh(mapping)
                            new_prod += mapping[ch]
                        else:
                            new_prod += ch
                    fixed.add(new_prod)
            fixed_gram[A] = list(fixed)
        # agregar reglas para los nuevos no terminales
        for t, X in mapping.items():
            fixed_gram[X] = [t]
        return fixed_gram

    # aplicacion secuencial de los pasos para convertir a gnf
    gram1 = remove_epsilon_local(grammar, start)
    gram2 = remove_unit_local(gram1)
    gram3 = remove_useless_local(gram2, start)
    gram4 = remove_left_rec_all(gram3)
    expanded = {}
    for A, prods in gram4.items():
        exp_set = set()
        for prod in prods:
            exp_set |= expand_prod(prod, gram4)
        expanded[A] = list(exp_set)
    final = fix_trailing_prods(expanded)
    return final

# funcion para mostrar una gramatica en un contenedor streamlit
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

# funcion principal que ejecuta la aplicacion streamlit
def main():
    st.set_page_config(page_title="conversor de gramatica", page_icon="🔤", layout="wide")
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
    st.markdown('<h1 class="main-title">conversor de gramatica</h1>', unsafe_allow_html=True)
    with st.sidebar:
        st.header("acerca de las conversiones")
        st.markdown("""
        ### gramatica bien formada
        - sin producciones epsilon (*)
        - sin producciones unitarias (a->b)
        - sin simbolos inutiles
        """)
        st.markdown("""
        ### forma normal de chomsky
        todas las producciones tienen la forma:
        - a -> bc (donde b y c son no terminales)
        - a -> a (donde a es terminal)
        """)
        st.markdown("""
        ### forma normal de greibach
        todas las producciones tienen la forma:
        - a -> aα (donde a es terminal y α es una cadena de no terminales)
        """)
        st.markdown("""
        ### ejemplo de gramatica
        s -> bA | aB
        A -> bAA | aS | a
        B -> aBB | bS | b
        """)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-header"><h3>ingresa tu gramatica</h3></div>', unsafe_allow_html=True)
        st.markdown("""
        introduce la gramatica usando:
        - `->` para las producciones
        - `|` para separar alternativas
        - `*` para representar epsilon/vacio
        """)
        input_grammar = st.text_area("gramatica:", height=200, placeholder="S -> bA | aB\nA -> bAA | aS | a\nB -> aBB | bS | b")
        start_symbol = st.text_input("simbolo inicial:", value='S')
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        ### instrucciones
        1. escribe cada produccion en una linea separada
        2. usa mayusculas para no terminales
        3. usa minusculas para terminales
        4. define el simbolo inicial
        5. da clic en "convertir"
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        convert_button = st.button("convertir", type="primary", use_container_width=True)
        if st.button("limpiar", type="secondary", use_container_width=True):
            st.session_state.input_grammar = ""
            st.session_state.start_symbol = "S"
            st.experimental_rerun()
    if convert_button and input_grammar:
        try:
            # se parsea la gramatica del texto ingresado
            grammar = parse_grammar(input_grammar)
            st.markdown('<div class="section-header"><h3>gramatica original</h3></div>', unsafe_allow_html=True)
            with st.expander("ver gramatica original", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(grammar, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>gramatica bien formada</h3></div>', unsafe_allow_html=True)
            well_formed = remove_useless(remove_unit(remove_epsilon(grammar, start_symbol), start_symbol), start_symbol)
            with st.expander("ver gramatica bien formada", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(well_formed, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>forma normal de chomsky</h3></div>', unsafe_allow_html=True)
            cnf = to_cnf(grammar, start_symbol)
            with st.expander("ver forma normal de chomsky", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(cnf, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>forma normal de greibach</h3></div>', unsafe_allow_html=True)
            gnf = to_gnf(grammar, start_symbol)
            with st.expander("ver forma normal de greibach", expanded=True):
                st.markdown('<div class="grammar-container">', unsafe_allow_html=True)
                display_grammar(gnf, st)
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header"><h3>descargar resultados</h3></div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            # funcion para convertir la gramatica a texto
            def grammar_to_text(grammar):
                result = []
                for head, prods in grammar.items():
                    result.append(f"{head} -> {' | '.join(prods)}")
                return "\n".join(result)
            with col1:
                st.download_button(label="descargar bien formada", data=grammar_to_text(well_formed), file_name="gramatica_bien_formada.txt", mime="text/plain")
            with col2:
                st.download_button(label="descargar chomsky", data=grammar_to_text(cnf), file_name="forma_normal_chomsky.txt", mime="text/plain")
            with col3:
                st.download_button(label="descargar greibach", data=grammar_to_text(gnf), file_name="forma_normal_greibach.txt", mime="text/plain")
        except Exception as e:
            st.error(f"error al procesar la gramatica: {str(e)}")
            st.error("asegurese de que la gramatica este correctamente formateada.")
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; opacity: 0.7;'>
            conversor de gramatica © 2025
        </div>
    """, unsafe_allow_html=True)

main()