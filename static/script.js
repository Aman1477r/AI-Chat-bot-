
const messageInput = document.getElementById("message");
const chat = document.getElementById("chat");
const sendButton = document.getElementById("sendButton");

const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const previewImage = document.getElementById("previewImage");
const imageFileName = document.getElementById("imageFileName");
const removeImageButton = document.getElementById("removeImage");

let conversationCount = 0;
let selectedImage = null;
let previewObjectUrl = null;

/* ================================= */
/* PAGE NAVIGATION */
/* ================================= */

function showPage(page, element) {
    const pages = [
        "chatPage",
        "agentPage",
        "dashboardPage",
        "settingsPage"
    ];

    pages.forEach(function (pageId) {
        const pageElement = document.getElementById(pageId);

        if (pageElement) {
            pageElement.classList.remove("active-page");
        }
    });

    const selectedPage = document.getElementById(page + "Page");

    if (selectedPage) {
        selectedPage.classList.add("active-page");
    }

    document.querySelectorAll(".nav-item").forEach(function (item) {
        item.classList.remove("active");
    });

    if (element) {
        element.classList.add("active");
    }

    const titles = {
        chat: "AI Assistant",
        agent: "AI Agent",
        dashboard: "Dashboard",
        settings: "Settings"
    };

    const pageTitle = document.getElementById("pageTitle");

    if (pageTitle) {
        pageTitle.textContent = titles[page] || "AI Assistant";
    }

    if (page === "dashboard") {
        updateDashboard();
    }
}

/* ================================= */
/* IMAGE UPLOAD AND PREVIEW */
/* ================================= */

function clearSelectedImage() {
    selectedImage = null;

    if (previewObjectUrl) {
        URL.revokeObjectURL(previewObjectUrl);
        previewObjectUrl = null;
    }

    if (imageInput) {
        imageInput.value = "";
    }

    if (previewImage) {
        previewImage.removeAttribute("src");
    }

    if (imageFileName) {
        imageFileName.textContent = "";
    }

    if (imagePreview) {
        imagePreview.hidden = true;
        imagePreview.style.display = "none";
    }
}

if (imageInput) {
    imageInput.addEventListener("change", function () {
        const file = imageInput.files && imageInput.files[0];

        if (!file) {
            clearSelectedImage();
            return;
        }

        const allowedTypes = ["image/jpeg", "image/png"];
        const maxSize = 5 * 1024 * 1024;

        if (!allowedTypes.includes(file.type)) {
            alert("Please select a JPG or PNG image.");
            clearSelectedImage();
            return;
        }

        if (file.size > maxSize) {
            alert("Image size must be 5 MB or less.");
            clearSelectedImage();
            return;
        }

        selectedImage = file;

        if (previewObjectUrl) {
            URL.revokeObjectURL(previewObjectUrl);
        }

        previewObjectUrl = URL.createObjectURL(file);

        if (previewImage) {
            previewImage.src = previewObjectUrl;
            previewImage.alt = "Selected image preview";
        }

        if (imageFileName) {
            imageFileName.textContent = file.name;
        }

        if (imagePreview) {
            imagePreview.hidden = false;
            imagePreview.style.display = "flex";
        }

        messageInput.focus();
    });
}

if (removeImageButton) {
    removeImageButton.addEventListener("click", function () {
        clearSelectedImage();
    });
}

/* ================================= */
/* SEND MESSAGE */
/* ================================= */

async function sendMessage() {
    const message = messageInput.value.trim();

    if ((!message && !selectedImage) || sendButton.disabled) {
        return;
    }

    const welcome = document.getElementById("welcome");

    if (welcome) {
        welcome.remove();
    }

    // Show the user's question and selected image in the chat.
    addMessage(message || "Please describe this image.", "user");

    if (selectedImage) {
        addImageMessage(selectedImage);
    }

    const outgoingImage = selectedImage;

    messageInput.value = "";
    autoResize();
    sendButton.disabled = true;

    const typingId = showTyping();

    try {
        let response;

        if (outgoingImage) {
            // FormData allows the browser to upload the image file.
            const formData = new FormData();

            formData.append("message", message);
            formData.append("image", outgoingImage);

            response = await fetch("/chat", {
                method: "POST",
                body: formData
            });

            // Clear the preview once the upload has been sent.
            clearSelectedImage();
        } else {
            // Keep JSON requests for normal text-only messages.
            response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            });
        }

        const data = await response.json();

        removeTyping(typingId);

        if (!response.ok || data.error) {
            addMessage(
                "⚠️ " +
                (data.error || "Something went wrong. Please try again."),
                "ai"
            );
        } else {
            addMessage(
                data.answer || "I couldn't generate a response.",
                "ai"
            );

            conversationCount++;
            updateDashboard();
        }
    } catch (error) {
        removeTyping(typingId);

        addMessage(
            "⚠️ Unable to connect to the AI server.",
            "ai"
        );

        console.error("Chat error:", error);
    } finally {
        sendButton.disabled = false;
        messageInput.focus();
    }
}

/* ================================= */
/* DISPLAY IMAGE IN CHAT */
/* ================================= */

