from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm
from io import BytesIO
import os
from datetime import datetime

def generate_pdf_report(deviation):
    """
    Gera um relatório PDF para um desvio específico com layout e estilo profissionais.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='HeadingStyle',
        parent=styles['h2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor='#002E63', # Azul corporativo
        spaceAfter=6,
        spaceBefore=10
    ))
    styles.add(ParagraphStyle(
        name='BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    ))
    
    story = []

    # --- Cabeçalho e Título ---
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'Blau-Farmaceutica-logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=120, height=30)
        logo.hAlign = 'LEFT'
        story.append(logo)
    
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph("Relatório de Análise de Desvio", styles['TitleStyle']))
    story.append(Spacer(1, 10 * mm))

    # --- Conteúdo do Relatório ---
    report_content = {
        "Descrição do Desvio": deviation.deviation_description,
        "Data da Ocorrência": deviation.deviation_date,
        "Item de GMP não Cumprido": deviation.gmp_item,
        "Produto(s) e Lote(s) Envolvido(s)": deviation.product_involved,
        "Análise de Causa Raiz": deviation.root_cause,
        "Ações Imediatas Tomadas": deviation.immediate_actions,
        "Ações Corretivas e Preventivas": deviation.preventive_actions,
        "Responsáveis pela Investigação": deviation.responsible_investigation,
        "Decisão Final (Conforme Registro)": deviation.final_decision
    }

    for title, content in report_content.items():
        story.append(Paragraph(title, styles['HeadingStyle']))
        story.append(Paragraph(content or "Não informado.", styles['BodyStyle']))

    # --- Seção de Análise da IA ---
    story.append(Paragraph("Análise por Inteligência Artificial", styles['HeadingStyle']))
    
    prediction_text = "Não analisado"
    if deviation.prediction_procedente is not None and deviation.prediction_improcedente is not None:
        if deviation.prediction_procedente > deviation.prediction_improcedente:
            prediction_text = f"<b>Procedente</b> (Confiança: {deviation.prediction_procedente:.2f}%)"
        else:
            prediction_text = f"<b>Improcedente</b> (Confiança: {deviation.prediction_improcedente:.2f}%)"

    story.append(Paragraph(f"<b>Previsão de Resultado:</b> {prediction_text}", styles['BodyStyle']))

    # --- Construção e Rodapé ---
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        footer_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Blau Farmacêutica"
        canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin / 2, footer_text)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes