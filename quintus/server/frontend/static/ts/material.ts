import { NameModule } from "./name.js";
import { TagModule } from "./tags.js";


// new NameModule();
// new TagModule();

console.log(document.URL.endsWith("new"))
if (document.URL.endsWith("new")){
    console.log("Creates a new Material");
} else{
    var url_elements = document.URL.split('/');
    var collection = url_elements[url_elements.length -2];
    var document_id = url_elements[url_elements.length -1];
    console.log(`Collection: '${collection}', Document: '${document_id}'`);
}
