from . import db

class Deviation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_desvio = db.Column(db.String(50), unique=True, nullable=False)
    data_identificacao = db.Column(db.String(50))
    descricao = db.Column(db.Text, nullable=False)
    causa_raiz = db.Column(db.Text)
    acao_corretiva = db.Column(db.Text)
    status_acao = db.Column(db.String(50))
    classificacao_desvio = db.Column(db.String(100))
    keywords = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'id_desvio': self.id_desvio,
            'data_identificacao': self.data_identificacao,
            'descricao': self.descricao,
            'causa_raiz': self.causa_raiz,
            'acao_corretiva': self.acao_corretiva,
            'status_acao': self.status_acao,
            'classificacao_desvio': self.classificacao_desvio,
            'keywords': self.keywords
        }