from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    
    # Preços
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Tributário
    ncm = db.Column(db.String(8))  # Nomenclatura Comum do Mercosul
    icms_rate = db.Column(db.Numeric(5, 2), default=0)  # Taxa ICMS
    ipi_rate = db.Column(db.Numeric(5, 2), default=0)   # Taxa IPI
    pis_rate = db.Column(db.Numeric(5, 2), default=0)   # Taxa PIS
    cofins_rate = db.Column(db.Numeric(5, 2), default=0) # Taxa COFINS
    
    # Informações adicionais
    unit = db.Column(db.String(20))  # Unidade (UN, KG, L, etc)
    barcode = db.Column(db.String(100), unique=True)
    weight = db.Column(db.Numeric(10, 3))  # Peso em kg
    height = db.Column(db.Numeric(10, 2))  # Altura em cm
    width = db.Column(db.Numeric(10, 2))   # Largura em cm
    depth = db.Column(db.Numeric(10, 2))   # Profundidade em cm
    
    # Status
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    inventories = db.relationship('Inventory', backref='product', lazy=True, cascade='all, delete-orphan')
    movements = db.relationship('InventoryMovement', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.sku} - {self.name}>'
    
    def duplicate(self, new_sku, new_name=None):
        """Duplica um produto existente com um novo SKU"""
        new_product = Product(
            sku=new_sku,
            name=new_name or f"{self.name} (Cópia)",
            description=self.description,
            category=self.category,
            cost_price=self.cost_price,
            sale_price=self.sale_price,
            ncm=self.ncm,
            icms_rate=self.icms_rate,
            ipi_rate=self.ipi_rate,
            pis_rate=self.pis_rate,
            cofins_rate=self.cofins_rate,
            unit=self.unit,
            weight=self.weight,
            height=self.height,
            width=self.width,
            depth=self.depth,
            active=True
        )
        return new_product
