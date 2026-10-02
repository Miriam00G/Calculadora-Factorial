import re
import string
from itertools import combinations
from math import comb

from sympy import Mul, combsimp, factorial, fraction, latex, simplify, sympify
from sympy.parsing.sympy_parser import (
    convert_xor,
    factorial_notation,
    parse_expr,
    standard_transformations,
)

TRANS = standard_transformations + (factorial_notation, convert_xor)

# C(5,2)  |  c(n, r)  |  C( 10 , 3 )
PATRON_C = re.compile(r"^\s*[Cc]\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)\s*$")

MAX_LETRAS = 26
MAX_COMBOS = 600


def parsear_valores(texto):
    """'n=10, k=2' -> {n: 10, k: 2}"""
    valores = {}
    if not texto or not texto.strip():
        return valores
    for par in texto.split(","):
        if "=" not in par:
            raise ValueError("Los valores deben tener el formato n=6, r=3")
        nombre, valor = par.split("=", 1)
        valores[sympify(nombre.strip())] = sympify(valor.strip())
    return valores


def es_entero(x):
    return getattr(x, "is_Integer", False)


def paso_expansion(expr):
    """Si hay un factorial arriba y uno abajo,
    muestra cómo se expande el mayor.
    """
    num, den = fraction(expr)
    if not (num.func == factorial and den.func == factorial):
        return None
    a, b = num.args[0], den.args[0]
    d = simplify(b - a)
    if not d.is_Integer or d == 0:
        return None
    k = abs(int(d))
    grande, chico = (b, a) if d > 0 else (a, b)
    factores = [grande - i for i in range(k)]
    producto = latex(Mul(*factores, evaluate=False))
    return f"({latex(grande)})! = {producto}\\cdot ({latex(chico)})!"


def resolver_factorial(texto, valores_texto=""):
    pasos = []
    original = parse_expr(texto, transformations=TRANS, evaluate=False)
    expr = parse_expr(texto, transformations=TRANS)

    pasos.append(("Expresión original", latex(original)))

    exp = paso_expansion(expr)
    if exp:
        pasos.append(("Expansión del factorial mayor", exp))

    simplificada = combsimp(expr)
    pasos.append(("Expresión simplificada", latex(simplificada)))

    valores = parsear_valores(valores_texto)
    if valores:
        sustituida = simplificada.subs(valores)
        pasos.append(("Reemplazando " + valores_texto, latex(sustituida)))
        pasos.append(("Resultado final", latex(simplify(sustituida))))

    return pasos


def resolver_combinacion(texto, valores_texto=""):
    m = PATRON_C.match(texto)
    if not m:
        raise ValueError("Usa el formato C(n, r). Ejemplo: C(6, 3)")

    n = sympify(m.group(1))
    r = sympify(m.group(2))
    valores = parsear_valores(valores_texto)

    pasos = []
    pasos.append(
        (
            "Fórmula de combinación",
            r"C(n,r)=\frac{n!}{r!\,(n-r)!}",
        )
    )

    n_val = n.subs(valores) if valores else n
    r_val = r.subs(valores) if valores else r

    if not (es_entero(n_val) and es_entero(r_val)):
        general = (
            r"\frac{(" + latex(n_val) + r")!}{(" + latex(r_val)
            + r")!\,(" + latex(n_val - r_val) + r")!}"
        )
        pasos.append(("Sustituyendo", general))
        return pasos, None

    n_i, r_i = int(n_val), int(r_val)
    if n_i < 0 or r_i < 0:
        raise ValueError("n y r deben ser números enteros no negativos.")
    if r_i > n_i:
        raise ValueError("r no puede ser mayor que n.")

    pasos.append(
        (
            "Sustituyendo",
            rf"C({n_i},{r_i})=\frac{{{n_i}!}}{{{r_i}!\,({n_i}-{r_i})!}}",
        )
    )
    pasos.append(
        (
            "Resolviendo la resta",
            rf"C({n_i},{r_i})=\frac{{{n_i}!}}{{{r_i}!\cdot {n_i - r_i}!}}",
        )
    )

    total = comb(n_i, r_i)
    pasos.append(("Resultado final", rf"C({n_i},{r_i})={total}"))

    grafico = None
    if n_i <= MAX_LETRAS and total <= MAX_COMBOS:
        letras = string.ascii_uppercase[:n_i]
        grafico = {
            "n": n_i,
            "r": r_i,
            "total": total,
            "combinaciones": [list(c) for c in combinations(letras, r_i)],
        }
    return pasos, grafico


def procesar(modo, texto, valores_texto=""):
    """
    Devuelve (modo_final, pasos, grafico).
    Si el texto tiene forma C(n, r) se trata como combinación aunque la
    pestaña activa sea Factoriales (y al revés).
    """
    texto = (texto or "").strip()
    if not texto:
        raise ValueError("Escribe una expresión.")

    if PATRON_C.match(texto):
        pasos, grafico = resolver_combinacion(texto, valores_texto)
        return "combinacion", pasos, grafico

    if modo == "combinacion":
        raise ValueError(
            "En Combinaciones usa el formato C(n, r). "
            "Ejemplo: C(6, 3)"
        )

    return "factorial", resolver_factorial(texto, valores_texto), None
