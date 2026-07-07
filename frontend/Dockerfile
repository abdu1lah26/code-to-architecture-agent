# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files first
COPY package.json package-lock.json ./

# Install exact dependencies from lock file
RUN npm ci

# Copy application source
COPY . .

# Build the frontend
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Install static file server
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/build ./build

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["serve", "-s", "build", "-l", "3000"]