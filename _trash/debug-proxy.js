
const http = require('http');

console.log("Testing connection to 127.0.0.1:8000...");
const req = http.request({
    hostname: '127.0.0.1',
    port: 8000,
    path: '/docs', // Just check if we can reach docs
    method: 'GET',
}, (res) => {
    console.log('STATUS: ' + res.statusCode);
    res.on('data', () => { }); // Consume
});

req.on('error', (e) => {
    console.log('ERROR: ' + e.message);
});
req.end();
