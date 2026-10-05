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


        // ====================================================
        // GET FORM VALUES
        // ====================================================

        const fullNameInput =
            document.getElementById("fullName");

        const ageGroupInput =
            document.getElementById("ageGroup");

        const educationInput =
            document.getElementById("education");


        const fullName =
            fullNameInput
                ? fullNameInput.value.trim()
                : "";

        const ageGroup =
            ageGroupInput
                ? ageGroupInput.value
                : "";

        const education =
            educationInput
                ? educationInput.value
                : "";


        // ====================================================
        // CHECK BASIC INFORMATION
        // ====================================================

        if (
            fullName === "" ||
            ageGroup === "" ||
            education === ""
        ) {

            alert(
                "Please complete your basic profile information."
            );

            return;
        }


        // ====================================================
        // GET EDUCATION STREAM
        // ====================================================

        const selectedStream =
            document.querySelector(
                'input[name="stream"]:checked'
            );


        if (!selectedStream) {

            alert(
                "Please select your education stream."
            );

            return;
        }


        // ====================================================
        // GET CAREER GOAL
        // ====================================================

        const selectedGoal =
            document.querySelector(
                'input[name="goal"]:checked'
            );


        if (!selectedGoal) {

            alert(
                "Please select your career goal."
            );

            return;
        }


        // ====================================================
        // GET INTERESTS
        // ====================================================

        const selectedInterests =
            document.querySelectorAll(
                'input[name="interest"]:checked'
            );


        if (selectedInterests.length === 0) {

            alert(
                "Please select at least one interest."
            );

            return;
        }


        const interests =
            Array.from(selectedInterests)
                .map(function (item) {
                    return item.value;
                });


        // ====================================================
        // CREATE PROFILE DATA
        // ====================================================

        const profileData = {

            fullName: fullName,

            ageGroup: ageGroup,

            education: education,

            stream: selectedStream.value,

            interests: interests,

            careerGoal: selectedGoal.value

        };


        // ====================================================
        // SEND PROFILE TO FLASK
        // ====================================================

        try {

            const response = await fetch(
                "/api/profile",
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(profileData)

                }
            );


            const result = await response.json();


            // =================================================
            // SUCCESS
            // =================================================

            if (result.success) {

                // Keep a temporary copy for the frontend
                localStorage.setItem(
                    "careerCompassProfile",
                    JSON.stringify(profileData)
                );


                alert(
                    "Profile saved! Let's discover your career."
                );


                // Continue to questionnaire
                window.location.href =
                    "questionnaire.html";

            }


            // =================================================
            // ERROR
            // =================================================

            else {

                alert(result.message);

            }


        } catch (error) {

            console.error(
                "Profile error:",
                error
            );

            alert(
                "Unable to connect to the server. Please make sure Flask is running."
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