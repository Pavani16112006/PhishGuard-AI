function collectWebsiteData() {

    const url = window.location.href;

    const title = document.title;

    const text = document.body
        ? document.body.innerText
            .replace(/\s+/g, " ")
            .trim()
            .substring(0, 5000)
        : "";

    const hasPasswordField =
        document.querySelector(
            'input[type="password"]'
        ) !== null;

    const forms = document.forms.length;

    const externalLinks = [...document.links].filter(link => {

        try {
            return (
                link.hostname &&
                link.hostname !== window.location.hostname
            );
        } catch {
            return false;
        }

    }).length;

    const isHttps =
        window.location.protocol === "https:";

    let metaDescription = "";

    const meta = document.querySelector(
        'meta[name="description"]'
    );

    if (meta) {
        metaDescription = meta.content || "";
    }

    return {
        url,
        title,
        text,
        hasPasswordField,
        forms,
        externalLinks,
        isHttps,
        metaDescription
    };
}


chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.action === "getWebsiteData") {

            sendResponse(
                collectWebsiteData()
            );
        }

        return true;
    }
);