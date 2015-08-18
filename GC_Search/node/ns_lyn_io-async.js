var fs = require('fs');
var buffer = fs.readFile(
	process.argv[2]
	, 'utf-8'
	, function callback (err, buffer) {
		console.log(buffer.split('\n').length - 1);
	});