function addImageMessage(file) {
    const row = document.createElement("div");
    row.className = "message-row user";

    const message = document.createElement("div");
    message.className = "message user";

    const image = document.createElement("img");
    image.className = "chat-image";
    image.alt = "Uploaded image";
    image.loading = "lazy";

    const objectUrl = URL.createObjectURL(file);
    image.src = objectUrl;

    image.addEventListener("load", function () {
        scrollToBottom();
    });

    image.addEventListener("error", function () {
        image.alt = "Image preview unavailable";
    });

    message.appendChild(image);
    row.appendChild(message);

    const avatar = document.createElement("div");
    avatar.className = "message-avatar user-avatar";
    avatar.textContent = "👤";
    row.appendChild(avatar);

    chat.appendChild(row);
    scrollToBottom();
}

/* ================================= */
/* SAFE ANSWER FORMATTING + LINKS */
/* ================================= */

function escapeHTML(text) {
    return String(text).replace(/[&<>"']/g, function (char) {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[char];
    });
}

function makeSafeLinks(text) {
    const escaped = escapeHTML(text);

    // Convert Markdown links: [title](https://example.com)
    const markdownLinks = escaped.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/gi,
        function (match, label, url) {
            const safeUrl = url.replace(/&amp;/g, "&");

            return (
                '<a href="' +
                safeUrl.replace(/&/g, "&amp;").replace(/"/g, "&quot;") +
                '" target="_blank" rel="noopener noreferrer">' +
                label +
                "</a>"
            );
        }
    );

    // Convert plain HTTP/HTTPS links, without linking inside anchors.
    return markdownLinks.replace(
        /(^|[\s>])(https?:\/\/[^\s<]+)/gi,
        function (match, prefix, url, offset, fullText) {
            let cleanUrl = url;
            let punctuation = "";

            while (/[.,!?;:)\]]$/.test(cleanUrl)) {
                punctuation = cleanUrl.slice(-1) + punctuation;
                cleanUrl = cleanUrl.slice(0, -1);
            }

            const before = fullText.slice(0, offset);

            if (
                before.lastIndexOf("<a ") >
                before.lastIndexOf("</a>")
            ) {
                return match;
            }

            const safeUrl = cleanUrl.replace(/&amp;/g, "&");

            return (
                prefix +
                '<a href="' +
                safeUrl.replace(/&/g, "&amp;").replace(/"/g, "&quot;") +
                '" target="_blank" rel="noopener noreferrer">' +
                cleanUrl +
                "</a>" +
                punctuation
            );
        }
    );
}

function renderAnswer(text) {
    let formatted = makeSafeLinks(String(text));
    formatted = formatted.replace(/\r\n|\r|\n/g, "<br>");
    return formatted;
}

/* ================================= */
/* ADD MESSAGE */
/* ================================= */

function addMessage(text, type) {
    const row = document.createElement("div");
    row.className = `message-row ${type}`;

    const avatar = document.createElement("div");
    avatar.className = `message-avatar ${
        type === "ai" ? "ai-avatar" : "user-avatar"
    }`;

    avatar.textContent = type === "ai" ? "🤖" : "👤";

    const message = document.createElement("div");
    message.className = `message ${type}`;

    if (type === "ai") {
        message.innerHTML = renderAnswer(text);
    } else {
        message.textContent = text;
    }

    if (type === "ai") {
        row.appendChild(avatar);
        row.appendChild(message);
    } else {
        row.appendChild(message);
        row.appendChild(avatar);
    }

    chat.appendChild(row);
    scrollToBottom();
}

/* ================================= */
/* TYPING ANIMATION */
/* ================================= */

function showTyping() {
    const id = "typing-" + Date.now();

    const row = document.createElement("div");
    row.className = "message-row";
    row.id = id;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar ai-avatar";
    avatar.textContent = "🤖";

    const typing = document.createElement("div");
    typing.className = "typing";

    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    row.appendChild(avatar);
    row.appendChild(typing);

    chat.appendChild(row);
    scrollToBottom();

    return id;
}

function removeTyping(id) {
    const element = document.getElementById(id);

    if (element) {
        element.remove();
    }
}

/* ================================= */
/* SUGGESTIONS */
/* ================================= */

function useSuggestion(text) {
    messageInput.value = text;
    autoResize();
    messageInput.focus();
}

/* ================================= */
/* NEW CHAT */
/* ================================= */

function newChat() {
    location.reload();
}

/* ================================= */
/* THEME */
/* ================================= */

function toggleTheme() {
    document.body.classList.toggle("light");

    const light = document.body.classList.contains("light");

    localStorage.setItem("theme", light ? "light" : "dark");

    const checkbox = document.getElementById("themeToggle");

    if (checkbox) {
        checkbox.checked = light;
    }
}

const savedTheme = localStorage.getItem("theme");

if (savedTheme === "light") {
    document.body.classList.add("light");
}

/* ================================= */
/* DASHBOARD */
/* ================================= */

function updateDashboard() {
    const counter = document.getElementById("conversationCount");

    if (counter) {
        counter.textContent = conversationCount;
    }
}

/* ================================= */
/* ENTER TO SEND */
/* ================================= */

messageInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

/* ================================= */
/* TEXTAREA AUTO RESIZE */
/* ================================= */

messageInput.addEventListener("input", autoResize);

function autoResize() {
    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 130) + "px";
}

/* ================================= */
/* SCROLL */
/* ================================= */

function scrollToBottom() {
    const container = document.querySelector(".chat-container");

    if (container) {
        container.scrollTo({
            top: container.scrollHeight,
            behavior: "smooth"
        });
    }
}
