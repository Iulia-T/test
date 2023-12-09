const express = require('express');
const httpProxy = require('http-proxy');

const app = express();
const proxy = httpProxy.createProxyServer();

const menuServiceUrl = 'http://menu_serv:5001';
const orderServiceUrl = 'http://order_serv:5002';

// Log requests before they are forwarded
app.use((req, res, next) => {
  console.log(`Received request: ${req.method} ${req.url}`);
  next();
});

// Define routes for each microservice
app.use('/menu', (req, res) => {
  console.log(`Forwarding request to Menu Service: ${req.method} ${req.url}`);
  proxy.web(req, res, { target: menuServiceUrl });
});

app.use('/order', (req, res) => {
  console.log(`Forwarding request to Order Service: ${req.method} ${req.url}`);
  proxy.web(req, res, { target: orderServiceUrl });
});

// Handle errors from the proxy
proxy.on('error', (err, req, res) => {
  console.error(err);
  res.status(500).send('Proxy Error');
});

// Start the gateway on port 3000
const port = 3000;
app.listen(port, () => {
  console.log(`Gateway is running on http://gateway:${port}`);
});

