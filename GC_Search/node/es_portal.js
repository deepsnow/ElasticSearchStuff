var http = require('http')
var fs = require('fs')
var url = require('url')

var pathPrefix = '../web/'
var parsedUrl = ''

http.createServer(function (req, res) {
		
	console.log(req.url)
		
	if (req.url == '/') {
		res.writeHead(200, {'Content-Type': 'text/html'})
		fs.readFile(
			pathPrefix + 'gc.html'
			, function callback (err, data) {
				res.end(data)
			})
	}
	else {
		res.writeHead(200, {'Content-Type': 'application/javascript'})
		fs.readFile(
			pathPrefix + req.url
			, function callback (err, data) {
				res.end(data)
			})
	}
	
}).listen(80, 'localhost')
console.log('Server running at http://localhost:80/')