// Function to fetch entities from the GET endpoint
async function fetchComponents() {
    const response = await fetch('/api/components');
    const entities = await response.json();
    displayComponents(entities);
}

// Function to display entities in the list
function displayComponents(componentsList) {
    const entityHTMLList = document.getElementById('component-list');
    entityHTMLList.innerHTML = '';
    componentsList.forEach(component => {
        entityHTMLList.appendChild(createComponentHTML(component));
    });
}

function createComponentHTML(componentJSON){
    const componentHTMLItem = document.createElement('div');
    componentHTMLItem.setAttribute('data-json', JSON.stringify(componentJSON));
    componentHTMLItem.classList.add(['component']);
    componentHTMLItem.id = componentJSON.id;
    componentHTMLItem.innerHTML += `
    <div class="main-field row">
        <div class="name">${componentJSON.name}</div>
        <span class="icons">
            <div class="edit-field"><button><i class="nf nf-cod-edit"></i></button></div>
            <div class="expand-field"><i class="nf nf-md-arrow_expand"></i></div>
        </span>
    </div>`;
    componentHTMLItem.onclick = function(){
        showInfo(componentHTMLItem);
        componentJSONtoForm(componentJSON);
    };
    componentHTMLItem.appendChild(createComponentExpandableHTML(componentJSON));
    return componentHTMLItem;
}

function createComponentExpandableHTML(componentJSON) {
    const expandableHTML = document.createElement('div');
    expandableHTML.className = 'expandable-content';
    
    expandableHTML.innerHTML = `<div class="description">${componentJSON.description}</div>`;

    expandableHTML.appendChild(createTagsHTML(componentJSON.tags, false));

    const linksContainerHTML = document.createElement('div');
    linksContainerHTML.style.width= "100%";
    linksContainerHTML.style.display= "flex";
    expandableHTML.appendChild(linksContainerHTML);

    const usedComponentsHTMLList= document.createElement('div');
    usedComponentsHTMLList.classList.add(["links", "components"]);
    usedComponentsHTMLList.style.width = "50%";
    usedComponentsHTMLList.textContent = "Consists of:";
    linksContainerHTML.appendChild(usedComponentsHTMLList);
    const composition = componentJSON.composition;
    if (composition != null) {
        for (var cType in composition){
            const cItem = document.createElement('div');
            cItem.innerHTML = `<a href="#${composition[cType]}">${cType}</a>`;
            usedComponentsHTMLList.appendChild(cItem);
        }
    }

    const usedInComponentsHTMLList= document.createElement('div');
    usedInComponentsHTMLList.classList.add(["links", "compositions"]);
    usedInComponentsHTMLList.style.width = "50%";
    usedInComponentsHTMLList.textContent = "Used in:";
    linksContainerHTML.appendChild(usedInComponentsHTMLList);
    const used_in = componentJSON.used_in;
    if (used_in != null) {
        for (var index in used_in){
            const item = used_in[index];
            const cItem = document.createElement('div');
            cItem.innerHTML = `<a href="#${item['id']}">as ${item['ctype']} in ${item['name']}</a>`;
            usedInComponentsHTMLList.appendChild(cItem);
        }
    }
    return expandableHTML;
}

