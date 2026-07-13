from app import db
from datetime import datetime
from enum import Enum

class MovementTypeEnum(Enum):
    """Tipos de movimentação de estoque"""
    ENTRADA = 'entrada'
    SAIDA = 'saida'
    AJUSTE = 'ajuste'
    DEVOLUCAO = 'devolucao'

class Inventory(db.Model):
    __tablename__ = 'inventories'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    warehouse = db.Column(db.String(100), default='Principal')
    quantity = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    min_quantity = db.Column(db.Numeric(10, 2), default=0)  # Quantidade mínima
    max_quantity = db.Column(db.Numeric(10, 2))  # Quantidade máxima
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    movements = db.relationship('InventoryMovement', backref='inventory', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inventory {self.product.sku} - {self.quantity}>'

class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=False, index=True)
    movement_type = db.Column(db.String(20), nullable=False)  # entrada, saida, ajuste, devolucao
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    reference = db.Column(db.String(100))  # Referência: NF, PO, etc
    reason = db.Column(db.String(255))  # Motivo do movimento
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='inventory_movements')
    
    def __repr__(self):
        return f'<Movement {self.movement_type} - {self.quantity}>'
