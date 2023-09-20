import { postData } from "./request.js";
export class Module {
    constructor(name, url = null) {
        this.name = name;
        if (url == null) {
            url = document.URL;
        }
        this.url = url;
        const form = document.querySelector(name);
        if (form == null) {
            alert(`Could not find FORM with class '${this.name}' for ${typeof (this)}.`);
            throw new TypeError("Form is 'null'! Expected type 'Element'.");
        }
        this.form = form;
    }
    async sendData(data) {
        const [status, response] = await postData(this.url, data);
        console.log(response);
        if (status < 300) {
            this.successfullRequest(response);
        }
        else {
            this.unsuccessfullRequest(response);
        }
    }
    /**
    @abstract
    */
    successfullRequest(response) {
        throw new Error('Method is not implemented!');
    }
    /**
    @abstract
    */
    unsuccessfullRequest(response) {
        throw new Error('Method is not implemented!');
    }
}
//# sourceMappingURL=module.js.map
