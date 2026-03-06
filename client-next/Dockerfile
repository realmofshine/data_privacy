FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

# Railway sets PORT env var — Next.js must listen on it
ENV PORT=3000
CMD ["npm", "start"]
