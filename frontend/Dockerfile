FROM node:16.16.0

WORKDIR /star-burger

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
