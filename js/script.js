// ============================================================
// CAREER COMPASS AI - MAIN JAVASCRIPT
// ============================================================


// ============================================================
// LOGIN FORM
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const emailInput =
            document.getElementById("loginEmail");

        const passwordInput =
            document.getElementById("loginPassword");

        const email =
            emailInput ? emailInput.value.trim().toLowerCase() : "";

        const password =
            passwordInput ? passwordInput.value : "";


        // Check empty fields

        if (email === "" || password === "") {

            alert("Please fill in all fields.");

            return;
        }


        try {

            const response = await fetch("/api/login", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    email: email,

                    password: password

                })

            });


            const result = await response.json();


            if (result.success) {

                // Save logged-in user's name
                localStorage.setItem(
                    "loggedInUser",
                    result.name
                );

                alert(result.message);

                // Go to the correct page after login

            if (result.nextPage === "profile") {

                 window.location.href =
                       "./profile.html";

            } else {

                window.location.href =
                         "./dashboard.html";

        }

            } else {

                alert(result.message);

            }


        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            alert(
                "Unable to connect to the server. Please make sure Flask is running."
            );

        }

    });

}

// ============================================================
// GET STARTED BUTTON
// ============================================================

const getStartedButton = document.getElementById("getStarted");

if (getStartedButton) {

    getStartedButton.addEventListener("click", function () {

        window.location.href = "signup.html";

    });

}



// ============================================================
// SIGNUP FORM
// ============================================================

const signupForm = document.getElementById("signupForm");

if (signupForm) {

    signupForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const nameInput = document.getElementById("signupName");
        const emailInput = document.getElementById("signupEmail");
        const passwordInput = document.getElementById("signupPassword");
        const confirmPasswordInput =
            document.getElementById("confirmPassword");

        const name = nameInput ? nameInput.value.trim() : "";
        const email = emailInput ? emailInput.value.trim().toLowerCase() : "";
        const password =
            passwordInput ? passwordInput.value : "";
        const confirmPassword =
            confirmPasswordInput
                ? confirmPasswordInput.value
                : "";


        // Check empty fields
        if (
            name === "" ||
            email === "" ||
            password === "" ||
            confirmPassword === ""
        ) {

            alert("Please fill in all fields.");

            return;
        }


        // Check password length
        if (password.length < 6) {

            alert("Password must contain at least 6 characters.");

            return;
        }


        // Check passwords
        if (password !== confirmPassword) {

            alert("Passwords do not match!");

            return;
        }


        // Split full name into first name and last name
        const nameParts = name.split(/\s+/);

        const firstName = nameParts[0];

        const lastName =
            nameParts.length > 1
                ? nameParts.slice(1).join(" ")
                : "";


        // Last name is required by the backend
        if (lastName === "") {

            alert("Please enter your first name and last name.");

            return;
        }


        try {

            const response = await fetch("/api/signup", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    firstName: firstName,

                    lastName: lastName,

                    email: email,

                    password: password

                })

            });


            const result = await response.json();


            if (result.success) {

                alert(result.message);

                // After successful signup
                window.location.href = "login.html";

            } else {

                alert(result.message);

            }


        } catch (error) {

            console.error("Signup error:", error);

            alert(
                "Unable to connect to the server. Please make sure Flask is running."
            );

        }

    });

}

// ============================================================
// LOAD SAVED PROFILE (GET /api/profile)
// Prefills the profile form from the server so saved data
// comes back after login instead of living only in localStorage.
// ============================================================

async function loadProfileForm() {

    const fullNameInput =
        document.getElementById("fullName");

    const profileFormElement =
        document.getElementById("profileForm");

    /* Only runs on profile.html */
    if (!profileFormElement || !fullNameInput) {
        return;
    }

    let profile = null;

    /* 1) Prefer the profile saved on the server */
    try {

        const response = await fetch("/api/profile");

        if (response.ok) {

            const result = await response.json();

            if (result.success && result.profile) {
                profile = result.profile;
            }

        }

    } catch (error) {

        console.error("Profile load error:", error);

    }

    /* 2) Fallback: saved locally by the existing flow */
    if (!profile) {

        try {
            profile = JSON.parse(
                localStorage.getItem("careerCompassProfile")
            );
        } catch (error) {
            profile = null;
        }

    }

    if (!profile) {
        return;
    }

    function fillIfEmpty(element, value) {

        if (element && !element.value && value) {
            element.value = value;
        }

    }

    function checkRadio(name, value) {

        if (!value) {
            return;
        }

        const radios = document.querySelectorAll(
            'input[name="' + name + '"]'
        );

        radios.forEach(function (radio) {

            if (radio.value === value) {
                radio.checked = true;
            }

        });

    }

    /* Text + select fields */
    fillIfEmpty(fullNameInput, profile.fullName);
    fillIfEmpty(
        document.getElementById("ageGroup"),
        profile.ageGroup
    );
    fillIfEmpty(
        document.getElementById("education"),
        profile.education
    );

    /* Radio groups */
    checkRadio("stream", profile.stream);
    checkRadio("goal", profile.careerGoal);

    /* Interest checkboxes */
    if (Array.isArray(profile.interests)) {

        const interestBoxes = document.querySelectorAll(
            'input[name="interest"]'
        );

        interestBoxes.forEach(function (box) {

            if (profile.interests.indexOf(box.value) !== -1) {
                box.checked = true;
            }

        });

    }

}

