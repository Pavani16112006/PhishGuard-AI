chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

    if (message.action !== "analyze") {
        return;
    }

    chrome.tabs.query(
        { active: true, currentWindow: true },
        (tabs) => {

            if (!tabs || !tabs[0]) {
                sendResponse({
                    prediction: "Error",
                    risk: 0,
                    confidence: 0,
                    reasons: ["Could not find the active tab."]
                });

                return;
            }

            const tabId = tabs[0].id;

            chrome.tabs.sendMessage(
                tabId,
                { action: "getWebsiteData" },
                (websiteData) => {

                    if (chrome.runtime.lastError) {

                        console.error(
                            chrome.runtime.lastError.message
                        );

                        sendResponse({
                            prediction: "Error",
                            risk: 0,
                            confidence: 0,
                            reasons: [
                                "Could not access this webpage."
                            ]
                        });

                        return;
                    }

                    fetch("http://127.0.0.1:8000/analyze", {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify(websiteData)

                    })
                    .then(response => {

                        if (!response.ok) {
                            throw new Error(
                                `Backend returned ${response.status}`
                            );
                        }

                        return response.json();

                    })
                    .then(data => {

                        sendResponse(data);

                    })
                    .catch(error => {

                        console.error(
                            "Backend error:",
                            error
                        );

                        sendResponse({
                            prediction: "Backend Offline",
                            risk: 0,
                            confidence: 0,
                            reasons: [
                                "Could not connect to the PhishGuard AI backend."
                            ]
                        });

                    });
                }
            );
        }
    );

    return true;
});