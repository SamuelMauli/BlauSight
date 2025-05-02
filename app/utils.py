from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import tempfile
import os


def salvar_temporariamente(file_storage, suffix=".docx"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        return tmp.name

def extrair_zip_temporario(zip_file):
    tmpdir = tempfile.mkdtemp()
    zip_path = os.path.join(tmpdir, zip_file.filename)
    zip_file.save(zip_path)
    return tmpdir, zip_path

def gerar_relatorio_pdf(parsed, prediction, explicacao):
    file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4
    margin = 50
    y = height - margin

    # Logo da empresa
    try:
        logo_path = os.path.join("static", "Blau-Farmaceutica-logo.png")
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            c.drawImage(logo, margin, y - 60, width=100, height=40, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print("Erro ao inserir logo:", e)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin + 110, y - 30, "Relatório de Análise de Desvio")
    y -= 90

    # Conteúdo principal
    c.setFont("Helvetica", 12)
    for k, v in parsed.items():
        c.drawString(margin, y, f"{k.capitalize()}: {v}")
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Predição da Causa Raiz: {prediction}")
    y -= 30

    c.setFont("Helvetica-Oblique", 10)
    for linha in explicacao.strip().split("\n"):
        for sublinha in dividir_linha(linha.strip(), width - 2 * margin, c):
            c.drawString(margin, y, sublinha)
            y -= 14
            if y < 100:
                rodape_pdf(c, width, height, margin)
                c.showPage()
                y = height - margin

    # Rodapé na última página
    rodape_pdf(c, width, height, margin)

    c.save()
    return file_path


def dividir_linha(texto, max_width, canvas_obj):
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        test_linha = f"{linha_atual} {palavra}".strip()
        if canvas_obj.stringWidth(test_linha, "Helvetica-Oblique", 10) <= max_width:
            linha_atual = test_linha
        else:
            linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas


def rodape_pdf(c, width, height, margin):
    data = datetime.now().strftime('%d/%m/%Y %H:%M')
    c.setFont("Helvetica", 8)
    c.setFillGray(0.5)
    c.drawString(margin, 30, f"Gerado em: {data} - Blau Farmacêutica")

    # Assinatura digitalizada (opcional)
    assinatura_path = os.path.join("static", "assinatura.png")
    if os.path.exists(assinatura_path):
        try:
            c.drawImage(assinatura_path, width - 150, 20, width=100, height=30, mask='auto')
        except Exception as e:
            print("Erro ao desenhar assinatura:", e)

    # Futuro: QR code ou ID de verificação
    # c.drawString(width - 160, 60, "Verificação: BLAU-ML-2025-001")