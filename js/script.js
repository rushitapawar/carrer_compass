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
            emailInput ? emailInput.value.trim() : "";

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
        const email = emailInput ? emailInput.value.trim() : "";
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

    logoutButton.addEventListener("click", function () {

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
const chatbotButton = document.getElementById("chatbot-button");
const chatbotBox = document.getElementById("chatbot-box");
const closeChat = document.getElementById("close-chat");

const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatMessages = document.getElementById("chat-messages");

chatbotButton.addEventListener("click", function () {
    chatbotBox.style.display = "flex";
    userInput.focus();
});

closeChat.addEventListener("click", function () {
    chatbotBox.style.display = "none";
});

function sendMessage() {

    const message = userInput.value.trim();

    if (message === "") {
        return;
    }

    // Show user's message
    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = message;

    chatMessages.appendChild(userMessage);

    userInput.value = "";

    // Send message to Python
    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {

        const botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.textContent = data.response;

        chatMessages.appendChild(botMessage);

        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(error => {
        console.error(error);

        const botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        botMessage.textContent = "Sorry, something went wrong.";

        chatMessages.appendChild(botMessage);
    });
}

sendButton.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", function (event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});