FROM node:24-slim AS builder
ENV NODE_OPTIONS="--max-old-space-size=6144"
ENV CI=true
WORKDIR /app

ENV PUBLIC_BACKEND_API_URL=foo

RUN npm install -g pnpm

# Copy dependency manifests and local plugins for layer caching
COPY package.json pnpm-lock.yaml ./
COPY plugins/ plugins/
RUN pnpm install --frozen-lockfile --ignore-scripts

# Copy source
COPY . .
RUN pnpm exec svelte-kit sync
RUN pnpm exec vite build
RUN pnpm prune --prod --ignore-scripts

FROM node:24-slim
WORKDIR /app
COPY --from=builder /app/build build/
COPY --from=builder /app/server server/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .
EXPOSE 3000
ENV NODE_ENV=production
ENV BODY_SIZE_LIMIT=25000000

CMD [ "node", "server" ]
