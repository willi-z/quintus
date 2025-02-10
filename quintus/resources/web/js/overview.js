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
    <div class="main-field">
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
    expandableHTML.appendChild(linksContainerHTML);

    const usedComponentsHTMLList= document.createElement('div');
    usedComponentsHTMLList.classList.add(["links", "components"]);
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
    const form = document.getElementById('component-form');
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
    form.querySelector(".id").value = componentJSON.id;
    form.querySelector(".name").children[1].value = componentJSON.name;
    form.querySelector(".description").children[1].value = componentJSON.description;

    const tagsElement= form.querySelector('.tags .container');
    tagsElement.innerHTML = '';
    componentJSON.tags.forEach(tag =>{
        tagsElement.appendChild(createTagHTML(tag, true));
    });

    const compositionElement = form.querySelector(".composition .container");
    compositionElement.innerHTML = '';
    const composition = componentJSON.composition;
    if (composition != null) {
        for (var component_type in composition){
            compositionElement.appendChild(createSubComponentHTML(component_type, composition[component_type]));
        }
    }

    const propertiesElement = form.querySelector(".properties .container");
    propertiesElement.innerHTML = '';
    const properties = componentJSON.properties;
    if (properties != null) {
        for (var property_name in properties){
            const property = properties[property_name];
            propertiesElement.appendChild(createPropertyShortHTML(property));
        }
    }
}

function createSubComponentHTML(component_type, component_id){
    const componentHTML = document.createElement('div');
    componentHTML.className = "component";
    componentHTML.innerHTML = `
        <input type="text" name="component_type" value="${component_type}">
        <input type="text" name="component_id" value="${component_id}">
    `;
    componentHTML.appendChild(createDeleteButtonHTML(componentHTML));
    return componentHTML;
}

function getComponentTypeAndComponentIdFromSubComponentHTML(divElement){
    return [div.children[0].value, div.children[1].value]
}

function createPropertyShortHTML(propertyJSON){
    const propertyHTML = document.createElement('div');
    propertyHTML.setAttribute('data-json', JSON.stringify(propertyJSON));
    propertyHTML.innerHTML = `
        <span class="name">${propertyJSON.name}</span>
        <span class="value">${propertyJSON.value}</span>
        <span class="tolerance">(+${propertyJSON.tolerance.max}/-${propertyJSON.tolerance.min})</span>
        <span class="unit">[${propertyJSON.unit.unit}]</span>`;
    propertyHTML.appendChild(createEditButtonHTML(null));
    propertyHTML.appendChild(createDeleteButtonHTML(propertyHTML));
    return propertyHTML;
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
    tagsList.forEach(tag =>{
        const tagHTML = document.createElement('span');
        tagHTML.textContent = tag;
        tagsHTML.appendChild(createTagHTML(tag, deletable));
    });
    return tagsHTML;
}

function createTagHTML(tagName, deletable=true) {
    const tagHTML = document.createElement('div');
    tagHTML.className = "tag";
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


