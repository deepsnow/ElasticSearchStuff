describe('GC Search trivial search test', function() {
  it('search for one term with one hit', function() {
    browser.get('http://localhost/');

    var el = element(by.model('searcher.searchTerm'))
	el.clear()
	el.sendKeys('rehearsing')
    element(by.css('[value="search"]')).click()

    var resultList = element.all(by.repeater('result in searcher.results'))
    expect(resultList.count()).toEqual(1)
	
    expect(resultList.get(0).getText()).toContain('Neil L. Andersen')
  });
});