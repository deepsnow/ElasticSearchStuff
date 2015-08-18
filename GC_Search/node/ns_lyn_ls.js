var fs = require('fs');
var path = require('path');
var ext = process.argv[3];
ext = '.'.concat(ext);
fs.readdir(
	process.argv[2]
	, function callback (err, list) {
		var len = list.length;
		for (var i=0; i<len; i++) {
			if (path.extname(list[i]) == ext) {
				console.log(list[i])
			}
		}
	});