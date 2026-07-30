window.addEventListener("load", () => {

    chrome.runtime.sendMessage({
        url: window.location.href
    });

});

chrome.runtime.onMessage.addListener((request) => {
    if (request.warning) {
        alert(request.warning);
    }
});