function componentJSONtoForm(componentJSON) {
    const propertyForm = document.getElementById('property-editor');
    propertyForm.style.display = 'none';
    const form = document.getElementById('component-editor');
    if (form.style.display == 'none'){
        const tagsInput= form.querySelector('.tags input');
        tagsInput.addEventListener("keypress", function(event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
              // Cancel the default action, if needed
              event.preventDefault();
              // Trigger the button element with a click
              const tag = tagsInput.value.trim();
              if (tag) {
                const tagsList = form.querySelector('.tags .container');
                // Add the tag to the tags input value
                tagsList.appendChild(createTagHTML(tag,true));
                tagsInput.value = ''; // Clear the input field
              }
            }
          }); 
    }
    form.style.display = 'block';
    form.querySelector("#id").textContent = componentJSON.id;
    form.querySelector(".name").children[1].value = componentJSON.name;
    form.querySelector(".description").children[1].value = componentJSON.description;

    const tagsElement= form.querySelector('.tags .container');
    tagsElement.innerHTML = '';
    componentJSON.tags.forEach(tag =>{
        tagsElement.appendChild(createTagHTML(tag, true));
    });

    const compositionElement = form.querySelector(".composition .container");
    compositionElement.innerHTML = '';
    const compositionTable = document.createElement('table');
    compositionTable.innerHTML = `
    <tr>
    <th>Component Type</th>
    <th>Component ID</th>
    <th></th>
    </tr>
    `
    compositionElement.appendChild(compositionTable);
    const composition = componentJSON.composition;
    if (composition != null) {
        for (var component_type in composition){
            compositionTable.appendChild(createSubComponentHTML(component_type, composition[component_type]));
        }
    }

    const propertiesElement = form.querySelector(".properties .container");
    propertiesElement.innerHTML = '';
    const propertyTable = document.createElement('table');
    propertyTable.innerHTML = `
    <tr>
    <th>Name</th>
    <th>Value</th>
    <th>Tolerance</th>
    <th>Unit</th>
    <th></th>
    <th></th>
    </tr>
    `
    propertiesElement.appendChild(propertyTable);
    const properties = componentJSON.properties;
    if (properties != null) {
        for (var property_name in properties){
            const property = properties[property_name];
            propertyTable.appendChild(createPropertyShortHTML(property));
        }
    }
}

function createSubComponentHTML(component_type, component_id){
    const componentHTML = document.createElement('tr');
    componentHTML.classList.add('component', 'row');
    componentHTML.innerHTML = `
        <td><input type="text" name="component_type" value="${component_type}"></td>
        <td><input type="text" name="component_id" value="${component_id}"></td>
    `;
    const delete_column = document.createElement('td');
    delete_column.appendChild(createDeleteButtonHTML(componentHTML));
    componentHTML.appendChild(delete_column);
    return componentHTML;
}

function addEmptySubComponent(){
    const result = createSubComponentHTML('', '');
    const form = document.getElementById('component-form');
    const container = form.querySelector('div[class="composition"] > div[class="container"]');
    container.children[0].appendChild(result);
}

function getComponentTypeAndComponentIdFromSubComponentHTML(divElement){
    return [div.children[0].value, div.children[1].value]
}

function createPropertyShortHTML(propertyJSON){
    const propertyHTML = document.createElement('tr');
    propertyHTML.classList.add('property', 'row');
    propertyHTML.id = propertyJSON.id;
    propertyHTML.setAttribute('data-json', JSON.stringify(propertyJSON));
    propertyHTML.innerHTML = `
        <td><span class="name">${propertyJSON.name}</span></td>
        <td><span class="value">${propertyJSON.value}</span></td>
        <td><span class="tolerance">(+${propertyJSON.tolerance.max}/-${propertyJSON.tolerance.min})</span></td>
        <td><span class="unit">[${propertyJSON.unit.unit}]</span></td>`;
    const edit_column = document.createElement('td');
    edit_column.appendChild(createEditButtonHTML(function () {
        propertyJSONtoForm(propertyJSON);
    }));
    propertyHTML.appendChild(edit_column);
    const delete_column = document.createElement('td');
    delete_column.appendChild(createDeleteButtonHTML(propertyHTML));
    propertyHTML.appendChild(delete_column);
    return propertyHTML;
}

function propertyJSONtoForm(propertyJSON){
    const form = document.getElementById('property-editor');
    console.log(propertyJSON);
    form.style.display = 'block';
    const id = form.children[0];
    id.children[1].textContent = propertyJSON.id;
    const name = form.children[1];
    name.children[1].value = propertyJSON.name;
    const value = form.children[4];
    value.children[1].value = propertyJSON.value;
    const unit = form.children[5];
    unit.children[1].value = propertyJSON.unit.unit;

    const tolerance = form.children[8];
    const tolerance_extras = tolerance.children[2];
    if (propertyJSON.tolerance.min == 0 && propertyJSON.tolerance.max == 0){
        tolerance.children[1].checked = false;
        tolerance_extras.style.display = 'none';
    } else {
        tolerance.children[1].checked = true;
        tolerance_extras.style.display = 'block';
    }
    const tolerance_range = tolerance_extras.children[0];
    tolerance_range.children[0].children[1].value = propertyJSON.tolerance.min;
    tolerance_range.children[1].children[1].value = propertyJSON.tolerance.max;

    const source = form.children[11];
    if (propertyJSON.source) {
        source.children[1].value = propertyJSON.source.source_type;
        source.children[4].value = propertyJSON.source.remark;
    } else {
        source.children[1].value = 'UNKNOWN';
        source.children[4].value = '';
    }
    
}

