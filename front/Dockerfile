FROM node:24.11.1-alpine
WORKDIR /app
EXPOSE 4200
# Temporary server for checking the Docker environment.
CMD ["node", "-e", "require('node:http').createServer((req, res) => { res.writeHead(200, {'Content-Type': 'text/plain'}); res.end('ok\\n'); }).listen(4200, '0.0.0.0')"]
