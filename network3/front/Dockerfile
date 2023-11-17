FROM node:20-alpine

WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

# Set the entrypoint script as executable
# RUN chmod +x /app/entrypoint.sh

EXPOSE 3000

CMD npm run dev


