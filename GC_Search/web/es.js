angular.module('gcApp', ['elasticsearch'])
.service('client', function (esFactory) {
	return esFactory({
		host: 'localhost:9200',
		log: 'trace'
})})
.controller('gcEsSearch', function($scope, client, esFactory) {
	
	$scope.searcher = this;
	$scope.searcher.searchTerm = "enter search term";
	$scope.searcher.results = [];
	
	$scope.searcher.search = function ($scope, client) {
		client.search({
			index: 'gc',
			type: 'talk',
			body: {
				query: {
					match: {
						content: $scope.searcher.searchTerm
					}
				}
			}
		}).then(function (resp) {
			$scope.searcher.results = resp.hits.hits;
			console.trace('successful query?');
		}, function (err) {
			console.trace(err.message);
		});
	};
	
});