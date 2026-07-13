FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Instalar serve para servir a aplicação
RUN npm install -g serve

# Expor porta
EXPOSE 3000

# Comando para iniciar
CMD ["serve", "-s", "build", "-l", "3000"]
