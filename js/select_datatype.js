//create an array of possible data types
let possibleDataTypes = data[instruName] //array of all possible data types of the instrument selected

//--------------------------------------------------------------------
    //add the list of data types
var ul = document.querySelector("#dataName");
for (var i = 0; i < possibleDataTypes.length; i++) {
var chosenDataType = possibleDataTypes[i];
var newItem = document.createElement("li")
newItem.setAttribute('class','list-group-item list-group-item-action'); //allows setting class attribute the to html elemnt created
var aItem = document.createElement("a"); //Document refers to the html code
aItem.textContent = chosenDataType; //creating <a href=".."> movie </a>
aItem.href = "/selected-instru&datatype/" + instruName + "/" + chosenDataType;
newItem.appendChild(aItem);
ul.appendChild(newItem); //ul goes in the html div 
    }
//--------------------------------------------------------------------
