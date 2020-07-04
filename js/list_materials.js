//sample of result: dicts nested in a list
//[{'submission_id': 1, 'material_name': 'Carbon', 'source_data': 'url1'}, {'submission_id': 2, 'material_name': 'Silicon', 'source_data': 'url2'}]
console.log(materials_data_linkam);
console.log(materials_listOfDicts)
//change to query variable sby dictionary otherwise when no. of fields changes, the list index must also be changed :(
  function generateTable(table, data_listOfDicts, materials_data_linkam) {
    for (var i = 0; i < data_listOfDicts.length; ++i) {

       //for each element in the list of dictinaries
      let row = table.insertRow(); //a predefined method of HTMLTableElement 
      let the_submission_id = data_listOfDicts[i].submission_id;
      let the_material_name = data_listOfDicts[i].material_name;
      let the_source_data = data_listOfDicts[i].source_data;
      let cell = row.insertCell();
      let textbox = document.createElement("a"); //make an outerlayer of the text in cell first 
      textbox.href = "/show-material/" + the_submission_id + "/" + the_material_name; //cannot do .href directly for a TextNode :(
      let text = document.createTextNode(the_material_name); //take value of the key
      textbox.appendChild(text);
      cell.appendChild(textbox);

      let cell2 = row.insertCell();
      let textbox2 = document.createElement("b"); //make an outerlayer of the text in cell first 
      let text2 = document.createTextNode(the_source_data); //take value of the key
      textbox2.appendChild(text2);
      cell2.appendChild(textbox2);
      
      let cell3 = row.insertCell();
      let textbox3 = document.createElement("c"); //make an outerlayer of the text in cell first 
      let text3 = document.createTextNode(data_listOfDicts[i].curr_time); //take value of the key
      textbox3.appendChild(text3);
      cell3.appendChild(textbox3);
      }

    for (var i = 0; i < materials_data_linkam.length; ++i) {

       //for each element in the list of dictinaries
      let row = table.insertRow(); //a predefined method of HTMLTableElement 
      let the_submission_id = materials_data_linkam[i].submission_id;
      let the_material_name = materials_data_linkam[i].composition;
      // let the_source_data = materials_data_linkam[i].source_data;
      let cell = row.insertCell();
      let textbox = document.createElement("a"); //make an outerlayer of the text in cell first 
      textbox.href = "/show-material/" + the_submission_id + "/" + the_material_name; //cannot do .href directly for a TextNode :(
      let text = document.createTextNode(the_material_name); //take value of the key
      textbox.appendChild(text);
      cell.appendChild(textbox);

      let cell2 = row.insertCell();
      let textbox2 = document.createElement("b"); //make an outerlayer of the text in cell first 
      let text2 = document.createTextNode("Auto-loaded"); //take value of the key
      textbox2.appendChild(text2);
      cell2.appendChild(textbox2);

      let cell3 = row.insertCell();
      let textbox3 = document.createElement("c"); //make an outerlayer of the text in cell first 
      let text3 = document.createTextNode(materials_data_linkam[i].curr_time); //take value of the key
      textbox3.appendChild(text3);
      cell3.appendChild(textbox3);
      
      }
  
    }
   

  let table = document.querySelector("tbody");
  generateTable(table, materials_listOfDicts, materials_data_linkam);

