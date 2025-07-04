# Use official Node.js image for building
FROM node:20 AS build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Use a lightweight web server to serve the static files
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the port Vite/React app will run on (default 80 for nginx)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
