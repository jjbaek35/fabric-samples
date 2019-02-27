var stdio = require('stdio');
var ops = stdio.getopt({
    'check': {key: 'c', args: 2, description: 'What this option means'},
    'map': {key: 'm', description: 'Another description'},
    'kaka': {args: 1, mandatory: true},
    'ooo': {key: 'o'}
});