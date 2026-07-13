from app import db
from datetime import datetime
from enum import Enum

class CashFlowTypeEnum(Enum):
    """Tipos de fluxo de caixa"""
    ENTRADA = 'entrada'
    SAIDA = 'saida'

class CashFlow(db.Model):
    __tablename__ = 'cashflows'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # entrada, saida
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Vendas, Custos, etc
    reference = db.Column(db.String(100))  # Referência: NF, PO, etc
    
    # Datas
    due_date = db.Column(db.DateTime)  # Data de vencimento
    payment_date = db.Column(db.DateTime)  # Data de pagamento efetivo
    status = db.Column(db.String(20), default='pendente')  # pendente, pago, cancelado
    
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='cashflows')
    
    def __repr__(self):
        return f'<CashFlow {self.type} - R$ {self.amount}>'
