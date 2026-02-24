# =============================================================================
# SICO GRC Frontend - Secure Multi-Stage Production Build
# =============================================================================
# Security improvements:
# - Multi-stage build separates build-time from runtime dependencies
# - Uses Node.js 20 LTS (latest security patches)
# - Minimal Alpine Linux base (reduces attack surface)
# - Non-root user execution
# - Production-only dependencies in final image
# - No package managers or build tools in production
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies (cached layer for faster rebuilds)
# -----------------------------------------------------------------------------
FROM node:20.11.1-alpine3.19 AS deps

# Install only required system packages for node-gyp builds
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy only package files for dependency installation
COPY package.json package-lock.json ./

# Install dependencies with clean install (respects lockfile exactly)
# --omit=dev not used here as we need devDependencies for build
RUN npm ci

# -----------------------------------------------------------------------------
# Stage 2: Builder (compile application)
# -----------------------------------------------------------------------------
FROM node:20.11.1-alpine3.19 AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . .

# Set production environment for optimized build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application with standalone output
# This creates a minimal production server with only required files
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Production Runtime (minimal image)
# -----------------------------------------------------------------------------
FROM node:20.11.1-alpine3.19 AS runner

# Install only essential runtime dependencies
RUN apk add --no-cache \
    dumb-init \
    && rm -rf /var/cache/apk/*

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Create non-root user for running application
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    mkdir -p /app/.next && \
    chown -R nextjs:nodejs /app

# Copy only production files from builder
# Next.js standalone output includes only necessary dependencies
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Start application with Node.js directly (no npm overhead)
CMD ["node", "server.js"]
