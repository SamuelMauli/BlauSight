from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.units import inch, mm
from datetime import datetime
import tempfile
import os
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_report(description, prediction, explanation):
    # Cria o PDF em um arquivo temporário seguro
    fd, file_path = tempfile.mkstemp(suffix=".pdf", prefix="report_")
    os.close(fd)  # Fecha o descritor do arquivo para que a biblioteca possa abri-lo

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        fontName='Times-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        name='HeadingStyle',
        parent=styles['h2'],
        fontName='Times-Bold',
        fontSize=14,
        spaceAfter=6,
        spaceBefore=12
    )

    normal_style = ParagraphStyle(
        name='NormalStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        alignment=TA_LEFT
    )

    # Margens (em mm) - padrão ABNT para trabalhos acadêmicos (podem ser ajustadas)
    margin_top = 30 * mm
    margin_bottom = 30 * mm
    margin_left = 30 * mm
    margin_right = 30 * mm

    # Posição atual para o conteúdo
    y_position = height - margin_top

    # Inserir Logo
    logo_path = os.path.join("app", "static", "Blau-Farmaceutica-logo.png") # Ajuste o caminho se necessário
    if os.path.exists(logo_path):
        try:
            img_width = 1.5 * inch
            img_height = img_width * (141 / 592) # Mantém a proporção (altura/largura original)
            c.drawImage(logo_path, margin_left, y_position - img_height, width=img_width, height=img_height, mask='auto')
            y_position -= (img_height + 0.5 * inch)
        except Exception as e:
            print(f"Erro ao inserir logo: {e}")
            y_position -= 0.5 * inch # Espaço se a logo não for inserida
    else:
        y_position -= 0.5 * inch # Espaço se a logo não for encontrada

    # Título
    title = Paragraph("Relatório de Análise de Desvio", title_style)
    title_width, title_height = title.wrapOn(c, width - margin_left - margin_right, y_position)
    title.drawOn(c, margin_left, y_position - title_height)
    y_position -= (title_height + 0.5 * inch)

    # Descrição Analisada
    heading_descricao = Paragraph("Descrição Analisada:", heading_style)
    heading_descricao_width, heading_descricao_height = heading_descricao.wrapOn(c, width - margin_left - margin_right, y_position)
    heading_descricao.drawOn(c, margin_left, y_position - heading_descricao_height)
    y_position -= heading_descricao_height

    descricao_paragraph = Paragraph(description, normal_style)
    descricao_width, descricao_height = descricao_paragraph.wrapOn(c, width - margin_left - margin_right, y_position)
    descricao_paragraph.drawOn(c, margin_left, y_position - descricao_height)
    y_position -= (descricao_height + 0.3 * inch)

    # Previsão da Causa Raiz
    heading_predicao = Paragraph("Previsão da Causa Raiz:", heading_style)
    heading_predicao_width, heading_predicao_height = heading_predicao.wrapOn(c, width - margin_left - margin_right, y_position)
    heading_predicao.drawOn(c, margin_left, y_position - heading_predicao_height)
    y_position -= heading_predicao_height

    predicao_paragraph = Paragraph(prediction, normal_style)
    predicao_width, predicao_height = predicao_paragraph.wrapOn(c, width - margin_left - margin_right, y_position)
    predicao_paragraph.drawOn(c, margin_left, y_position - predicao_height)
    y_position -= (predicao_height + 0.3 * inch)

    # Justificativa
    heading_justificativa = Paragraph("Justificativa:", heading_style)
    heading_justificativa_width, heading_justificativa_height = heading_justificativa.wrapOn(c, width - margin_left - margin_right, y_position)
    heading_justificativa.drawOn(c, margin_left, y_position - heading_justificativa_height)
    y_position -= heading_justificativa_height

    justificativa_paragraph = Paragraph(explanation, normal_style)
    justificativa_width, justificativa_height = justificativa_paragraph.wrapOn(c, width - margin_left - margin_right, y_position)
    justificativa_paragraph.drawOn(c, margin_left, y_position - justificativa_height)
    y_position -= justificativa_height

    # Rodapé
    c.setFont("Times-Roman", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5) # Cor cinza para o rodapé
    c.drawString(margin_left, margin_bottom, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.drawRightString(width - margin_right, margin_bottom, "Blau Farmacêutica")

    c.save()
    return file_path