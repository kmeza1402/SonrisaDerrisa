"""Genera los 5 diagramas del modelo (Crow's Foot, Classic/Chen, Connect to
Columns, UML e IDEF1X) como archivos .dot editables y exporta PNG y PDF.
Uso: python generar_diagramas.py   (requiere Graphviz: dot en el PATH o en
C:\\Program Files\\Graphviz\\bin)"""
import os
import shutil
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
DOT = shutil.which("dot") or r"C:\Program Files\Graphviz\bin\dot.exe"

# (columna, tipo, PK, FK, nulo)
T = {
    "especialidad": [("id_especialidad", "INT", 1, 0, 0), ("nombre", "VARCHAR(50)", 0, 0, 0)],
    "paciente": [("id_paciente", "INT", 1, 0, 0), ("nombre", "VARCHAR(50)", 0, 0, 0), ("apellidos", "VARCHAR(80)", 0, 0, 0),
                 ("fecha_nacimiento", "DATE", 0, 0, 1), ("telefono", "VARCHAR(15)", 0, 0, 0),
                 ("correo", "VARCHAR(100)", 0, 0, 1), ("fecha_registro", "DATE", 0, 0, 0)],
    "historial_clinico": [("id_historial", "INT", 1, 0, 0), ("id_paciente", "INT", 0, 1, 0),
                          ("alergias", "VARCHAR(200)", 0, 0, 1), ("enfermedades", "VARCHAR(200)", 0, 0, 1),
                          ("medicamentos", "VARCHAR(200)", 0, 0, 1), ("fecha_actualizacion", "DATE", 0, 0, 0)],
    "dentista": [("id_dentista", "INT", 1, 0, 0), ("nombre", "VARCHAR(50)", 0, 0, 0), ("apellidos", "VARCHAR(80)", 0, 0, 0),
                 ("cedula", "VARCHAR(20)", 0, 0, 0), ("telefono", "VARCHAR(15)", 0, 0, 1), ("id_especialidad", "INT", 0, 1, 0)],
    "tratamiento": [("id_tratamiento", "INT", 1, 0, 0), ("nombre", "VARCHAR(60)", 0, 0, 0),
                    ("descripcion", "VARCHAR(200)", 0, 0, 1), ("precio_base", "DECIMAL(10,2)", 0, 0, 0)],
    "cita": [("id_cita", "INT", 1, 0, 0), ("id_paciente", "INT", 0, 1, 0), ("id_dentista", "INT", 0, 1, 0),
             ("fecha", "DATE", 0, 0, 0), ("hora", "TIME", 0, 0, 0), ("motivo", "VARCHAR(150)", 0, 0, 1),
             ("estado", "VARCHAR(15)", 0, 0, 0)],
    "detalle_cita": [("id_detalle", "INT", 1, 0, 0), ("id_cita", "INT", 0, 1, 0), ("id_tratamiento", "INT", 0, 1, 0),
                     ("diente", "VARCHAR(5)", 0, 0, 1), ("precio_aplicado", "DECIMAL(10,2)", 0, 0, 0)],
    "pago": [("id_pago", "INT", 1, 0, 0), ("id_cita", "INT", 0, 1, 0), ("fecha_pago", "DATE", 0, 0, 0),
             ("monto", "DECIMAL(10,2)", 0, 0, 0), ("metodo_pago", "VARCHAR(15)", 0, 0, 0)],
}

# (padre, hijo, columna FK, cardinalidad padre, cardinalidad hijo, verbo)
# card: '1' = exactamente uno, '01' = cero o uno, '0N' = cero o muchos, '1N' = uno o muchos
R = [
    ("especialidad", "dentista", "id_especialidad", "1", "0N", "agrupa"),
    ("paciente", "historial_clinico", "id_paciente", "1", "01", "tiene"),
    ("paciente", "cita", "id_paciente", "1", "0N", "solicita"),
    ("dentista", "cita", "id_dentista", "1", "0N", "atiende"),
    ("cita", "detalle_cita", "id_cita", "1", "0N", "incluye"),
    ("tratamiento", "detalle_cita", "id_tratamiento", "1", "0N", "se aplica en"),
    ("cita", "pago", "id_cita", "1", "0N", "se liquida con"),
]

DEBILES = {"historial_clinico"}
ASOCIATIVAS = {"detalle_cita"}
VERDE = "#0f6e8c"
FUENTE = 'fontname="Helvetica"'


