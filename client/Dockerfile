FROM node:22.22.2-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --fetch-timeout=600000 --fetch-retries=5 --fetch-retry-mintimeout=20000 --fetch-retry-maxtimeout=120000 \
    && (node -e 'require("rollup"); require("@swc/core")' 2>/dev/null || npm install --force --no-save @rollup/rollup-linux-arm64-musl @rollup/rollup-linux-x64-musl @swc/core-linux-arm64-musl @swc/core-linux-x64-musl)

COPY . .

EXPOSE 4174

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4174"]
