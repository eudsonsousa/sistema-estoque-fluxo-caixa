from app import db
from datetime import datetime
from enum import Enum

class PurchaseStatusEnum(Enum):
    """Status de compra"""
    RASCUNHO = 'rascunho'
    PROCESSADA = 'processada'
    RECEBIDA = 'recebida'
    CANCELADA = 'cancelada'

class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False, index=True)
    nf_number = db.Column(db.String(20), index=True)  # Número da nota fiscal
    nf_series = db.Column(db.String(10))
    nf_key = db.Column(db.String(44), unique=True)  # Chave da NF-e
    
    # Valores
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    net_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Datas
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    received_date = db.Column(db.DateTime)
    
    # Status e notas
    status = db.Column(db.String(20), default='rascunho')  # rascunho, processada, recebida, cancelada
    notes = db.Column(db.Text)
    
    # XML (armazenar o arquivo XML da NF-e em base64)
    nf_xml = db.Column(db.LongText)  # Conteúdo XML da NF-e
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    items = db.relationship('PurchaseItem', backref='purchase', lazy=True, cascade='all, delete-orphan')
    supplier = db.relationship('Supplier', backref='purchases')
    user = db.relationship('User', backref='purchases')
    
    def __repr__(self):
        return f'<Purchase NF {self.nf_number}/{self.nf_series}>'

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Informações do item
    sku = db.Column(db.String(100))  # SKU do fornecedor ou produto
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20))
    
    # Preços
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Tributos
    icms_rate = db.Column(db.Numeric(5, 2), default=0)
    ipi_rate = db.Column(db.Numeric(5, 2), default=0)
    pis_rate = db.Column(db.Numeric(5, 2), default=0)
    cofins_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Preço de venda sugerido (pode ser preenchido manualmente)
    suggested_sale_price = db.Column(db.Numeric(10, 2))
    final_sale_price = db.Column(db.Numeric(10, 2))  # Preço de venda final no estoque
    
    # Status de processamento
    processed = db.Column(db.Boolean, default=False)  # Se o item foi adicionado ao estoque
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='purchase_items')
    
    def __repr__(self):
        return f'<PurchaseItem {self.description}>'
