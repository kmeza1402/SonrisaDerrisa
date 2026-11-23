"""Genera Reporte.pdf del Proyecto Final (Sonrisa Derrisa) y Pruebas/matriz_pruebas.csv.
Uso: python generar_reporte.py   (requiere reportlab)"""
import csv
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

F = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("TNR", F + r"\times.ttf"))
pdfmetrics.registerFont(TTFont("TNR-B", F + r"\timesbd.ttf"))
pdfmetrics.registerFont(TTFont("TNR-I", F + r"\timesi.ttf"))
pdfmetrics.registerFont(TTFont("MONO", F + r"\consola.ttf"))
pdfmetrics.registerFont(TTFont("SYM", F + r"\seguisym.ttf"))
registerFontFamily("TNR", normal="TNR", bold="TNR-B", italic="TNR-I", boldItalic="TNR-B")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL = os.path.join(RAIZ, "Sql")
DIAG = os.path.join(RAIZ, "Diagramas")
CAP = os.path.join(RAIZ, "Pruebas", "capturas")
RES = os.path.join(RAIZ, "Pruebas", "resultados_sql")
LOGOS = r"C:\Users\jaime\Documents\Evidencias_P7_DBA\logos"
SALIDA = os.path.join(RAIZ, "Reporte.pdf")

W, H = A4
M = 72
ANCHO = W - 2 * M

# ------------------------------------------------------------------ estilos
c14 = ParagraphStyle("c14", fontName="TNR-B", fontSize=14, leading=18, alignment=TA_CENTER)
c13 = ParagraphStyle("c13", fontName="TNR", fontSize=13, leading=17, alignment=TA_CENTER)
l12 = ParagraphStyle("l12", fontName="TNR", fontSize=12, leading=16, alignment=TA_LEFT)
TX = ParagraphStyle("tx", fontName="TNR", fontSize=12, leading=16, alignment=TA_JUSTIFY, spaceAfter=6)
BUL = ParagraphStyle("bul", parent=TX, leftIndent=16, bulletIndent=4, spaceAfter=2)
H1 = ParagraphStyle("h1", fontName="TNR-B", fontSize=16, leading=20, spaceBefore=6, spaceAfter=10)
H2 = ParagraphStyle("h2", fontName="TNR-B", fontSize=13, leading=17, spaceBefore=10, spaceAfter=6)
CEL = ParagraphStyle("cel", fontName="TNR", fontSize=9, leading=11)
CELB = ParagraphStyle("celb", fontName="TNR-B", fontSize=9, leading=11)
PIE = ParagraphStyle("pie", fontName="TNR-I", fontSize=10, leading=12, alignment=TA_CENTER, spaceAfter=10)
ALG = ParagraphStyle("alg", fontName="SYM", fontSize=11, leading=16, leftIndent=12, spaceAfter=4)
TOC1 = ParagraphStyle("toc1", fontName="TNR", fontSize=12, leading=18)
TOC2 = ParagraphStyle("toc2", fontName="TNR", fontSize=11, leading=15, leftIndent=18)


class Doc(BaseDocTemplate):
    def __init__(self, ruta):
        super().__init__(ruta, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
                         title="Proyecto Final - Sonrisa Derrisa", author="Equipo Bombones")
        marco = Frame(M, M, ANCHO, H - 2 * M, id="f")
        self.addPageTemplates([PageTemplate("p", [marco], onPage=self.decorar)])

    def decorar(self, cv, doc):
        if doc.page == 1:
            top = H - M
            cv.drawImage(LOGOS + r"\logo_izq.png", M - 42.75, top - 116.25, 116.25, 116.25, mask="auto")
            cv.drawImage(LOGOS + r"\logo_der.jpg", M + 401.25, top - 108.6, 79.875, 108.6)
        else:
            cv.setFont("TNR", 10)
            cv.drawCentredString(W / 2, 40, str(doc.page))

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ("h1", "h2"):
            nivel = 0 if f.style.name == "h1" else 1
            texto = f.getPlainText()
            clave = "s%d" % id(f)
            self.canv.bookmarkPage(clave)
            self.notify("TOCEntry", (nivel, texto, self.page, clave))


S = []
sp = lambda h=12: Spacer(1, h)
p = lambda t: S.append(Paragraph(t, TX))
h1 = lambda t: S.append(Paragraph(t, H1))
h2 = lambda t: S.append(Paragraph(t, H2))


def bullets(items):
    for it in items:
        S.append(Paragraph(it, BUL, bulletText="•"))


