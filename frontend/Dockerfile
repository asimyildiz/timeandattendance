# Step 1: Build the Vite app
FROM node:20-alpine as build

WORKDIR /app

# Pass env at build time
ARG BACKEND_URL
ENV BACKEND_URL=$BACKEND_URL

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Run NPM build
COPY . .
RUN npm run build

# Step 2: Serve with static server
FROM node:20-alpine

WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
