const websiteURL =
    document.getElementById("websiteURL");

const scanButton =
    document.getElementById("scanButton");

const prediction =
    document.getElementById("prediction");

const risk =
    document.getElementById("risk");

const confidence =
    document.getElementById("confidence");

const reasons =
    document.getElementById("reasons");


let currentTab = null;


chrome.tabs.query(
    { active: true, currentWindow: true },
    (tabs) => {

        if (!tabs || !tabs[0]) {
            websiteURL.textContent =
                "Unable to detect current tab.";
            return;
        }

        currentTab = tabs[0];

        websiteURL.textContent =
            currentTab.url || "Unknown";
    }
);


scanButton.addEventListener("click", () => {

    if (!currentTab) {
        prediction.textContent =
            "No active website found.";
        return;
    }

    prediction.textContent =
        "Analyzing...";

    risk.textContent = "--";

    confidence.textContent = "--";

    reasons.innerHTML = "";

    scanButton.disabled = true;
    scanButton.textContent = "Analyzing...";


    chrome.runtime.sendMessage(
        {
            action: "analyze",
            url: currentTab.url
        },
        (response) => {

            scanButton.disabled = false;
            scanButton.textContent =
                "Analyze Website";


            if (chrome.runtime.lastError) {

                prediction.textContent =
                    "Extension error";

                reasons.innerHTML =
                    `<li>${chrome.runtime.lastError.message}</li>`;

                return;
            }


            if (!response) {

                prediction.textContent =
                    "Backend not responding.";

                return;
            }


            prediction.textContent =
                response.prediction || "Unknown";


            risk.textContent =
                response.risk !== undefined
                    ? response.risk + "%"
                    : "--";


            confidence.textContent =
                response.confidence !== undefined
                    ? response.confidence + "%"
                    : "--";


            reasons.innerHTML = "";


            if (Array.isArray(response.reasons)) {

                response.reasons.forEach(reason => {

                    const li =
                        document.createElement("li");

                    li.textContent = reason;

                    reasons.appendChild(li);
                });
            }


            prediction.className = "";


            if (response.prediction === "Safe") {

                prediction.classList.add("safe");

            } else if (
                response.prediction === "Suspicious"
            ) {

                prediction.classList.add("warning");

            } else if (
                response.prediction === "Phishing"
            ) {

                prediction.classList.add("danger");
            }
        }
    );
});