def cabecera(nombre, rankdir="LR", extra=""):
    return (f'digraph {nombre} {{\n  graph [rankdir={rankdir}, splines=ortho, nodesep=0.6, ranksep=1.1, '
            f'pad=0.3, {FUENTE}, labelloc=t, fontsize=20{extra}];\n'
            f'  node [{FUENTE}, fontsize=11];\n  edge [{FUENTE}, fontsize=10];\n')


def escribir(nombre, texto):
    ruta = os.path.join(AQUI, nombre + ".dot")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    for fmt in ("png", "pdf"):
        subprocess.run([DOT, f"-T{fmt}", "-Gdpi=130", ruta, "-o", os.path.join(AQUI, f"{nombre}.{fmt}")], check=True)
    print("ok", nombre)


# ---------------------------------------------------------------- Crow's Foot
def crows_foot():
    s = cabecera("crows_foot", extra=', label="DER - Notación Crow\'s Foot"')
    for t, cols in T.items():
        filas = "".join(
            f'<TR><TD ALIGN="LEFT">{"<B>PK</B>" if pk else ("FK" if fk else "")}</TD>'
            f'<TD ALIGN="LEFT">{"<U>" + c + "</U>" if pk else c}</TD><TD ALIGN="LEFT"><FONT COLOR="#555555">{ty}</FONT></TD></TR>'
            for c, ty, pk, fk, nu in cols)
        s += (f'  {t} [shape=plain, label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">'
              f'<TR><TD COLSPAN="3" BGCOLOR="{VERDE}"><FONT COLOR="white"><B>{t}</B></FONT></TD></TR>{filas}</TABLE>>];\n')
    simbolo = {"1": "teetee", "01": "teeodot", "0N": "crowodot", "1N": "crowtee"}
    for p, h, fk, cp, ch, verbo in R:
        s += f'  {p} -> {h} [dir=both, arrowtail={simbolo[cp]}, arrowhead={simbolo[ch]}, xlabel="{verbo}"];\n'
    escribir("01_crows_foot", s + "}\n")


# ---------------------------------------------------------------- Classic (Chen)
def chen():
    s = ('graph chen {\n  graph [layout=neato, overlap=false, sep="+12", splines=true, pad=0.4, '
         f'{FUENTE}, labelloc=t, fontsize=20, label="DER - Notación Classic (Chen)"];\n'
         f'  node [{FUENTE}, fontsize=10];\n  edge [{FUENTE}, fontsize=11];\n')
    for t, cols in T.items():
        forma = 'shape=box, peripheries=2' if t in DEBILES else (
            'shape=box, style="rounded,filled", fillcolor="#e8f4f1"' if t in ASOCIATIVAS else 'shape=box, style=filled, fillcolor="#e8f4f1"')
        s += f'  {t} [{forma}, fontsize=13, label="{t}"];\n'
        for c, ty, pk, fk, nu in cols:
            if fk:
                continue  # en Chen las FK se representan con la relación, no como atributo
            etq = f"<<U>{c}</U>>" if pk else f'"{c}"'
            borde = ', style=dashed' if nu else ''
            s += f'  "{t}.{c}" [shape=ellipse, label={etq}{borde}];\n  {t} -- "{t}.{c}";\n'
    txt = {"1": "1", "01": "1", "0N": "N", "1N": "N"}
    for p, h, fk, cp, ch, verbo in R:
        rel = f"r_{p}_{h}"
        doble = ', peripheries=2' if h in DEBILES else ''
        s += f'  {rel} [shape=diamond, style=filled, fillcolor="#fff2cc", label="{verbo}"{doble}];\n'
        total_h = ch in ("1", "1N")
        total_p = cp in ("1", "1N")
        s += f'  {p} -- {rel} [label="{txt[cp]}"{", penwidth=2.5" if total_p and False else ""}];\n'
        s += f'  {rel} -- {h} [label="{txt[ch]}"{", color=\"black:white:black\"" if total_h else ""}];\n'
    escribir("02_classic_chen", s + "}\n")


