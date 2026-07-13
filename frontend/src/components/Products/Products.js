import React, { useState, useEffect } from 'react';
import { productsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import Navigation from '../Navigation/Navigation';
import './Products.css';

const Products = () => {
  const { hasPermission } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [duplicateFrom, setDuplicateFrom] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category: '',
    cost_price: '',
    sale_price: '',
    ncm: '',
    icms_rate: '0',
    ipi_rate: '0',
    pis_rate: '0',
    cofins_rate: '0',
    unit: '',
  });

  useEffect(() => {
    fetchProducts();
  }, [page]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.list(page, 10, true);
      setProducts(response.data.products);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Erro ao buscar produtos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        await productsAPI.update(editingProduct.id, formData);
        alert('Produto atualizado com sucesso!');
      } else if (duplicateFrom) {
        await productsAPI.duplicate(duplicateFrom.id, formData.sku, formData.name);
        alert('Produto duplicado com sucesso!');
      } else {
        await productsAPI.create(formData);
        alert('Produto criado com sucesso!');
      }
      resetForm();
      fetchProducts();
    } catch (error) {
      alert(error.response?.data?.message || 'Erro ao salvar produto');
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData(product);
    setShowForm(true);
  };

  const handleDuplicate = (product) => {
    setDuplicateFrom(product);
    setFormData({
      ...product,
      sku: `${product.sku}-COPY`,
      name: `${product.name} (Cópia)`,
    });
    setShowForm(true);
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Tem certeza que deseja deletar este produto?')) return;
    try {
      await productsAPI.delete(productId);
      alert('Produto deletado com sucesso!');
      fetchProducts();
    } catch (error) {
      alert(error.response?.data?.message || 'Erro ao deletar produto');
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditingProduct(null);
    setDuplicateFrom(null);
    setFormData({
      sku: '',
      name: '',
      description: '',
      category: '',
      cost_price: '',
      sale_price: '',
      ncm: '',
      icms_rate: '0',
      ipi_rate: '0',
      pis_rate: '0',
      cofins_rate: '0',
      unit: '',
    });
  };

  if (loading && products.length === 0) {
    return <div className="loading">Carregando produtos...</div>;
  }

  return (
    <div className="dashboard">
      <Navigation />
      <div className="dashboard-content products-page">
        <div className="page-header">
          <h1>Produtos</h1>
          {hasPermission(['admin', 'gerente']) && (
            <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
              {showForm ? 'Cancelar' : '+ Novo Produto'}
            </button>
          )}
        </div>

        {showForm && (
          <form className="product-form" onSubmit={handleSubmit}>
            <h3>{editingProduct ? 'Editar Produto' : duplicateFrom ? 'Duplicar Produto' : 'Novo Produto'}</h3>

            <div className="form-row">
              <div className="form-group">
                <label>SKU *</label>
                <input
                  type="text"
                  name="sku"
                  value={formData.sku}
                  onChange={handleInputChange}
                  required
                  disabled={!!editingProduct}
                />
              </div>
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Preço de Custo *</label>
                <input
                  type="number"
                  name="cost_price"
                  value={formData.cost_price}
                  onChange={handleInputChange}
                  step="0.01"
                  required
                />
              </div>
              <div className="form-group">
                <label>Preço de Venda *</label>
                <input
                  type="number"
                  name="sale_price"
                  value={formData.sale_price}
                  onChange={handleInputChange}
                  step="0.01"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>NCM</label>
                <input
                  type="text"
                  name="ncm"
                  value={formData.ncm}
                  onChange={handleInputChange}
                  placeholder="Nomenclatura Comum do Mercosul"
                />
              </div>
              <div className="form-group">
                <label>Categoria</label>
                <input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>ICMS (%)</label>
                <input
                  type="number"
                  name="icms_rate"
                  value={formData.icms_rate}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
              <div className="form-group">
                <label>IPI (%)</label>
                <input
                  type="number"
                  name="ipi_rate"
                  value={formData.ipi_rate}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
              <div className="form-group">
                <label>PIS (%)</label>
                <input
                  type="number"
                  name="pis_rate"
                  value={formData.pis_rate}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
              <div className="form-group">
                <label>COFINS (%)</label>
                <input
                  type="number"
                  name="cofins_rate"
                  value={formData.cofins_rate}
                  onChange={handleInputChange}
                  step="0.01"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Unidade</label>
                <input
                  type="text"
                  name="unit"
                  value={formData.unit}
                  onChange={handleInputChange}
                  placeholder="UN, KG, L, etc"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                {editingProduct ? 'Atualizar' : duplicateFrom ? 'Duplicar' : 'Criar'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={resetForm}>
                Cancelar
              </button>
            </div>
          </form>
        )}

        <div className="products-list">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Preço de Custo</th>
                <th>Preço de Venda</th>
                <th>NCM</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.sku}</td>
                  <td>{product.name}</td>
                  <td>{product.category || '-'}</td>
                  <td>R$ {product.cost_price.toFixed(2)}</td>
                  <td>R$ {product.sale_price.toFixed(2)}</td>
                  <td>{product.ncm || '-'}</td>
                  <td className="actions">
                    {hasPermission(['admin', 'gerente']) && (
                      <>
                        <button onClick={() => handleEdit(product)} className="btn-icon edit">
                          ✏️
                        </button>
                        <button onClick={() => handleDuplicate(product)} className="btn-icon duplicate">
                          📋
                        </button>
                        {hasPermission(['admin']) && (
                          <button onClick={() => handleDelete(product.id)} className="btn-icon delete">
                            🗑️
                          </button>
                        )}
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pagination">
          <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}>
            Anterior
          </button>
          <span>Página {page} de {totalPages}</span>
          <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages}>
            Próxima
          </button>
        </div>
      </div>
    </div>
  );
};

export default Products;
