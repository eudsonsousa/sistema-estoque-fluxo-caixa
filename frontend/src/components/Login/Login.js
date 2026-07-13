import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await register(name, email, password);
        setError('Registrado com sucesso! Faça login agora.');
        setIsRegister(false);
        setEmail('');
        setPassword('');
        setName('');
      } else {
        await login(email, password);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Erro na autenticação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>📦 Sistema de Estoque</h1>
        <h2>{isRegister ? 'Criar Conta' : 'Entrar'}</h2>

        {error && <div className={`message ${error.includes('sucesso') ? 'success' : 'error'}`}>{error}</div>}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div className="form-group">
              <label>Nome</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Carregando...' : isRegister ? 'Registrar' : 'Entrar'}
          </button>
        </form>

        <p className="toggle-auth">
          {isRegister ? 'Já tem conta?' : 'Não tem conta?'} 
          <button type="button" onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Entrar' : 'Registrar'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