# ---------------------------------------------------------------- Connect to Columns
def connect_columns():
    s = cabecera("connect_columns", extra=', label="Modelo relacional - Notación Connect to Columns", splines=true')
    for t, cols in T.items():
        filas = "".join(
            f'<TR><TD PORT="{c}" ALIGN="LEFT" BGCOLOR="{"#d9ead3" if pk else ("#fce5cd" if fk else "white")}">'
            f'{"🔑 " if False else ""}{c}{" (PK)" if pk else ""}{" (FK)" if fk else ""}</TD></TR>'
            for c, ty, pk, fk, nu in cols)
        s += (f'  {t} [shape=plain, label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">'
              f'<TR><TD BGCOLOR="{VERDE}"><FONT COLOR="white"><B>{t}</B></FONT></TD></TR>{filas}</TABLE>>];\n')
    for p, h, fk, cp, ch, verbo in R:
        pk = T[p][0][0]
        s += f'  {p}:{pk}:e -> {h}:{fk}:w [dir=back, arrowtail=normal, color="#3c78d8"];\n'
    escribir("03_connect_to_columns", s.replace("splines=ortho, ", "") + "}\n")


# ---------------------------------------------------------------- UML
def uml():
    s = cabecera("uml", extra=', label="Diagrama de clases - Notación UML"')
    for t, cols in T.items():
        estereotipo = "&laquo;asociativa&raquo;<BR/>" if t in ASOCIATIVAS else ("&laquo;débil&raquo;<BR/>" if t in DEBILES else "")
        attrs = "<BR ALIGN=\"LEFT\"/>".join(
            f'{"+" if pk else "-"} {c} : {ty}{" {PK}" if pk else ""}{" {FK}" if fk else ""}{" [0..1]" if nu else ""}'
            for c, ty, pk, fk, nu in cols) + '<BR ALIGN="LEFT"/>'
        s += (f'  {t} [shape=plain, label=<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5">'
              f'<TR><TD BGCOLOR="#fff2cc">{estereotipo}<B>{t.capitalize()}</B></TD></TR>'
              f'<TR><TD ALIGN="LEFT">{attrs}</TD></TR><TR><TD> </TD></TR></TABLE>>];\n')
    mult = {"1": "1", "01": "0..1", "0N": "0..*", "1N": "1..*"}
    for p, h, fk, cp, ch, verbo in R:
        s += f'  {p} -> {h} [arrowhead=none, taillabel="{mult[cp]}", headlabel="{mult[ch]}", label="{verbo}"];\n'
    escribir("04_uml", s.replace("splines=ortho, ", "splines=polyline, ") + "}\n")


# ---------------------------------------------------------------- IDEF1X
def idef1x():
    s = cabecera("idef1x", extra=', label="Modelo - Notación IDEF1X"')
    for t, cols in T.items():
        pk = "<BR ALIGN=\"LEFT\"/>".join(c for c, ty, p, f, n in cols if p) + '<BR ALIGN="LEFT"/>'
        resto = "<BR ALIGN=\"LEFT\"/>".join(f'{c}{" (FK)" if f else ""}' for c, ty, p, f, n in cols if not p) + '<BR ALIGN="LEFT"/>'
        s += (f'  {t} [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">'
              f'<TR><TD ALIGN="LEFT"><B>{t}</B></TD></TR><TR><TD><TABLE BORDER="1" CELLBORDER="0" '
              f'CELLSPACING="0" CELLPADDING="5" SIDES="LTRB"><TR><TD ALIGN="LEFT" SIDES="B" BORDER="1">{pk}</TD></TR>'
              f'<TR><TD ALIGN="LEFT">{resto}</TD></TR></TABLE></TD></TR></TABLE>>];\n')
    # Todas las relaciones son no identificadoras (la FK no forma parte de la PK) -> línea punteada.
    # Punto negro en el extremo hijo; Z = cero o uno, P = uno o más, sin letra = cero o más.
    letra = {"0N": "", "1N": "P", "01": "Z", "1": ""}
    for p, h, fk, cp, ch, verbo in R:
        rombo = ", arrowtail=odiamond" if cp == "01" else ", arrowtail=none"
        s += (f'  {p} -> {h} [style=dashed, dir=both, arrowhead=dot{rombo}, '
              f'headlabel="{letra[ch]}", label="{verbo}"];\n')
    escribir("05_idef1x", s.replace("splines=ortho, ", "splines=polyline, ") + "}\n")


if __name__ == "__main__":
    crows_foot()
    chen()
    connect_columns()
    uml()
    idef1x()
