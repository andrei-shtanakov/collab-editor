# Frontend Dockerfile for React + Vite

# ===== Development Stage =====
FROM node:20-alpine AS dev

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 5173

# Dev server with hot reload (host 0.0.0.0 for container access)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


# ===== Build Stage =====
FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build


# ===== Production Stage (nginx) =====
FROM nginx:alpine AS prod

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
