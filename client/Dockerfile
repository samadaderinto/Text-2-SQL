# Use the latest Node.js LTS version as the base image
FROM node:lts

# Set the working directory to /app
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the React app source code
COPY . .

# Build the React app
RUN npm run build

# Expose the port that the React app will run on (usually 3000)
EXPOSE 4173

# Set the command to start the React app
CMD ["npm", "run", "preview"]