export function sendForm(form, action, endpoint, callback) {
    const formData = new FormData(form);
    const dataJSON = JSON.stringify(Object.fromEntries(formData));
    const request = new XMLHttpRequest();
    request.onreadystatechange = () => {
        if (request.readyState === 4) {
            callback(request.response, form);
        }
    };
    request.open(action, endpoint);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(dataJSON);
}
export function getData(endpoint, callback) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = () => {
        if (request.readyState === 4) {
            callback(request.response);
        }
    };
    request.open("GET", endpoint);
    request.send();
}
export async function postData(url, data) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: "POST",
        mode: "cors",
        cache: "no-cache",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: "follow",
        referrerPolicy: "no-referrer",
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    });
    return [response.status, response.json()]; // parses JSON response into native JavaScript objects
}
//# sourceMappingURL=request.js.map
