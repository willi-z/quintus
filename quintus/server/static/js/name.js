import { Editable } from "./editable.js";
import { Module } from "./module.js";
export class NameModule extends Module {
    constructor(url = null) {
        super('.name', url);
        this.editable = new Editable(this.form);
        this.form.addEventListener('submit', (event) => {
            event.preventDefault();
            let data = { "name": this.editable.getValue() };
            this.sendData(data);
        });
    }
    successfullRequest(response) {
        this.editable.present(response["name"]);
    }
}
//# sourceMappingURL=name.js.map
