FROM node:24-alpine

WORKDIR /app

# Installation des dépendances
COPY package*.json ./
RUN npm install

# Copie du code source
COPY . .

# Port du serveur Angular
EXPOSE 4200

# Démarrage du serveur Angular
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--port", "4200"]