from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app.extractor import parse_desvio_docx
from app.ml_engine import train_model, predict, explain_prediction
from app.models import db, RelatorioDesvio
from app.utils import salvar_temporariamente, extrair_zip_temporario, gerar_relatorio_pdf

import pandas as pd
import zipfile
import os
import traceback

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/upload_zip', methods=['POST'])
def upload_zip():
    try:
        zip_file = request.files.get('zipfile')

        if not zip_file or not zip_file.filename.endswith('.zip'):
            flash("Por favor, envie um arquivo .zip válido contendo relatórios .docx.")
            return redirect(url_for('main.index'))

        tmpdir, zip_path = extrair_zip_temporario(zip_file)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        records = []

        for filename in os.listdir(tmpdir):
            if filename.endswith('.docx'):
                path = os.path.join(tmpdir, filename)
                parsed = parse_desvio_docx(path)
                parsed = {k.lower(): v for k, v in parsed.items()}
                records.append(parsed)

                db.session.add(RelatorioDesvio(**parsed))

        if not records:
            flash("Nenhum arquivo .docx foi encontrado no .zip enviado.")
            return redirect(url_for('main.index'))

        db.session.commit()
        df = pd.DataFrame(records)
        train_model(df)

        flash("Modelo treinado com sucesso com os desvios enviados!")
        return redirect(url_for('main.index'))

    except Exception as e:
        print("Erro ao processar upload_zip:", traceback.format_exc())
        flash(f"Ocorreu um erro ao processar o .zip: {str(e)}")
        return redirect(url_for('main.index'))


@bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files.get('file')

        if not file or not file.filename.endswith('.docx'):
            flash("Por favor, envie um arquivo .docx válido para análise.")
            return redirect(url_for('main.index'))

        temp_path = salvar_temporariamente(file)
        parsed = parse_desvio_docx(temp_path)
        parsed = {k.lower(): v for k, v in parsed.items()}
        df = pd.DataFrame([parsed])

        prediction = predict(df)[0]
        explicacao = explain_prediction(df, prediction)
        pdf_path = gerar_relatorio_pdf(parsed, prediction, explicacao)

        return send_file(pdf_path, as_attachment=True, download_name="relatorio_analise.pdf")

    except Exception as e:
        print("Erro ao processar analyze:", traceback.format_exc())
        flash(f"Ocorreu um erro ao analisar o documento: {str(e)}")
        return redirect(url_for('main.index'))
