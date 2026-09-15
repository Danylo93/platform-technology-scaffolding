const http = require('node:http');

const port = process.env.PORT || 8080;
const environment = process.env.APP_ENV || 'local';

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  if (req.url === '/health') {
    res.writeHead(200);
    return res.end(JSON.stringify({ status: 'UP', environment }));
  }

  res.writeHead(200);
  res.end(JSON.stringify({
    app: '__SERVICE_NAME__',
    environment,
    message: 'Laboratório de Platform Engineering'
  }));
});

if (require.main === module) {
  server.listen(port, '0.0.0.0', () => {
    console.log(`Aplicação escutando na porta ${port}`);
  });
}

module.exports = server;
