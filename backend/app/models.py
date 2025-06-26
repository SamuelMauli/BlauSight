# app/models.py
from . import db

class Deviation(db.Model):
    __tablename__ = 'deviations'  # É uma boa prática nomear a tabela explicitamente.

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(255), nullable=True)
    gestor = db.Column(db.String(255), nullable=True)
    data_desvio = db.Column(db.String(50), nullable=True)
    produto = db.Column(db.String(255), nullable=True)
    lote = db.Column(db.String(50), nullable=True)
    id_desvio = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    causa_raiz = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Deviation {self.id_desvio}>'