loadProfileForm();


// ============================================================
// PROFILE FORM
// ============================================================

const profileForm = document.getElementById("profileForm");

if (profileForm) {

    profileForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        // Get basic information
        const fullName =
            document.getElementById("fullName").value.trim();

        const ageGroup =
            document.getElementById("ageGroup").value;

        const education =
            document.getElementById("education").value;

        // Get stream
        const selectedStream =
            document.querySelector('input[name="stream"]:checked');

        // Get career goal
        const selectedGoal =
            document.querySelector('input[name="goal"]:checked');

        // Get interests
        const selectedInterests =
            document.querySelectorAll(
                'input[name="interest"]:checked'
            );

        // Validation
        if (!fullName || !ageGroup || !education) {
            alert("Please complete your basic profile information.");
            return;
        }

        if (!selectedStream) {
            alert("Please select your education stream.");
            return;
        }

        if (!selectedGoal) {
            alert("Please select your career goal.");
            return;
        }

        if (selectedInterests.length === 0) {
            alert("Please select at least one interest.");
            return;
        }

        // Create profile data
        const profileData = {

            fullName: fullName,

            ageGroup: ageGroup,

            education: education,

            stream: selectedStream.value,

            interests: Array.from(selectedInterests).map(
                item => item.value
            ),

            careerGoal: selectedGoal.value
        };

        console.log("Profile data:", profileData);

        try {

            const response = await fetch(
                "/api/profile",
                {
                    method: "POST",

                    credentials: "include",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(profileData)
                }
            );

            // Read response as text first
            const responseText = await response.text();

            console.log(
                "Profile server response:",
                responseText
            );

          let result;

            try {

                result = JSON.parse(responseText);

            } catch (jsonError) {

                console.error(
                    "REAL SERVER RESPONSE:",
                    responseText
                );

                alert(
                    "FLASK RESPONSE:\n\n" +
                    responseText.substring(0, 1000)
                );

                return;
            }

            // Backend success
            if (response.ok && result.success) {

                localStorage.setItem(
                    "careerCompassProfile",
                    JSON.stringify(profileData)
                );

                alert(
                    "Profile saved! Let's discover your career."
                );

                window.location.href =
                    "questionnaire.html";

                return;
            }

            // Backend error
            alert(
                result.message ||
                "Unable to save your profile."
            );

        } catch (error) {

            console.error(
                "Profile request error:",
                error
            );

            alert(
                "Unable to save the profile. " +
                "Please try again."
            );
        }

    });

}

// ============================================================
// BACK TO HOME BUTTONS
// ============================================================

const homeButtons =
    document.querySelectorAll("[data-home]");

homeButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        window.location.href = "index.html";

    });

});


// ============================================================
// LOGOUT
// ============================================================

const logoutButton =
    document.getElementById("logoutButton");

if (logoutButton) {

    logoutButton.addEventListener("click", async function () {

        /* Clear the server session so protected pages
           actually require a new login. */
        try {

            await fetch("/api/logout", {
                method: "POST"
            });

        } catch (error) {

            console.error("Logout error:", error);

        }

        localStorage.removeItem("careerCompassProfile");

        window.location.href = "index.html";

    });

}


// ============================================================
// MOBILE MENU
// ============================================================

const menuButton =
    document.getElementById("menuButton");

const mobileMenu =
    document.getElementById("mobileMenu");

if (menuButton && mobileMenu) {

    menuButton.addEventListener("click", function () {

        mobileMenu.classList.toggle("active");

    });

}


// ============================================================
// CURRENT YEAR
// ============================================================

const currentYear =
    document.getElementById("currentYear");

if (currentYear) {

    currentYear.textContent =
        new Date().getFullYear();

}


// ============================================================
// END OF SCRIPT
// ============================================================
// ============================================================
// AI CHATBOT
// Works on every page: injects UI if missing, guards nulls,
// falls back to /api/chat if /chat fails.
// ============================================================

