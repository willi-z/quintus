export class Editable {
    constructor(parent, presentID = ".presentor", editableID = ".editor", editButtonID = '#edit-button') {
        const presentFind = parent.querySelector(presentID);
        if (presentFind == null) {
            alert(`Could not find static Element. Searched for class '${presentID}' in ${parent.nodeName}`);
            throw new TypeError("Static Element is 'null'. Expected type: 'Element'");
        }
        const editabelFind = parent.querySelector(editableID);
        if (editabelFind == null) {
            alert(`Could not find editable Element. Searched for class '${editableID}' in ${parent.nodeName}`);
            throw new TypeError("Editabel Element is 'null'. Expected type: 'Element'");
        }
        this.presentElem = presentFind;
        this.editabelElem = editabelFind;
        const button = this.presentElem.querySelector(editButtonID);
        if (button == null) {
            alert(`Could not find button Element. Searched for class '${editButtonID}' in ${parent.nodeName}`);
            throw new TypeError("Edit-Button is 'null'. Expected type: 'Element'");
        }
        this.editButton = button;
        var self = this;
        this.editButton.addEventListener('click', () => { this.enableEdit(self); });
    }
    enableEdit(main) {
        main.presentElem.classList.add('hidden');
        main.editabelElem.classList.remove('hidden');
    }
    present(content) {
        const output = this.presentElem.querySelector(".output");
        output.innerHTML = content;
        this.editabelElem.classList.add('hidden');
        this.presentElem.classList.remove('hidden');
    }
    getValue() {
        var input = this.editabelElem.querySelector("input");
        return input.value;
    }
}
//# sourceMappingURL=editable.js.map
