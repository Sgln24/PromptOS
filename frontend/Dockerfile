# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package management files first to cache depend
COPY package.json package-lock.json ./

# CHANGE THIS LINE from npm ci to npm install
RUN npm install

# Copy the rest of the Next.js application
COPY . .

# Build the production application
RUN npm run build

EXPOSE 3001

# Start the Next.js production server
CMD ["npm", "start"]