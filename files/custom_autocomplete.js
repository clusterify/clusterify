function lastWord (str) {
	var words = str.split(" ");
	return words[words.length - 1];
}

function customTemplate(str) {
	return "<li>" + lastWord(str) + "</li>";
}

function customTextInsert(str, original) {
	var firstWords = original.split(" ");
	firstWords[firstWords.length - 1] = str;
	var toReturn = firstWords.join(" ");
	return toReturn;
}

function customTextInsertBinder(input) {
	return function(str){ return customTextInsert(str, input.val()); }
}

function customTextMatch(typed) {
	return this.match(new RegExp(lastWord(typed)));
}