function initChatbot() {
    let chatbotButton = document.getElementById("chatbot-button");
    let chatbotBox = document.getElementById("chatbot-box");
    let closeChat = document.getElementById("close-chat");
    let userInput = document.getElementById("user-input");
    let sendButton = document.getElementById("send-button");
    let chatMessages = document.getElementById("chat-messages");

    // Inject chatbot UI on pages that don't have it
    if (!chatbotButton || !chatbotBox) {
        const btn = document.createElement("button");
        btn.id = "chatbot-button";
        btn.textContent = "💬";
        btn.setAttribute("aria-label", "Open chat");
        document.body.appendChild(btn);

        const box = document.createElement("div");
        box.id = "chatbot-box";
        box.innerHTML =
            '<div id="chatbot-header">Career Assistant <span id="close-chat">×</span></div>' +
            '<div id="chat-messages"><div class="bot-message">Hi! I\'m your Career Assistant. How can I help you?</div>' +
            '<div class="chat-quick-options">' +
            '<button class="chat-quick-btn" data-msg="Suggest careers for artistic people">🎨 Artistic careers</button>' +
            '<button class="chat-quick-btn" data-msg="What is investigative?">🔍 What is Investigative?</button>' +
            '<button class="chat-quick-btn" data-msg="How does the assessment work?">📝 Assessment help</button>' +
            '<button class="chat-quick-btn" data-msg="How it works">✨ How it works</button>' +
            '</div></div>' +
            '<div id="chat-input-area"><input type="text" id="user-input" placeholder="Type your message..."><button id="send-button">Send</button></div>';
        document.body.appendChild(box);

        chatbotButton = btn;
        chatbotBox = box;
        closeChat = box.querySelector("#close-chat");
        userInput = box.querySelector("#user-input");
        sendButton = box.querySelector("#send-button");
        chatMessages = box.querySelector("#chat-messages");
    }

    if (!chatbotButton || !chatbotBox || !userInput || !sendButton || !chatMessages) {
        return;
    }

    chatbotButton.addEventListener("click", function () {
        chatbotBox.style.display = "flex";
        userInput.focus();
    });

    if (closeChat) {
        closeChat.addEventListener("click", function () {
            chatbotBox.style.display = "none";
        });
    }

    function addMessage(text, cls) {
        const el = document.createElement("div");
        el.className = cls;
        el.style.whiteSpace = "pre-line";
        el.textContent = text;
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Show quick-option buttons (after every bot reply)
    function showQuickOptions() {
        // Avoid duplicates if user typed instead of clicking
        const old = chatMessages.querySelector(".chat-quick-options");
        if (old) {
            old.remove();
        }
        const wrap = document.createElement("div");
        wrap.className = "chat-quick-options";
        [
            ["🎨 Artistic careers", "Suggest careers for artistic people"],
            ["🔍 What is Investigative?", "What is investigative?"],
            ["📝 Assessment help", "How does the assessment work?"],
            ["✨ How it works", "How it works"]
        ].forEach(function (pair) {
            const b = document.createElement("button");
            b.className = "chat-quick-btn";
            b.textContent = pair[0];
            b.setAttribute("data-msg", pair[1]);
            wrap.appendChild(b);
        });
        chatMessages.appendChild(wrap);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessage() {
        const message = userInput.value.trim();

        if (message === "") {
            return;
        }

        sendText(message);
        userInput.value = "";
    }

    // Send any text (typed or from a quick button)
    function sendText(message) {
        addMessage(message, "user-message");

        // Show typing indicator
        const typing = document.createElement("div");
        typing.className = "bot-message";
        typing.textContent = "Typing...";
        chatMessages.appendChild(typing);

        function postMessage(url) {
            return fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            }).then(function (response) {
                if (!response.ok) {
                    throw new Error("HTTP " + response.status);
                }
                return response.json();
            });
        }

        postMessage("/api/chat")
            .catch(function () {
                return postMessage("/chat");
            })
            .then(function (data) {
                typing.remove();
                addMessage(data.response || "Sorry, I got an empty reply.", "bot-message");
                showQuickOptions();
            })
            .catch(function (error) {
                console.error("Chat error:", error);
                typing.remove();
                addMessage(
                    "Sorry, I can't reach the server. Please make sure Flask (backend/app.py) is running.",
                    "bot-message"
                );
                showQuickOptions();
            });
    }

    sendButton.addEventListener("click", sendMessage);

    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Quick-option buttons: one click = send + answer
    chatMessages.addEventListener("click", function (event) {
        const btn = event.target.closest(".chat-quick-btn");
        if (!btn) {
            return;
        }
        const preset = btn.getAttribute("data-msg") || btn.textContent.trim();
        // Remove the buttons after first use so chat stays clean
        const wrap = btn.closest(".chat-quick-options");
        sendText(preset);
        if (wrap) {
            wrap.remove();
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChatbot);
} else {
    initChatbot();
}