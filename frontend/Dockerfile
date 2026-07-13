# Frontend do VentureOps AI (servidor de desenvolvimento Vite).
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

# Vite em modo desenvolvimento, acessível fora do contentor; o proxy /api
# aponta para VITE_BACKEND_ORIGIN (definido no compose).
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
