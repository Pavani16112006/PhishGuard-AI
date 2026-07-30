console.log("Background started");

let blacklist = new Set();

// Load blacklist
fetch(chrome.runtime.getURL("blacklist.json"))
.then(res => res.json())
.then(data => {

    blacklist = new Set(data);

    console.log("Blacklist loaded");

});

// Rule checking
function checkRules(url) {

    let score = 0;
    let reasons = [];

    if (url.length > 60) {
        score++;
        reasons.push("Long URL");
    }

    if (url.includes("@")) {
        score += 2;
        reasons.push("Contains @");
    }

    if (/login|verify|update|bank|secure/.test(url)) {
        score++;
        reasons.push("Suspicious keyword");
    }

    if (url.startsWith("http://")) {
        score++;
        reasons.push("HTTP not secure");
    }

    return { score, reasons };
}

// Main detection
chrome.runtime.onMessage.addListener((request, sender) => {

    let url = request.url;

    let hostname = new URL(url).hostname.replace("www.", "");

    // Blacklist check
    if (blacklist.has(hostname)) {

        chrome.tabs.sendMessage(sender.tab.id, {
            warning: "⚠ BLACKLISTED SITE"
        });

        return;
    }

    // Rule-based check
    let result = checkRules(url);

    if (result.score >= 2) {

        chrome.tabs.sendMessage(sender.tab.id, {
            warning: "⚠ Phishing Warning\n" + result.reasons.join("\n")
        });

    }

});