def tabla(filas, anchos, encabezado=True, fuente=9):
    est = ParagraphStyle("t", parent=CEL, fontSize=fuente, leading=fuente + 2)
    estb = ParagraphStyle("tb", parent=CELB, fontSize=fuente, leading=fuente + 2)
    datos = [[Paragraph(str(c), estb if (encabezado and i == 0) else est) for c in fila]
             for i, fila in enumerate(filas)]
    t = Table(datos, colWidths=anchos, repeatRows=1 if encabezado else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if encabezado:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe9ef")))
    t.setStyle(TableStyle(st))
    return t


def codigo(texto, tam=None):
    lineas = texto.rstrip("\n").split("\n")
    largo = max(len(x) for x in lineas) or 1
    tam = tam or max(5.2, min(9, ANCHO / (largo * 0.55)))
    est = ParagraphStyle("code", fontName="MONO", fontSize=tam, leading=tam * 1.25,
                         backColor=colors.HexColor("#f4f6f8"), borderPadding=4, spaceAfter=8, spaceBefore=2)
    return Preformatted(texto.rstrip("\n"), est)


def imagen(ruta, pie, ancho=ANCHO, alto_max=8.2 * inch):
    img = Image(ruta)
    r = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = ancho, ancho * r
    if img.drawHeight > alto_max:
        img.drawHeight, img.drawWidth = alto_max, alto_max / r
    S.append(KeepTogether([img, Paragraph(pie, PIE)]))


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def tablas_resultado(ruta):
    """Separa la salida --table de mysql en bloques (borde, encabezado, borde, filas, borde)."""
    bloques, actual, bordes = [], [], 0
    for ln in leer(ruta).splitlines():
        if not ln.strip():
            continue
        actual.append(ln)
        if ln.startswith("+"):
            bordes += 1
            if bordes == 3:
                bloques.append("\n".join(actual))
                actual, bordes = [], 0
    return bloques


# ================================================================== PORTADA
S += [sp(8), Paragraph("Universidad Autónoma de Baja California", c14),
      Paragraph("Facultad de Ingeniería, Arquitectura y Diseño.", c14), sp(34),
      Paragraph("Ingenieria en Software y Tecnologias Emergentes", c13), sp(51),
      Paragraph("Bases de datos", c13), sp(34),
      Paragraph("Meza Espinoza Kevin Andre [379140]", c13),
      Paragraph("Zazueta Medrano Aidan [379479]", c13),
      Paragraph("Jaime Mascareño Carlos Alberto [377175]", c13), sp(34),
      Paragraph("Grupo 952 · Equipo Bombones", c13), sp(34),
      Paragraph("Proyecto Final: Sonrisa Derrisa", c13),
      Paragraph("Sistema de citas, tratamientos y pagos para clínica dental", c13), sp(34),
      Paragraph("Profesora:", c13), Paragraph("Julia Guadalupe Juarez Hernandez", c13), sp(80),
      Paragraph("Ensenada, B. C.  21 de Noviembre del 2026.", l12), PageBreak()]

# ================================================================== ÍNDICE
S.append(Paragraph("Índice", H1.clone("idx")))
toc = TableOfContents()
toc.levelStyles = [TOC1, TOC2]
toc.dotsMinLevel = 0
S += [toc, PageBreak()]

# ================================================================== 1 INTRODUCCIÓN
h1("1. Introducción")
p("<b>Sonrisa Derrisa</b> es una clínica dental pequeña que agendaba sus citas en una libreta y por WhatsApp. "
  "Esto provocaba citas empalmadas para un mismo dentista, pérdida de antecedentes médicos importantes "
  "(alergias, enfermedades, medicamentos) y saldos de tratamientos calculados a mano.")
p("Este proyecto diseña e implementa una base de datos relacional en MySQL 8 y una aplicación web "
  "(ASP.NET Core Razor Pages, arquitectura en capas) para administrar pacientes, historial clínico, dentistas, "
  "citas, tratamientos y pagos en abonos. Las reglas críticas del negocio se garantizan en la propia base de "
  "datos mediante restricciones, triggers, una función y procedimientos almacenados, y la aplicación las "
  "presenta al usuario como mensajes claros.")
p("<b>Objetivo general:</b> construir un sistema de información confiable que evite empalmes de agenda, "
  "conserve el historial clínico de cada paciente y calcule automáticamente el saldo de cada cita.")

# ================================================================== 2 ANÁLISIS
h1("2. Etapa 1: Análisis del problema")
h2("2.1 Usuarios y alcance")
bullets(["<b>Recepcionista:</b> registra pacientes y su historial, agenda, reprograma o cancela citas y "
         "registra abonos.",
         "<b>Dentista:</b> consulta su agenda, ve las alergias del paciente y registra el tratamiento realizado.",
         "<b>Paciente:</b> es la persona atendida; no usa el sistema directamente.",
         "<b>Fuera de alcance:</b> facturación electrónica, inventario de materiales y recordatorios automáticos."])
h2("2.2 Reglas de negocio")
RN = [
    ("RN1", "Todo paciente debe registrar nombre, apellidos y teléfono (10 dígitos).", "NOT NULL, CHECK ck_paciente_telefono"),
    ("RN2", "Cada paciente tiene un único historial clínico, que debe existir antes de su primera cita.", "UNIQUE uq_historial_paciente, trigger trg_cita_bi"),
    ("RN3", "Cada dentista pertenece a una sola especialidad y su cédula profesional es única.", "FK fk_dentista_especialidad, UNIQUE uq_dentista_cedula"),
    ("RN4", "Una cita requiere paciente, dentista, fecha y hora.", "NOT NULL + FK"),
    ("RN5", "Un dentista no puede tener dos citas activas (no canceladas) a la misma fecha y hora.", "Triggers trg_cita_bi y trg_cita_bu"),
    ("RN6", "El estado de una cita sólo puede ser Programada, Atendida o Cancelada.", "CHECK ck_cita_estado, DEFAULT 'Programada'"),
    ("RN7", "Sólo las citas atendidas pueden tener tratamientos registrados.", "Trigger trg_detalle_cita_bi"),
    ("RN8", "En una cita se pueden aplicar uno o varios tratamientos (incluso por diente).", "Tabla detalle_cita, UNIQUE (cita, tratamiento, diente)"),
    ("RN9", "El precio aplicado puede diferir del precio base (descuentos) pero no ser negativo.", "CHECK ck_detalle_precio"),
    ("RN10", "Una cita puede pagarse en varios abonos con método Efectivo, Tarjeta o Transferencia.", "Tabla pago, CHECK ck_pago_metodo"),
    ("RN11", "Cada abono debe ser mayor a cero y la suma de abonos no puede exceder el total de la cita.", "CHECK ck_pago_monto, trigger trg_pago_bi"),
    ("RN12", "Saldo de una cita = suma de precios aplicados − suma de pagos.", "Función fn_saldo_cita, vista vw_saldo_citas"),
]
S.append(tabla([("ID", "Regla", "Implementación")] + RN, [36, 255, 160]))
h2("2.3 Requerimientos funcionales")
RF = [
    ("RF01", "Registrar, editar y eliminar pacientes capturando su historial clínico en el mismo formulario."),
    ("RF02", "Buscar pacientes por nombre o teléfono."),
    ("RF03", "Registrar, editar y eliminar dentistas con su especialidad."),
    ("RF04", "Filtrar dentistas por nombre, cédula o especialidad."),
    ("RF05", "Agendar citas validando historial clínico (RN2) y empalmes (RN5)."),
    ("RF06", "Reprogramar una cita programada."),
    ("RF07", "Cancelar una cita programada liberando el horario."),
    ("RF08", "Atender una cita: cambiar estado, registrar tratamiento y abono inicial en una sola transacción."),
    ("RF09", "Registrar abonos posteriores sin exceder el saldo (RN11)."),
    ("RF10", "Consultar la agenda filtrando por rango de fechas, dentista, estado y paciente."),
    ("RF11", "Mostrar las alergias del paciente en la agenda y al atender."),
    ("RF12", "Generar el reporte de saldos por cita con totales generales."),
    ("RF13", "Mostrar mensajes de confirmación, de error y de estado vacío."),
]
S.append(tabla([("ID", "Requerimiento")] + RF, [40, 411]))
h2("2.4 Requerimientos no funcionales")
bullets(["Integridad: las reglas críticas se validan en la base de datos, no sólo en la interfaz.",
         "Seguridad: la aplicación usa un usuario de MySQL con privilegios mínimos (SELECT, INSERT, UPDATE, "
         "DELETE, EXECUTE) y la cadena de conexión se guarda en User Secrets, fuera del repositorio.",
         "Reproducibilidad: la base completa se reconstruye ejecutando los scripts 01 a 04.",
         "Usabilidad: interfaz en español, responsiva (Bootstrap) y con mensajes comprensibles."])

# ================================================================== 3 ARQUITECTURA
h1("3. Etapa 2: Arquitectura del sistema")
p("Se eligió una arquitectura en capas. Cada capa sólo depende de la inmediata inferior:")
S.append(tabla([("Capa", "Proyecto", "Responsabilidad"),
                ("Presentación", "SonrisaDerrisa.Web", "Páginas Razor, validación de formularios (DataAnnotations), mensajes TempData."),
                ("Negocio", "SonrisaDerrisa.Negocios", "Validaciones de aplicación y traducción de errores MySQL (1644, 1062, 1451/1217, 3819) a mensajes."),
                ("Datos", "SonrisaDerrisa.Datos", "Consultas parametrizadas con MySql.Data, transacción paciente-historial, llamada a sp_atender_cita."),
                ("Entidades", "SonrisaDerrisa.Entidades", "Clases Paciente, Dentista, Cita, AgendaItem, SaldoCita."),
                ("Base de datos", "MySQL 8 sonrisa_derrisa", "Tablas, restricciones, vistas, triggers, función y procedimientos.")],
               [72, 120, 259]))
S.append(sp(6))
S.append(codigo("Navegador ──HTTP──► SonrisaDerrisa.Web (Razor Pages)\n"
                "                          │\n"
                "                          ▼\n"
                "                  SonrisaDerrisa.Negocios ──► SonrisaDerrisa.Entidades\n"
                "                          │\n"
                "                          ▼\n"
                "                  SonrisaDerrisa.Datos (MySql.Data, consultas parametrizadas)\n"
                "                          │  usuario sonrisa_app (mínimo privilegio)\n"
                "                          ▼\n"
                "       MySQL 8: tablas + vistas + triggers + fn_saldo_cita + sp_atender_cita", 8.5))
p("Todas las sentencias usan parámetros (<i>@nombre</i>), lo que previene inyección SQL. La cadena de conexión "
  "se lee de <i>ConnectionStrings:SonrisaDerrisa</i> en User Secrets; el repositorio no contiene contraseñas.")

# ================================================================== 4 MODELO CONCEPTUAL
h1("4. Etapa 3: Modelo entidad-relación")
p("El modelo tiene 8 entidades: <b>Especialidad, Dentista, Paciente, HistorialClinico, Cita, Tratamiento, "
  "DetalleCita y Pago</b>. Las relaciones son: Especialidad–Dentista 1:N, Paciente–HistorialClinico 1:1, "
  "Paciente–Cita 1:N, Dentista–Cita 1:N, Cita–Tratamiento N:M resuelta con DetalleCita, y Cita–Pago 1:N. "
  "A continuación se presenta el diagrama en las cinco notaciones solicitadas (archivos .dot editables con "
  "Graphviz y exportados a PNG y PDF en la carpeta Diagramas).")
imagen(os.path.join(DIAG, "01_crows_foot.png"), "Figura 1. Notación Crow's Foot")
imagen(os.path.join(DIAG, "02_classic_chen.png"), "Figura 2. Notación Classic (Chen)", alto_max=7.6 * inch)
imagen(os.path.join(DIAG, "03_connect_to_columns.png"), "Figura 3. Notación Connect to Columns")
imagen(os.path.join(DIAG, "04_uml.png"), "Figura 4. Notación UML (diagrama de clases)")
imagen(os.path.join(DIAG, "05_idef1x.png"), "Figura 5. Notación IDEF1X")
h2("4.1 Justificación de la notación más adecuada")
S.append(tabla([("Notación", "Fortaleza", "Limitación en este proyecto"),
                ("Crow's Foot", "Muestra cardinalidad mínima y máxima en cada extremo, PK/FK y tipos.", "Ninguna relevante."),
                ("Classic (Chen)", "Ideal para el análisis conceptual: atributos, relaciones y entidad débil.", "Con 8 entidades y 40 atributos el diagrama crece mucho; no muestra tipos."),
                ("Connect to Columns", "Señala exactamente qué columna referencia a qué PK.", "No muestra cardinalidades ni opcionalidad."),
                ("UML", "Multiplicidades claras (0..1, 0..*), familiar para programadores.", "Pensado para clases; las FK no son un concepto propio de UML."),
                ("IDEF1X", "Distingue relaciones identificadoras y llaves en la parte superior.", "Símbolos (P, Z, punto) poco intuitivos para usuarios del negocio.")],
               [80, 190, 181]))
p("Se elige <b>Crow's Foot</b> como notación principal porque en un solo diagrama comunica las "
  "cardinalidades que dan origen a las reglas de negocio (por ejemplo, que un paciente tiene <i>cero o un</i> "
  "historial y que una cita tiene <i>cero o muchos</i> pagos), muestra PK, FK y tipos de datos, y corresponde "
  "directamente con las tablas creadas en el script DDL. La notación Chen se conserva para la etapa conceptual.")

# ================================================================== 5 DICCIONARIO
h1("5. Etapa 4: Diccionario de datos")
DIC = {
    "especialidad": [("id_especialidad", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                     ("nombre", "VARCHAR(50)", "No", "UQ", "UNIQUE", "Área de la odontología")],
    "paciente": [("id_paciente", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                 ("nombre", "VARCHAR(50)", "No", "", "", "Nombre(s)"),
                 ("apellidos", "VARCHAR(80)", "No", "", "", "Apellidos"),
                 ("fecha_nacimiento", "DATE", "Sí", "", "", "Para distinguir pacientes infantiles"),
                 ("telefono", "VARCHAR(15)", "No", "", "CHECK 10 dígitos", "Contacto (RN1)"),
                 ("correo", "VARCHAR(100)", "Sí", "UQ", "UNIQUE, CHECK formato", "Correo electrónico"),
                 ("fecha_registro", "DATE", "No", "", "DEFAULT CURRENT_DATE", "Alta en la clínica")],
    "historial_clinico": [("id_historial", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                          ("id_paciente", "INT", "No", "FK, UQ", "ON DELETE CASCADE", "Paciente dueño (RN2, 1:1)"),
                          ("alergias", "VARCHAR(200)", "Sí", "", "", "Alergias conocidas"),
                          ("enfermedades", "VARCHAR(200)", "Sí", "", "", "Padecimientos crónicos"),
                          ("medicamentos", "VARCHAR(200)", "Sí", "", "", "Medicación actual"),
                          ("fecha_actualizacion", "DATE", "No", "", "DEFAULT CURRENT_DATE", "Última actualización")],
    "dentista": [("id_dentista", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                 ("nombre", "VARCHAR(50)", "No", "", "", "Nombre(s)"),
                 ("apellidos", "VARCHAR(80)", "No", "", "", "Apellidos"),
                 ("cedula", "VARCHAR(20)", "No", "UQ", "UNIQUE", "Cédula profesional (RN3)"),
                 ("telefono", "VARCHAR(15)", "Sí", "", "CHECK 10 dígitos", "Contacto"),
                 ("id_especialidad", "INT", "No", "FK", "ON DELETE RESTRICT", "Especialidad (RN3)")],
    "tratamiento": [("id_tratamiento", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                    ("nombre", "VARCHAR(60)", "No", "UQ", "UNIQUE", "Servicio ofrecido"),
                    ("descripcion", "VARCHAR(200)", "Sí", "", "", "Detalle del servicio"),
                    ("precio_base", "DECIMAL(10,2)", "No", "", "CHECK ≥ 0", "Precio de lista")],
    "cita": [("id_cita", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
             ("id_paciente", "INT", "No", "FK", "ON DELETE RESTRICT", "Paciente (RN4)"),
             ("id_dentista", "INT", "No", "FK", "ON DELETE RESTRICT, índice ix_cita_agenda", "Dentista (RN4)"),
             ("fecha", "DATE", "No", "", "", "Día de la cita"),
             ("hora", "TIME", "No", "", "Trigger anti-empalme", "Hora de inicio (RN5)"),
             ("motivo", "VARCHAR(150)", "Sí", "", "", "Motivo de consulta"),
             ("estado", "VARCHAR(15)", "No", "", "CHECK lista, DEFAULT 'Programada'", "Programada / Atendida / Cancelada (RN6)")],
    "detalle_cita": [("id_detalle", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
                     ("id_cita", "INT", "No", "FK, UQ*", "ON DELETE RESTRICT", "Cita atendida (RN7)"),
                     ("id_tratamiento", "INT", "No", "FK, UQ*", "ON DELETE RESTRICT", "Tratamiento aplicado (RN8)"),
                     ("diente", "VARCHAR(5)", "Sí", "UQ*", "CHECK FDI 11-88", "Pieza dental (notación FDI)"),
                     ("precio_aplicado", "DECIMAL(10,2)", "No", "", "CHECK ≥ 0", "Precio cobrado (RN9)")],
    "pago": [("id_pago", "INT", "No", "PK", "AUTO_INCREMENT", "Identificador"),
             ("id_cita", "INT", "No", "FK", "ON DELETE RESTRICT", "Cita pagada (RN10)"),
             ("fecha_pago", "DATE", "No", "", "DEFAULT CURRENT_DATE", "Fecha del abono"),
             ("monto", "DECIMAL(10,2)", "No", "", "CHECK > 0, trigger tope", "Importe (RN11)"),
             ("metodo_pago", "VARCHAR(15)", "No", "", "CHECK lista", "Efectivo / Tarjeta / Transferencia")],
}
for t, cols in DIC.items():
    S.append(KeepTogether([Paragraph(f"Tabla <b>{t}</b>", H2.clone("h3", fontSize=12, spaceBefore=6)),
                           tabla([("Columna", "Tipo", "Nulo", "Llave", "Restricción", "Descripción")] + cols,
                                 [88, 72, 30, 42, 112, 107], fuente=8.5)]))
p("UQ* = columnas de la llave única compuesta uq_detalle_cita_trat_diente (id_cita, id_tratamiento, diente).")

# ================================================================== 6 INTEGRIDAD
h1("6. Etapa 5: Integridad de datos")
S.append(tabla([("Tipo", "Implementación en sonrisa_derrisa"),
                ("Entidad", "Cada tabla tiene PK INT AUTO_INCREMENT (llave sustituta, nunca nula ni repetida)."),
                ("Referencial", "7 llaves foráneas. ON UPDATE CASCADE en todas. ON DELETE RESTRICT para no perder citas, "
                                "detalles ni pagos; ON DELETE CASCADE sólo en historial_clinico (el historial no existe sin su paciente)."),
                ("Dominio", "CHECK de teléfono (REGEXP 10 dígitos), correo, estado, método de pago, monto > 0, precios ≥ 0 y "
                            "diente FDI; tipos DATE, TIME y DECIMAL(10,2) para dinero."),
                ("Unicidad", "UNIQUE en especialidad.nombre, paciente.correo, historial.id_paciente (1:1), dentista.cedula, "
                             "tratamiento.nombre y (id_cita, id_tratamiento, diente)."),
                ("Valores por defecto", "estado = 'Programada', fecha_registro / fecha_pago / fecha_actualizacion = fecha actual."),
                ("Reglas de negocio", "Triggers para RN2, RN5, RN7 y RN11 (no expresables con CHECK porque consultan otras filas)."),
                ("Transaccional", "sp_atender_cita usa START TRANSACTION / COMMIT con EXIT HANDLER que hace ROLLBACK; "
                                  "el alta de paciente con historial también es una transacción en la capa de datos.")],
               [90, 361]))

# ================================================================== 7 NORMALIZACIÓN
h1("7. Etapa 6: Normalización (1FN a 3FN)")
p("Se parte de la ficha que la clínica llevaba en la libreta, representada como una sola relación no normalizada:")
S.append(codigo("FICHA(paciente, telefono, alergias, enfermedades, dentista, cedula, especialidad, fecha, hora, estado,\n"
                "      {tratamiento, diente, precio_base, precio_aplicado}, {fecha_pago, monto, metodo_pago})", 8))
h2("7.1 Primera forma normal (1FN)")
p("La ficha tiene dos grupos repetitivos (los tratamientos y los abonos de la cita) y atributos compuestos "
  "(nombre completo). Se separan los nombres en <i>nombre</i> y <i>apellidos</i>, se asigna la llave "
  "<i>id_cita</i> y cada grupo repetitivo pasa a su propia relación con valores atómicos:")
S.append(codigo("CITA_1FN(id_cita, paciente_nombre, paciente_apellidos, telefono, alergias, enfermedades, medicamentos,\n"
                "         dentista, cedula, especialidad, fecha, hora, motivo, estado)\n"
                "DETALLE_1FN(id_cita, tratamiento, diente, precio_base, precio_aplicado)\n"
                "PAGO_1FN(id_cita, num_pago, fecha_pago, monto, metodo_pago)", 8))
h2("7.2 Segunda forma normal (2FN)")
p("En DETALLE_1FN la llave es compuesta (id_cita, tratamiento, diente), pero <i>precio_base</i> y la "
  "descripción dependen sólo de <i>tratamiento</i> (dependencia parcial). Se extrae el catálogo TRATAMIENTO y "
  "el detalle conserva únicamente lo que depende de la llave completa (<i>precio_aplicado</i>). En PAGO se usa "
  "la llave sustituta id_pago, por lo que no hay dependencias parciales.")
S.append(codigo("TRATAMIENTO(id_tratamiento, nombre, descripcion, precio_base)\n"
                "DETALLE_CITA(id_detalle, id_cita, id_tratamiento, diente, precio_aplicado)   UQ(id_cita, id_tratamiento, diente)\n"
                "PAGO(id_pago, id_cita, fecha_pago, monto, metodo_pago)", 8))
h2("7.3 Tercera forma normal (3FN)")
p("En CITA_1FN existen dependencias transitivas: id_cita → paciente → telefono, alergias; "
  "id_cita → dentista → cedula → especialidad. Se separan PACIENTE, HISTORIAL_CLINICO (1:1, datos médicos "
  "opcionales y confidenciales), DENTISTA y ESPECIALIDAD. El saldo no se almacena porque es un dato derivado "
  "(RN12) que se calcula con fn_saldo_cita, evitando anomalías de actualización.")
S.append(codigo("ESPECIALIDAD(id_especialidad, nombre)\n"
                "PACIENTE(id_paciente, nombre, apellidos, fecha_nacimiento, telefono, correo, fecha_registro)\n"
                "HISTORIAL_CLINICO(id_historial, id_paciente, alergias, enfermedades, medicamentos, fecha_actualizacion)\n"
                "DENTISTA(id_dentista, nombre, apellidos, cedula, telefono, id_especialidad)\n"
                "CITA(id_cita, id_paciente, id_dentista, fecha, hora, motivo, estado)\n"
                "TRATAMIENTO(...), DETALLE_CITA(...), PAGO(...)", 8))
p("El resultado son las 8 tablas del script 01_esquema.sql. En cada una todos los atributos no clave dependen "
  "de la llave, de toda la llave y de nada más que la llave.")

# ================================================================== 8 BCNF/4FN/5FN
h1("8. Etapa 7: Análisis de BCNF, 4FN y 5FN")
h2("8.1 Forma normal de Boyce-Codd")
p("Una relación está en BCNF si todo determinante es superllave. Las dependencias funcionales no triviales del "
  "esquema son: paciente: id_paciente → resto, correo → id_paciente (correo es llave candidata); "
  "dentista: id_dentista → resto, cedula → id_dentista (llave candidata); especialidad y tratamiento: "
  "nombre → id (llave candidata); detalle_cita: (id_cita, id_tratamiento, diente) → id_detalle, precio_aplicado "
  "(llave candidata). Todos los determinantes son llaves candidatas, por lo que <b>todas las tablas cumplen BCNF</b>.")
p("Caso revisado: la regla RN5 sugiere la dependencia (id_dentista, fecha, hora) → id_cita. No es una "
  "dependencia funcional de toda la relación, porque una cita cancelada puede compartir horario con otra activa; "
  "por eso no se declaró como UNIQUE y se controla con trigger. No rompe BCNF.")
h2("8.2 Cuarta forma normal")
p("La 4FN prohíbe dependencias multivaluadas independientes en una misma tabla. Una cita tiene dos hechos "
  "multivaluados independientes entre sí: sus tratamientos y sus pagos (un abono no corresponde a un tratamiento "
  "específico). Si se guardaran juntos en CITA_TRAT_PAGO(id_cita, tratamiento, pago) habría que repetir cada pago "
  "por cada tratamiento. El diseño los separa en <b>detalle_cita</b> y <b>pago</b>, cada uno dependiente sólo de "
  "id_cita, por lo que el esquema cumple 4FN.")
h2("8.3 Quinta forma normal")
p("La 5FN exige que toda dependencia de reunión esté implicada por las llaves candidatas. No existen relaciones "
  "ternarias: Cita–Tratamiento es binaria con atributos propios (diente, precio_aplicado) y su llave contiene a "
  "id_cita. Descomponer detalle_cita en proyecciones más pequeñas produciría tuplas espurias al reunirlas, de modo "
  "que no hay dependencias de reunión adicionales. El esquema cumple 5FN y no requiere más descomposición.")

# ================================================================== 9 ÁLGEBRA RELACIONAL
h1("9. Álgebra relacional")
AR = [
    ("AR1. Selección y proyección: agenda programada de la Dra. Morales (id 1).",
     "π fecha, hora, id_paciente ( σ estado='Programada' ∧ id_dentista=1 (cita) )",
     "SELECT fecha, hora, id_paciente FROM cita WHERE estado='Programada' AND id_dentista=1;",
     "(2026-11-25, 11:00, 4)"),
    ("AR2. Reunión natural: pacientes y fechas de sus citas atendidas.",
     "π nombre, apellidos, fecha ( paciente ⋈ σ estado='Atendida' (cita) )",
     "SELECT p.nombre, p.apellidos, c.fecha FROM paciente p JOIN cita c USING (id_paciente) WHERE c.estado='Atendida';",
     "11 tuplas"),
    ("AR3. Reunión de tres relaciones: tratamientos de la cita 2.",
     "π nombre, diente, precio_aplicado ( σ id_cita=2 (detalle_cita) ⋈ tratamiento )",
     "SELECT t.nombre, d.diente, d.precio_aplicado FROM detalle_cita d JOIN tratamiento t USING (id_tratamiento) WHERE d.id_cita=2;",
     "(Valoración, null, 300), (Endodoncia, 36, 3500)"),
    ("AR4. Diferencia: pacientes sin historial clínico.",
     "π id_paciente (paciente) − π id_paciente (historial_clinico)",
     "SELECT id_paciente FROM paciente WHERE id_paciente NOT IN (SELECT id_paciente FROM historial_clinico);",
     "{ 8 } (Diego Rentería)"),
    ("AR5. Unión: directorio telefónico de pacientes y dentistas.",
     "π telefono (paciente) ∪ π telefono ( σ telefono≠null (dentista) )",
     "SELECT telefono FROM paciente UNION SELECT telefono FROM dentista WHERE telefono IS NOT NULL;",
     "12 teléfonos"),
    ("AR6. Agregación: total cobrado por método de pago.",
     "metodo_pago γ COUNT(id_pago), SUM(monto) (pago)",
     "SELECT metodo_pago, COUNT(*), SUM(monto) FROM pago GROUP BY metodo_pago;",
     "Tarjeta 3 / 3650; Efectivo 5 / 3200; Transferencia 2 / 1400"),
]
for titulo, expr, sql, res in AR:
    S.append(KeepTogether([Paragraph(f"<b>{titulo}</b>", TX), Paragraph(expr, ALG), codigo(sql, 7.5),
                           Paragraph(f"Resultado con los datos de prueba: {res}", TX)]))

# ================================================================== 10 IMPLEMENTACIÓN SQL
h1("10. Implementación en MySQL")
h2("10.1 Scripts")
S.append(tabla([("Script", "Contenido"),
                ("01_esquema.sql", "Crea la base sonrisa_derrisa (utf8mb4) y las 8 tablas con PK, FK, UNIQUE, CHECK, DEFAULT e índice."),
                ("02_datos.sql", "Datos ficticios reproducibles: 5 especialidades, 8 pacientes, 7 historiales, 5 dentistas, "
                                 "8 tratamientos, 14 citas, 13 detalles y 10 pagos. Incluye casos límite (paciente sin historial, "
                                 "especialidad sin dentistas, cita cancelada, seguimiento sin costo)."),
                ("03_consultas_vistas.sql", "10 consultas documentadas, 2 vistas, transacción con COMMIT y caso con ROLLBACK."),
                ("04_rutinas.sql", "4 triggers, 1 función y 2 procedimientos almacenados."),
                ("05_pruebas.sql", "Casos válidos e inválidos de rutinas y restricciones (se ejecuta con --force).")],
               [110, 341]))
p("Orden de ejecución: <font face='MONO' size='9'>mysql -u root -p --default-character-set=utf8mb4 &lt; 01_esquema.sql</font> "
  "y así sucesivamente con 02, 03 y 04. Las salidas reales están en Pruebas/resultados_sql.")

h2("10.2 Consultas")
sql03 = leer(os.path.join(SQL, "03_consultas_vistas.sql"))
bloques = tablas_resultado(os.path.join(RES, "03_consultas_vistas.txt"))
consultas = re.findall(r"(-- (Q\d+) \(([^)]*)\) ([^\n]*)\n(.*?;))", sql03, re.S)
for i, (_, q, tipo, desc, cuerpo) in enumerate(consultas):
    S.append(Paragraph(f"<b>{q}. {desc}</b> <i>({tipo})</i>", TX))
    S.append(codigo(cuerpo))
    S.append(Paragraph("Resultado:", TX))
    S.append(codigo(bloques[i]))

h2("10.3 Vistas")
p("<b>vw_agenda</b> une cita, paciente, dentista, especialidad e historial; la usa el módulo de citas para "
  "mostrar la agenda con alertas de alergias. <b>vw_saldo_citas</b> calcula total, pagado y saldo de cada cita "
  "atendida; la usan el reporte de saldos, el registro de pagos y sp_estado_cuenta_paciente.")
vistas = re.search(r"(CREATE OR REPLACE VIEW vw_agenda.*?;)\s*-- V2[^\n]*\n(CREATE OR REPLACE VIEW vw_saldo_citas.*?;)", sql03, re.S)
S.append(codigo(vistas.group(1)))
S.append(codigo(vistas.group(2)))
S.append(Paragraph("Consulta a las vistas (citas desde noviembre y saldos pendientes):", TX))
S.append(codigo(bloques[10]))
S.append(codigo(bloques[11]))

h2("10.4 Transacciones")
p("<b>T1 (COMMIT):</b> alta del tratamiento 'Corona de porcelana' y aumento de 5 % al precio de la limpieza "
  "dental; ambos cambios se confirman juntos.")
S.append(codigo(re.search(r"(START TRANSACTION;\nINSERT INTO tratamiento.*?COMMIT;)", sql03, re.S).group(1)))
S.append(codigo(bloques[12]))
p("<b>T2 (ROLLBACK controlado):</b> se eliminan por error los pagos de la cita 2; dentro de la transacción ya no "
  "aparecen y, tras ROLLBACK, se recuperan los 2 pagos por $2,800.")
S.append(codigo(re.search(r"(START TRANSACTION;\nDELETE FROM pago.*?ROLLBACK;)", sql03, re.S).group(1)))
for b in bloques[13:16]:
    S.append(codigo(b))

h2("10.5 Triggers, función y procedimientos")
S.append(tabla([("Objeto", "Evento / firma", "Regla", "Efecto"),
                ("trg_cita_bi", "BEFORE INSERT cita", "RN2, RN5", "Rechaza citas de pacientes sin historial y empalmes del dentista (ignora canceladas)."),
                ("trg_cita_bu", "BEFORE UPDATE cita", "RN5", "Rechaza reprogramar a un horario ocupado (excluye la propia cita)."),
                ("trg_detalle_cita_bi", "BEFORE INSERT detalle_cita", "RN7", "Sólo permite tratamientos en citas atendidas."),
                ("trg_pago_bi", "BEFORE INSERT pago", "RN11", "Rechaza abonos mayores al saldo pendiente."),
                ("fn_saldo_cita", "(p_id_cita INT) RETURNS DECIMAL(10,2)", "RN12", "Suma de precios aplicados menos suma de pagos."),
                ("sp_atender_cita", "(cita, tratamiento, diente, precio, monto, método)", "RN6-RN11",
                 "Operación multitabla todo o nada: actualiza cita, inserta detalle_cita y pago; ROLLBACK + RESIGNAL ante error."),
                ("sp_estado_cuenta_paciente", "(p_id_paciente INT)", "RN12", "Devuelve el detalle por cita y el total del paciente.")],
               [92, 110, 48, 201]))
rut = leer(os.path.join(SQL, "04_rutinas.sql"))
S.append(Paragraph("Código del trigger principal y del procedimiento transaccional:", TX))
S.append(codigo(re.search(r"(CREATE TRIGGER trg_cita_bi.*?END//)", rut, re.S).group(1)))
S.append(codigo(re.search(r"(CREATE PROCEDURE sp_atender_cita.*?END//)", rut, re.S).group(1)))

PS = [
    ("PF-01", "fn_saldo_cita de citas 1, 2, 4, 8, 11", "Saldos 0, 1000, 700, 400, 400", "Correcto", "Válido"),
    ("PF-02", "fn_saldo_cita de cita programada 12", "0.00", "0.00", "Límite"),
    ("PT-01", "Cita para paciente sin historial (8)", "ERROR 1644 RN2", "ERROR 1644 'El paciente debe tener historial…'", "Inválido"),
    ("PT-02", "Cita empalmada dentista 1, 25/11 11:00", "ERROR 1644 RN5", "ERROR 1644 'El dentista ya tiene una cita…'", "Inválido"),
    ("PT-03", "Cita en horario de cita cancelada", "Se inserta", "Insertada (cita 15)", "Válido"),
    ("PT-04", "Reprogramar cita 12 a horario ocupado", "ERROR 1644 RN5", "ERROR 1644", "Inválido"),
    ("PT-05", "Tratamiento en cita programada", "ERROR 1644 RN7", "ERROR 1644 'Solo las citas atendidas…'", "Inválido"),
    ("PT-06", "Pago 900 con saldo 700", "ERROR 1644 RN11", "ERROR 1644 'El pago excede…'", "Inválido"),
    ("PT-07", "Pago exacto 700", "Se inserta, saldo 0", "Saldo 0.00", "Válido"),
    ("PP-01", "sp_atender_cita(13, limpieza 500, abono 300)", "Atendida + detalle + pago", "Saldo 200.00", "Válido"),
    ("PP-02", "sp_atender_cita cita 999", "ERROR 'La cita no existe.'", "ERROR 1644", "Inválido"),
    ("PP-03", "sp_atender_cita cita cancelada", "ERROR", "ERROR 1644 'No se puede atender…'", "Inválido"),
    ("PP-04", "sp_atender_cita abono 5000 > 2800", "ROLLBACK total", "Cita sigue Programada, 0 detalles", "Inválido"),
    ("PP-05", "sp_atender_cita diente '99'", "ROLLBACK por CHECK", "ERROR 3819, cita sigue Programada", "Inválido"),
    ("PP-06", "sp_estado_cuenta_paciente(2)", "2 conjuntos de resultados", "Total 3800, pagado 2800, saldo 1000", "Válido"),
    ("PP-07", "sp_estado_cuenta_paciente(999)", "ERROR", "ERROR 1644 'El paciente no existe.'", "Inválido"),
    ("PR-01", "Eliminar dentista con citas", "ERROR 1451", "ERROR 1451", "Inválido"),
    ("PR-02", "Cédula repetida", "ERROR 1062", "ERROR 1062", "Inválido"),
    ("PR-03", "Segundo historial del paciente 1", "ERROR 1062", "ERROR 1062", "Inválido"),
    ("PR-04", "Estado 'Pendiente'", "ERROR 3819", "ERROR 3819", "Inválido"),
    ("PR-05", "Pago de 0", "ERROR 3819", "ERROR 3819", "Inválido"),
    ("PR-06", "Teléfono '64612AB'", "ERROR 3819", "ERROR 3819", "Inválido"),
    ("PR-07", "Borrar paciente con historial", "Historial borrado en cascada", "0 historiales huérfanos", "Válido"),
]
S.append(Paragraph("Resultados de 05_pruebas.sql (salida completa en Pruebas/resultados_sql/05_pruebas.txt):", TX))
S.append(tabla([("ID", "Caso", "Esperado", "Obtenido", "Tipo")] + PS, [38, 140, 98, 133, 42], fuente=8.5))

# ================================================================== 11 APLICACIÓN
h1("11. Aplicación")
S.append(tabla([("Requisito del proyecto", "Implementación"),
                ("CRUD de 3 entidades", "Pacientes (con historial), Dentistas (con especialidad) y Citas (agendar, reprogramar, cancelar)."),
                ("Operación transaccional multitabla", "Citas → Atender: llama a sp_atender_cita (cita + detalle_cita + pago)."),
                ("Consulta / reporte", "Agenda con filtros sobre vw_agenda y Reporte de saldos sobre vw_saldo_citas con totales."),
                ("Mensajes y estados vacíos", "Alertas de éxito y error (TempData) y recuadro 'No hay …' cuando no hay datos."),
                ("Validaciones", "DataAnnotations en cliente y servidor + reglas de la BD traducidas a mensajes."),
                ("Persistencia", "Los datos sobreviven al reinicio de la aplicación (prueba CP-13)."),
                ("Credenciales", "Usuario sonrisa_app con privilegios mínimos; cadena en User Secrets.")],
               [150, 301]))
p("Para ejecutar: crear la base con los scripts, configurar el secreto y lanzar la aplicación:")
S.append(codigo('dotnet user-secrets set "ConnectionStrings:SonrisaDerrisa" "Server=localhost;Database=sonrisa_derrisa;User ID=sonrisa_app;Password=<secreto>;" --project SonrisaDerrisa.Web\n'
                "dotnet run --project SonrisaDerrisa.Web", 7))

# ================================================================== 12 PRUEBAS
h1("12. Pruebas")
CP = [
    ("CP-01", "RF01, RN2", "Aplicación iniciada", "Sofía Herrera Campos, 6461230009, alergia Amoxicilina", "Pacientes → Nuevo → capturar → Guardar", "Paciente e historial guardados en una transacción", "Mensaje 'Paciente e historial clínico registrados.'; aparece con historial 'Sí'", "Aprobado", "cp01_alta_paciente.jpg"),
    ("CP-02", "RF01, RN1", "Formulario de paciente", "Teléfono '64612AB'", "Capturar teléfono inválido → Guardar", "Se rechaza sin llegar a la BD", "'El teléfono debe tener 10 dígitos.'", "Aprobado", "cp02_telefono_invalido.jpg"),
    ("CP-03", "RF05, RN2", "Diego no tiene historial", "Diego, Dra. Morales, 01/12/2026 09:00", "Citas → Agendar → Guardar", "Rechazo del trigger trg_cita_bi", "'El paciente debe tener historial clínico antes de agendar una cita.'", "Aprobado", "cp03_cita_sin_historial.jpg"),
    ("CP-04", "RF05, RN5", "Dra. Morales tiene cita 25/11 11:00", "Sofía, Dra. Morales, 25/11/2026 11:00", "Agendar en horario ocupado", "Rechazo por empalme", "'El dentista ya tiene una cita en esa fecha y hora.'", "Aprobado", "cp04_empalme.jpg"),
    ("CP-05", "RF05", "Horario libre", "Sofía, Dra. Morales, 25/11/2026 12:00", "Agendar → Guardar", "Cita creada como Programada", "'Cita agendada.'; cita 15 con alerta Amoxicilina", "Aprobado", "cp05_cita_agendada.jpg"),
    ("CP-06", "RF08, RN11", "Cita 14 programada", "Blanqueamiento 2800, abono 5000 Tarjeta", "Atender → Confirmar", "ROLLBACK: nada se guarda", "Mensaje de error; en BD la cita sigue Programada con 0 detalles y 0 pagos", "Aprobado", "cp06_atender_rollback.jpg"),
    ("CP-07", "RF08", "Cita 14 programada", "Blanqueamiento 2800, abono 1000 Tarjeta", "Atender → Confirmar", "Cita Atendida, detalle y pago creados", "'Cita #14 atendida. Saldo pendiente: $1,800.00.'", "Aprobado", "cp07_atender_cita.jpg"),
    ("CP-08", "RF09, RN11", "Cita 14 con saldo 1800", "Monto 2000 Efectivo", "Registrar pago", "Rechazo del trigger trg_pago_bi", "'El pago excede el saldo pendiente de la cita.'", "Aprobado", "cp08_pago_excede.jpg"),
    ("CP-09", "RF09, RF12", "Cita 14 con saldo 1800", "Monto 800 Efectivo", "Registrar pago", "Pago guardado y reporte actualizado", "Saldo de la cita 14 = $1,000; totales $10,000 / $6,500 / $3,500", "Aprobado", "cp09_pago_y_reporte.jpg"),
    ("CP-10", "RF12, RF13", "Sofía sin citas atendidas", "Paciente 'Sofía', sólo pendientes", "Reporte de saldos → Consultar", "Estado vacío", "'No hay citas atendidas que cumplan los criterios.'", "Aprobado", "cp10_estado_vacio.jpg"),
    ("CP-11", "RF03, integridad", "Dra. Morales tiene 6 citas", "Eliminar dentista 1", "Dentistas → Eliminar → Confirmar", "FK RESTRICT impide borrar", "'No se puede eliminar porque tiene citas…' (tras corregir INC-02)", "Aprobado", "cp11_eliminar_dentista_fk.jpg"),
    ("CP-12", "RF03, RN3", "Existe CED-10001", "Martha Lozano, CED-10001", "Dentistas → Nuevo → Guardar", "Rechazo por UNIQUE", "'Ya existe un dentista con esa cédula.'", "Aprobado", "cp12_cedula_duplicada.jpg"),
    ("CP-13", "Persistencia", "Datos de CP-01 a CP-09", "Reiniciar la aplicación", "Detener y volver a iniciar el servidor; filtrar agenda por Sofía", "Los datos siguen en MySQL", "Cita 15 y paciente 9 presentes; consulta directa en BD coincide", "Aprobado", "cp13_persistencia.jpg"),
]
h2("12.1 Matriz de pruebas de la aplicación")
S.append(tabla([("ID", "Req.", "Precondición", "Entrada", "Pasos", "Esperado", "Observado", "Estado")] + [c[:8] for c in CP],
               [32, 42, 58, 62, 62, 64, 92, 39], fuente=7.5))
p("Las pruebas de rutinas y restricciones SQL (PF, PT, PP, PR) se listan en la sección 10.5.")
h2("12.2 Evidencias")
for c in CP:
    imagen(os.path.join(CAP, c[8]), f"{c[0]}. {c[5]}", ancho=ANCHO * 0.86, alto_max=4.3 * inch)

h2("12.3 Incidencias")
INC = [
    ("INC-01", "Al guardar el primer paciente, el listado mostró 'Ocurrió un error en la base de datos'.",
     "La base usaba utf8mb4_unicode_ci y la conexión utf8mb4_0900_ai_ci; el LIKE con CONCAT mezclaba "
     "intercalaciones (ERROR 1267).",
     "Se cambió la intercalación de la base a utf8mb4_0900_ai_ci en 01_esquema.sql y se registró el código MySQL en consola.",
     "Cerrada"),
    ("INC-02", "Al eliminar un dentista con citas apareció el mensaje genérico en vez del de integridad.",
     "El usuario de mínimo privilegio recibe ERROR 1217 (no ve el detalle de la FK), mientras que root recibe 1451; "
     "sólo se mapeaba 1451.",
     "Se mapeó 1217 junto con 1451 en Servicio.Traducir; CP-11 ahora muestra el mensaje correcto.",
     "Cerrada"),
    ("INC-03", "Tras el ROLLBACK de CP-06, el siguiente detalle de cita se guardó con id 15; el id 14 no existe.",
     "InnoDB no devuelve los valores AUTO_INCREMENT consumidos por inserciones revertidas.",
     "Se acepta: los id son llaves sustitutas sin significado de negocio y ninguna consulta depende de que sean "
     "consecutivos. Evidencia en Pruebas/resultados_sql/persistencia_app.txt.",
     "Aceptada"),
]
S.append(tabla([("ID", "Descripción", "Causa", "Solución", "Estado")] + INC, [40, 110, 125, 136, 40], fuente=8.5))
imagen(os.path.join(CAP, "inc01_error_listado.jpg"), "INC-01. Error de intercalación antes de la corrección", ancho=ANCHO * 0.75, alto_max=3.6 * inch)
imagen(os.path.join(CAP, "inc02_error_generico_fk.jpg"), "INC-02. Mensaje genérico antes de mapear el error 1217", ancho=ANCHO * 0.75, alto_max=3.6 * inch)

# ================================================================== 13 CONCLUSIONES
h1("13. Conclusiones individuales")
h2("Kevin Andre Meza Espinoza")
p("Como responsable del backend, comprobé que separar la aplicación en capas facilita mantener las reglas en un "
  "solo lugar: la base de datos garantiza la integridad y la capa de negocio sólo traduce los errores a mensajes. "
  "Llamar a sp_atender_cita desde C# me mostró el valor de que una operación de varias tablas sea atómica: el "
  "caso del abono excesivo se revirtió completo sin escribir código de compensación en la aplicación.")
h2("Aidan Zazueta Medrano")
p("Desde el frontend aprendí que la interfaz debe acompañar al modelo de datos: los filtros de la agenda, las "
  "alertas de alergias y los estados vacíos salen directamente de las vistas vw_agenda y vw_saldo_citas. También "
  "vi que validar en el formulario mejora la experiencia, pero no sustituye a las restricciones de la base, que "
  "siguen protegiendo los datos aunque alguien evite la interfaz.")
h2("Carlos Alberto Jaime Mascareño")
p("En el diseño y las pruebas de la base de datos confirmé que normalizar hasta BCNF evitó guardar datos "
  "derivados como el saldo, que ahora se calcula con fn_saldo_cita. Las pruebas encontraron incidencias reales "
  "que no aparecían ejecutando los scripts como root, como la mezcla de intercalaciones y el error 1217 del "
  "usuario con privilegios mínimos, lo que demuestra la importancia de probar con la misma configuración que usa "
  "la aplicación.")

# ================================================================== 14 REFERENCIAS
h1("14. Referencias")
for r in ["Oracle. (2026). <i>MySQL 8.0 Reference Manual</i>. https://dev.mysql.com/doc/refman/8.0/en/",
          "Microsoft. (2026). <i>Razor Pages en ASP.NET Core</i>. https://learn.microsoft.com/aspnet/core/razor-pages/",
          "Elmasri, R. y Navathe, S. (2016). <i>Fundamentals of Database Systems</i> (7.ª ed.). Pearson.",
          "Silberschatz, A., Korth, H. y Sudarshan, S. (2020). <i>Database System Concepts</i> (7.ª ed.). McGraw-Hill.",
          "Graphviz. (2026). <i>DOT Language</i>. https://graphviz.org/doc/info/lang.html"]:
    S.append(Paragraph(r, BUL, bulletText="•"))

# ------------------------------------------------------------------ salida
Doc(SALIDA).multiBuild(S)
print(SALIDA)

with open(os.path.join(RAIZ, "Pruebas", "matriz_pruebas.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Requisito", "Precondición", "Entrada", "Pasos", "Resultado esperado", "Resultado observado", "Estado", "Evidencia"])
    w.writerows(CP)
    for i, caso, esp, obt, tipo in PS:
        w.writerow([i, "Rutinas/restricciones SQL", "Scripts 01-04 ejecutados", caso, "Ejecutar 05_pruebas.sql", esp, obt, "Aprobado", "resultados_sql/05_pruebas.txt"])
print("matriz_pruebas.csv")
