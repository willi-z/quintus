import { postData } from "./request.js";


export class Module {
    name: string;
    form: HTMLFormElement;
    url: URL|string;
    modules: Module[];

    constructor (name: string, url: URL|string|null = null, modules: Module[] = null) {
        this.name = name;
        if (url == null) {
            url = document.URL
        }
        this.url = url;

        if (modules == null) {
            modules = [];
        }
        this.modules = modules;

        const form = document.querySelector(name);
        if (form == null) {
            alert(`Could not find FORM with class '${this.name}' for ${typeof(this)}.`);
            throw new TypeError("Form is 'null'! Expected type 'Element'.");
        }
        this.form = (<HTMLFormElement>form)
    }

    async sendData(data: any): Promise<void> {
        const [status, response] = await postData(this.url, data);
        console.log(response);
        if (status < 300) {
            this.successfullRequest(response);
            for (const module of this.modules){
                module.successfullRequest(response)
            }
        } else {
            this.unsuccessfullRequest(response);
            for (const module of this.modules){
                module.unsuccessfullRequest(response)
            }
        }
    }

    /**
    @abstract
    */
    successfullRequest(response: any): void{
        throw new Error('Method is not implemented!')
    }

    /**
    @abstract
    */
    unsuccessfullRequest(response: any): void{
        throw new Error('Method is not implemented!')
    }
}
