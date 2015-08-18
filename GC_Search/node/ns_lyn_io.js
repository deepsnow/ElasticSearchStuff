var fs = require('fs');
var buffer = fs.readFileSync(process.argv[2]);
var str_array = buffer.toString().split('\n');
console.log(str_array.length - 1);