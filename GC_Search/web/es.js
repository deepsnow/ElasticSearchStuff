angular.module('gcApp', ['elasticsearch'])
.service('client', function (esFactory) {
	return esFactory({
		host: 'localhost:9200',
		log: 'trace'
})})
.controller('gcEsSearch', function($scope, client, esFactory, $sce) {
	
	$scope.searcher = this
	$scope.searcher.searchTerm = "enter search term"
	$scope.searcher.results = []
	$scope.searcher.sortOrderings = [{ name: "oldest first", id: 0 }, { name: "newest first", id: 1 }, { name: "relevance", id: 2 }]
	$scope.searcher.chosenOrdering = $scope.searcher.sortOrderings[0]
	
	$scope.searcher.search = function () {
		esCountAndSearch()
	}
	
	function esCountAndSearch() {
		client.count({
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
			hitCount = resp.count
			esSearch(hitCount)
		}, function (err) {
						
			if (err instanceof esFactory.errors.NoConnections) {
			  $scope.error = new Error('Unable to connect to elasticsearch for counting search hits. ' +
				'Make sure that it is running and listening at http://localhost:9200')
			}
			console.trace(err.message)
		})		
	}
	
	function esSearch(hitCount) {
		var sbody = generateEsSearchBody()
		
		client.search({
			index: 'gc',
			type: 'talk',
			size: hitCount,
			body: sbody
		}).then(function (resp) {
			$scope.searcher.results = resp.hits.hits	
			trustHtmlHighlightMarkup()
			console.trace(resp.hits.total)
			console.trace($scope.searcher.results.length)
		}, function (err) {
						
			if (err instanceof esFactory.errors.NoConnections) {
			  $scope.error = new Error('Unable to connect to elasticsearch to fetch previously counted hits. ' +
				'Make sure that it is running and listening at http://localhost:9200')
			}
			console.trace(err.message);
		})
	}
	
	function trustHtmlHighlightMarkup() {
		for (var i=0; i<$scope.searcher.results.length; i++) {
			var result = $scope.searcher.results[i]
			for (var j=0; j<result.highlight.content.length; j++) {
				result.highlight.content[j] = $sce.trustAsHtml(result.highlight.content[j])
			}
		}		
	}
	
	function generateEsSearchBody() {
		
		var sbody = {}
		
		sbody['fields'] = ['title', 'author', 'confid', 'url']
		sbody['query'] = {
						match: {
							content: $scope.searcher.searchTerm
						}
					}
		sbody['highlight'] = {
						  fields : {
							content : {number_of_fragments: 50}
						}
					}
					
		if ($scope.searcher.chosenOrdering.id === 0) {
			sbody['sort'] = { 'talkSortId': { order: 'desc' } }
		}
		
		if ($scope.searcher.chosenOrdering.id === 1) {
			sbody['sort'] = { 'talkSortId': { order: 'asc' } }
		}
		
		return sbody
	}
})