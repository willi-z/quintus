import { Editable } from "./editable.js";
import { Module } from "./module.js";


export class NameModule extends Module{
  editable: Editable;

  constructor(url: URL|string|null = null) {
    super('.name', url);

    this.editable = new Editable(this.form);

    this.form.addEventListener('submit', (event)=>{
        event.preventDefault();
        let data = {"name": this.editable.getValue()};
        this.sendData(data);
    });
  }

  successfullRequest(response: any): void {
    this.editable.present(response["name"]);
  }
}