function JSONfromPropertyForm(formID) {
    const form = document.getElementById(formID);
}

function addEmptyPropery(){
    
}

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';  /* Reset height */
    textarea.style.height = textarea.scrollHeight + 'px'; /* Set height to the scroll height */
}

function JSONfromComponentForm(formID) {
    const form = document.getElementById(formID);
    const componentJSON = JSON.parse(form.getAttribute('data-json'));
    componentJSON.name = form.children[1].children[1].value;
    componentJSON.description = form.children[2].children[1].value;
    componentJSON.tags = Array.from(form.children[3].children[2]).map(div=> 
        getTagfromHTML(div)
    );
    Array.from(form.children[3].children[1]).forEach(div => {
        const [ctype, id] = getComponentTypeAndComponentIdFromSubComponentHTML(div)
        componentJSON.composition[ctype] = id;
    });
    Array.from(form.children[4].children[1]).forEach(div => {
        const propertyJSON = JSON.parse(div.getAttribute('data-json'));
        componentJSON.properties[propertyJSON.name] = propertyJSON;
    });
}


function createTagsHTML(tagsList, deletable=true) {
    const tagsHTML= document.createElement('div');
    tagsHTML.className = 'tags';
    const containerHTML= document.createElement('div');
    containerHTML.classList.add("container");
    tagsHTML.appendChild(containerHTML);
    tagsList.forEach(tag =>{
        const tagHTML = document.createElement('span');
        tagHTML.textContent = tag;
        containerHTML.appendChild(createTagHTML(tag, deletable));
    });
    return tagsHTML;
}

function createTagHTML(tagName, deletable=true) {
    const tagHTML = document.createElement('div');
    tagHTML.classList.add('tag', 'inline');
    const tagNameHTML =  document.createElement('span');
    tagNameHTML.className = "name";
    tagNameHTML.textContent = tagName;
    tagHTML.appendChild(tagNameHTML);
    if (deletable) {
        tagHTML.appendChild(createDeleteButtonHTML(tagHTML));
    }
    return tagHTML;
}

function getTagfromHTML(divElement) {
    return divElement.children[0].textContent;
}

function createAddButtonHTML(add_func){
    const addHTML = document.createElement('button');
    addHTML.className = "add";
    addHTML.innerHTML = '<i class="nf nf-cod-diff_added"></i></button>';
    addHTML.onclick = add_func;
    return addHTML;
}

function createEditButtonHTML(edit_func){
    const editHTML = document.createElement('button');
    editHTML.className = "edit";
    editHTML.innerHTML = '<i class="nf nf-cod-edit"></i></button>';
    editHTML.onclick = edit_func;
    return editHTML;
}

function createExpandButtonHTML(expand_func){
    const deleteHTML = document.createElement('button');
    deleteHTML.className = "expand";
    deleteHTML.innerHTML = '<i class="nf nf-md-arrow_expand"></i></button>';
    deleteHTML.onclick = expand_func;
    return deleteHTML;
}

function createDeleteButtonHTML(parent){
    const deleteHTML = document.createElement('button');
    deleteHTML.className = "delete";
    deleteHTML.innerHTML = '<i class="nf nf-oct-trash"></i></button>';
    deleteHTML.onclick = function(){parent.remove()};
    return deleteHTML;
}

// Function to filter entities based on search input
function filterEntities() {
    const searchInput = document.getElementById('search-bar').value.toLowerCase();
    const listItems = document.querySelectorAll('#component-list div');
    listItems.forEach(item => {
        if (item.textContent.toLowerCase().includes(searchInput)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function showInfo(element) {
    const info = element.querySelector('.expandable-content');
    const icon = element.querySelector('.expand-field');
    if (info.style.display === 'none' || info.style.display === '') {
        info.style.display = 'block';
        icon.innerHTML = '<i class="nf nf-md-arrow_collapse"></i>';
    } else {
        info.style.display = 'none';
        icon.innerHTML = '<i class="nf nf-md-arrow_expand"></i>';
    }
}

function toggleDisplay(id){
    const element = document.getElementById(id);
    if (element.style.display == 'none') {
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

