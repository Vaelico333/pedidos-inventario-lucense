import reportlab.platypus.paragraph
from reportlab.lib.styles import PropertySet
from reportlab.lib.styles import StyleSheet1
from typing import Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime
import os


def generar_pdf_pedido(pedido_dict: dict[str, int]) -> io.BytesIO:
    """
    Recibe el diccionario de st.session_state.pedido 
    y devuelve un archivo binario en memoria listo para descargar.
    """
    
    # 1. Crear un contenedor en memoria para el archivo (evita guardar en el disco del servidor)
    buffer = io.BytesIO()
    
    # 2. Configurar el documento básico (Márgenes de 1.5 cm aprox)
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story: list[Any] = []
    
    # 3. Configurar los estilos de texto
    styles: StyleSheet1 = getSampleStyleSheet()
    
    # Estilo personalizado para el título
    style_titulo = ParagraphStyle(
        'TituloPedido',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"), # Azul oscuro profesional
        spaceAfter=15
    )
    
    # Estilo para el texto común y celdas
    style_texto: PropertySet = styles['Normal']
    style_cabecera_tabla = ParagraphStyle('Cabecera', parent=styles['Normal'], textColor=colors.white, fontName="Helvetica-Bold")

    # 4. Añadir Encabezado del PDF
    fecha: str = datetime.now().strftime('%d/%m/%Y')
    p_titulo = Paragraph(f'<b>Borrador de Pedido - Bar Lucense</b><br/><b>Fecha:</b> {fecha}', style_titulo)

    ruta_logo = './img/LOGO-LUCENSE_COMPLETO.webp'
    if os.path.exists(ruta_logo):
        logo_pdf = Image(ruta_logo, width=108, height=54)
        tabla_cabecera = Table([[logo_pdf, p_titulo]])
    else:
        # Si por algún motivo no encuentra el logo, coloca un título de texto alternativo
        p_titulo_alt = Paragraph("📋 Borrador de Pedido - Bar Lucense", style_titulo)
        tabla_cabecera = Table([[p_titulo_alt, p_titulo]])
    tabla_cabecera.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(tabla_cabecera)
    story.append(Spacer(1, 25))

    # 5. Estructurar los datos para la Tabla
    # Definimos las columnas: [Proveedor, Producto, Cantidad]
    datos_tabla: list[list[reportlab.platypus.paragraph.Paragraph]] = [[
        Paragraph("<b>Proveedor</b>", style_cabecera_tabla), 
        Paragraph("<b>Producto</b>", style_cabecera_tabla), 
        Paragraph("<b>Cantidad Pedida</b>", style_cabecera_tabla)
        Paragraph("<b>Presentación</b>", style_cabecera_tabla), 
    ]]
    
    for item, cantidad in pedido_dict.items():
        # Tu id_item está guardado como 'Proveedor - Producto'
        if " - " in item:
            prov, pres, prod = item.split(" - ", 2)
            
        datos_tabla.append([
            Paragraph(prov, style_texto),
            Paragraph(prod, style_texto),
            Paragraph(cantidad, style_texto),
            Paragraph(pres, style_texto),
        ])

    # 6. Crear la Tabla y darle diseño visual
    tabla_pedido = Table(
        datos_tabla,
        colWidths=[
            doc.width * 0.22,
            doc.width * 0.23,
            doc.width * 0.39,
            doc.width * 0.16,
        ],
    )
    
    diseno_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")), # Color fondo cabecera
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")), # Líneas divisoras grises
    ])
    
    # Alternar colores de filas para facilitar la lectura (filas cebra)
    for i in range(1, len(datos_tabla)):
        if i % 2 == 0:
            diseno_tabla.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F8FAFC"))
            
    tabla_pedido.setStyle(diseno_tabla)
    story.append(tabla_pedido)
    
    # 7. Construir el documento final
    doc.build(story)
    
    # 8. Mover el puntero del buffer al principio para que Streamlit pueda leerlo
    buffer.seek(0)
    return buffer
