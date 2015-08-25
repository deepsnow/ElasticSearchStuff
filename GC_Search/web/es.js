angular.module('gcApp', ['elasticsearch'])
.service('client', function (esFactory) {
	return esFactory({
		host: 'localhost:9200',
		log: 'trace'
})})
.controller('gcEsSearch', function($scope, client, esFactory, $sce) {
	
	$scope.searcher = this;
	$scope.searcher.searchTerm = "enter search term";
	$scope.searcher.results = [];
	
	$scope.searcher.search = function () {
		
		client.search({
			index: 'gc',
			type: 'talk',
			body: {
				fields : ['title', 'author', 'confid', 'url'],
				query: {
					match: {
						content: $scope.searcher.searchTerm
					}
				},
				highlight : {
					  fields : {
						content : {number_of_fragments: 50}
					}
				}
			}
		}).then(function (resp) {
			$scope.searcher.results = resp.hits.hits;
			
			for (var i=0; i<$scope.searcher.results.length; i++) {
				var result = $scope.searcher.results[i]
				for (var j=0; j<result.highlight.content.length; j++) {
					result.highlight.content[j] = $sce.trustAsHtml(result.highlight.content[j])
				}
			}
			console.trace(resp.hits.total)
			console.trace($scope.searcher.results.length)
		}, function (err) {
						
			if (err instanceof esFactory.errors.NoConnections) {
			  $scope.error = new Error('Unable to connect to elasticsearch. ' +
				'Make sure that it is running and listening at http://localhost:9200');
			}
			console.trace(err.message);
		
		});
	};
	
});