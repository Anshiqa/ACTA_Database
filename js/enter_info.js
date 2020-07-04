


//update the Instrument: string in the html
var ug = document.querySelector("#chosenInstru");
var myItem = document.createElement("h5");
myItem.textContent = "Instrument: " + chosenInstru;
ug.appendChild(myItem);
var newItem = document.createElement("h5");
newItem.textContent = "Data Type: " + chosenDataType;
ug.appendChild(newItem);


// //update the Chosen Data: string in the html
// var ul = document.querySelector("#chosenData");
// var newItem = document.createElement("h5");
// newItem.textContent = "Data Type: " + chosenDataType;
// ul.appendChild(newItem);


