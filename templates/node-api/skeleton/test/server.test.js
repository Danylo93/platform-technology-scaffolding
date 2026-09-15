const assert = require('node:assert/strict');
const { before, after, test } = require('node:test');
const { once } = require('node:events');

process.env.APP_ENV = 'ti';
const server = require('../src/server');
let baseUrl;

before(async () => {
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => new Promise((resolve, reject) => {
  server.close((error) => error ? reject(error) : resolve());
}));

test('GET / retorna a aplicação Node e o ambiente configurado', async () => {
  const response = await fetch(`${baseUrl}/`);
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-type'), /application\/json/);
  const body = await response.json();
  assert.equal(body.app, '__SERVICE_NAME__');
  assert.equal(body.environment, 'ti');
});

test('GET /health retorna status UP e o ambiente', async () => {
  const response = await fetch(`${baseUrl}/health`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: 'UP', environment: 'ti' });
});
