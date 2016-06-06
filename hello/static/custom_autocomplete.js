/*
“The contents of this file are subject to the Common Public Attribution
License Version 1.0 (the “License”); you may not use this file except 
in compliance with the License. You may obtain a copy of the License at 
http://www.clusterify.com/files/CODE_LICENSE.txt. The License is based 
on the Mozilla Public License Version 1.1 but Sections 14 and 15 have 
been added to cover use of software over a computer network and provide 
for limited attribution for the Original Developer. In addition, Exhibit 
A has been modified to be consistent with Exhibit B.

Software distributed under the License is distributed on an “AS IS” basis, 
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
for the specific language governing rights and limitations under the 
License.

The Original Code is Clusterify.

The Initial Developer of the Original Code is "the Clusterify.com team", 
which is described at http://www.clusterify.com/about/. All portions of 
the code written by the Initial Developer are Copyright (c) the Initial 
Developer. All Rights Reserved.
*/

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
