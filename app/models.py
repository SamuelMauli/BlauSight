from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RelatorioDesvio(db.Model):
    __tablename__ = 'relatorio_desvio'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    classificacao = db.Column(db.String(50))
    causa_raiz = db.Column(db.Text)
    capa = db.Column(db.Text)
