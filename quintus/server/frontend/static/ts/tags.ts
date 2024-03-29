import { Module } from "./module.js";
import { postData } from "./request.js";


export class TagModule extends Module{
    tags: string[] = [];
    button: HTMLButtonElement;
    tagInput: HTMLInputElement;
    tagContainer: HTMLElement;

  constructor(url: URL|string|null = null) {
    super('.tags', url);
    const button = this.form.querySelector("button");
    if (button == null){
        alert("Could not find button for ");
        throw new TypeError()
    }
    this.button = button;

    const tagInput = this.form.querySelector('input');
    if (tagInput == null){
        alert();
        throw new TypeError()
    }
    this.tagInput = tagInput;

    const tagContainer = <HTMLElement>this.form.querySelector('.tag-output-container');
    if (tagContainer == null){
        alert();
        throw new TypeError()
    }
    this.tagContainer = tagContainer;

    this.form.addEventListener('submit', (event)=>{
        event.preventDefault();
        let data = {};
        data['material'] = {"tags": {"new": "test", "old": "new"}};
        this.sendData(data);
        this.createTag(this.tagInput.value);
    });

    this.tagInput.addEventListener('keyup', (e) => {
        const { key } = e;
        if (key === ',') {
            this.createTag(tagInput.value.substring(0, tagInput.value.length - 1));
        }
    });

  }

  createTag(tagValue: string) {
    const value = tagValue.trim();

    if (value === '' || this.tags.includes(value)) return;

    const tag = document.createElement('span');
    const tagContent = document.createTextNode(value);
    tag.setAttribute('class', 'tag');
    tag.appendChild(tagContent);

    const close = document.createElement('span');
    close.setAttribute('class', 'remove-tag');
    close.innerHTML = '&#10006;';
    close.onclick = this.handleRemoveTag;

    tag.appendChild(close);
    this.tagContainer.appendChild(tag);
    this.tags.push(value);

    this.tagInput.value = '';
    this.tagInput.focus();
};

handleRemoveTag(e:Event){
    const target = e.target;
    if (target==null){
        throw new Error();
    }
    const tag = (<HTMLElement>target).textContent;
    const item = (<HTMLElement>target).parentElement;
    if (tag==null){
        throw new TypeError("'textContent' in tag is null. Expected string.");
    }
    if (item==null){
        throw new TypeError("'parentElement' for tag is null. Expected HTMLElement.");
    }
    item.remove();
    this.tags.splice(this.tags.indexOf(tag), 1);
};

}
