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
	
	$scope.searcher.search = function () {
		
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
			console.trace($scope.searcher.results.length);
		}, function (err) {
						
			if (err instanceof esFactory.errors.NoConnections) {
			  $scope.error = new Error('Unable to connect to elasticsearch. ' +
				'Make sure that it is running and listening at http://localhost:9200');
			}
			console.trace(err.message);
		
		});
	};
	
});