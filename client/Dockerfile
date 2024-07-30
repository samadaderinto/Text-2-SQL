# Use an official node runtime as a parent image
FROM node:8

WORKDIR /app/

COPY package.json yarn.lock /app/

RUN npm install

COPY . /app/

EXPOSE 3000

CMD npm run dev