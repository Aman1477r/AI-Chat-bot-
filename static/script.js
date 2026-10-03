const messageInput =
    document.getElementById("message");

const chat =
    document.getElementById("chat");

const sendButton =
    document.getElementById("sendButton");


let conversationCount = 0;


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


    pages.forEach(function(pageId) {

        const pageElement =
            document.getElementById(pageId);

        if (pageElement) {

            pageElement.classList.remove(
                "active-page"
            );

        }

    });


    const selectedPage =
        document.getElementById(
            page + "Page"
        );


    if (selectedPage) {

        selectedPage.classList.add(
            "active-page"
        );

    }


    document
        .querySelectorAll(".nav-item")
        .forEach(function(item) {

            item.classList.remove(
                "active"
            );

        });


    if (element) {

        element.classList.add(
            "active"
        );

    }


    const titles = {

        chat:
            "AI Assistant",

        agent:
            "AI Agent",

        dashboard:
            "Dashboard",

        settings:
            "Settings"

    };


    document.getElementById(
        "pageTitle"
    ).textContent =
        titles[page];


    if (page === "dashboard") {

        updateDashboard();

    }

}


/* ================================= */
/* SEND MESSAGE */
/* ================================= */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {

        return;

    }


    const welcome =
        document.getElementById(
            "welcome"
        );


    if (welcome) {

        welcome.remove();

    }


    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    autoResize();

    sendButton.disabled = true;


    const typingId =
        showTyping();


    try {

        const response =
            await fetch(
                "/chat",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:
                                message
                        })

                }
            );


        const data =
            await response.json();


        removeTyping(
            typingId
        );


        if (data.error) {

            addMessage(
                "⚠️ " +
                data.error,
                "ai"
            );

        }

        else {

            addMessage(
                data.answer,
                "ai"
            );

            conversationCount++;

        }

    }

    catch (error) {

        removeTyping(
            typingId
        );


        addMessage(
            "⚠️ Unable to connect to the AI server.",
            "ai"
        );


        console.error(error);

    }

    finally {

        sendButton.disabled =
            false;

        messageInput.focus();

    }

}


/* ================================= */
/* ADD MESSAGE */
/* ================================= */

function addMessage(text, type) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        `message-row ${type}`;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        `message-avatar ${
            type === "ai"
                ? "ai-avatar"
                : "user-avatar"
        }`;


    avatar.textContent =
        type === "ai"
            ? "🤖"
            : "👤";


    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${type}`;


    message.textContent =
        text;


    if (type === "ai") {

        row.appendChild(
            avatar
        );

        row.appendChild(
            message
        );

    }

    else {

        row.appendChild(
            message
        );

        row.appendChild(
            avatar
        );

    }


    chat.appendChild(
        row
    );


    scrollToBottom();

}


/* ================================= */
/* TYPING ANIMATION */
/* ================================= */

function showTyping() {

    const id =
        "typing-" +
        Date.now();


    const row =
        document.createElement(
            "div"
        );


    row.className =
        "message-row";


    row.id = id;


    const avatar =
        document.createElement(
            "div"
        );


    avatar.className =
        "message-avatar ai-avatar";


    avatar.textContent =
        "🤖";


    const typing =
        document.createElement(
            "div"
        );


    typing.className =
        "typing";


    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;


    row.appendChild(
        avatar
    );


    row.appendChild(
        typing
    );


    chat.appendChild(
        row
    );


    scrollToBottom();


    return id;

}


function removeTyping(id) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.remove();

    }

}


/* ================================= */
/* SUGGESTION */
/* ================================= */

function useSuggestion(text) {

    messageInput.value =
        text;

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

    document.body.classList.toggle(
        "light"
    );


    const light =
        document.body.classList.contains(
            "light"
        );


    localStorage.setItem(
        "theme",
        light
            ? "light"
            : "dark"
    );


    const checkbox =
        document.getElementById(
            "themeToggle"
        );


    if (checkbox) {

        checkbox.checked =
            light;

    }

}


/* LOAD THEME */

const savedTheme =
    localStorage.getItem(
        "theme"
    );


if (savedTheme === "light") {

    document.body.classList.add(
        "light"
    );

}


/* ================================= */
/* DASHBOARD */
/* ================================= */

function updateDashboard() {

    const counter =
        document.getElementById(
            "conversationCount"
        );


    if (counter) {

        counter.textContent =
            conversationCount;

    }

}


/* ================================= */
/* ENTER TO SEND */
/* ================================= */

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


/* ================================= */
/* TEXTAREA AUTO RESIZE */
/* ================================= */

messageInput.addEventListener(
    "input",
    autoResize
);


function autoResize() {

    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            130
        ) + "px";

}


/* ================================= */
/* SCROLL */
/* ================================= */

function scrollToBottom() {

    const container =
        document.querySelector(
            ".chat-container"
        );


    if (container) {

        container.scrollTo({

            top:
                container.scrollHeight,

            behavior:
                "smooth"

        });

    }

}