# Use an official node runtime as a parent image
FROM node:alpine

WORKDIR /app/

COPY package.json package-lock.json /app/

RUN npm install

COPY . /app/

EXPOSE 5173

CMD npm run dev