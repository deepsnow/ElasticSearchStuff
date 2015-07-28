angular.module('gcApp', [])
.controller('gcEsSearch', function($scope) {
	
	$scope.searcher = {};
	$scope.searcher.searchTerm = "enter search term";
	$scope.searcher.results = [];
	
	$scope.searcher.search = function () {
		
	};
	
});