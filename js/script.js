// ============================================================
// CAREER COMPASS AI - MAIN JAVASCRIPT
// ============================================================


// ============================================================
// LOGIN FORM
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const emailInput = document.getElementById("loginEmail");
        const passwordInput = document.getElementById("loginPassword");

        const email = emailInput ? emailInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value.trim() : "";

        if (email === "" || password === "") {

            alert("Please fill in all fields.");

            return;
        }

        alert("Login successful!");

        // Login ke baad profile page
        window.location.href = "profile.html";

    });

}


// ============================================================
// GOOGLE LOGIN BUTTON
// ============================================================

const googleButton = document.getElementById("googleLogin");

if (googleButton) {

    googleButton.addEventListener("click", function () {

        // Abhi frontend demo hai.
        // Backend / Google OAuth baad mein connect karenge.

        alert("Google login will be connected later.");

        window.location.href = "profile.html";

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

    signupForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const nameInput = document.getElementById("signupName");
        const emailInput = document.getElementById("signupEmail");
        const passwordInput = document.getElementById("signupPassword");
        const confirmPasswordInput =
            document.getElementById("confirmPassword");

        const name = nameInput ? nameInput.value.trim() : "";
        const email = emailInput ? emailInput.value.trim() : "";
        const password =
            passwordInput ? passwordInput.value.trim() : "";
        const confirmPassword =
            confirmPasswordInput
                ? confirmPasswordInput.value.trim()
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


        alert("Account created successfully!");

        // Signup ke baad PROFILE page
        window.location.href = "profile.html";

    });

}


// ============================================================
// PROFILE FORM
// ============================================================

const profileForm = document.getElementById("profileForm");

if (profileForm) {

    profileForm.addEventListener("submit", function (event) {

        event.preventDefault();


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


        // Check basic information

        if (
            fullName === "" ||
            ageGroup === "" ||
            education === ""
        ) {

            alert("Please complete your basic profile information.");

            return;
        }


        // Check stream

        const selectedStream =
            document.querySelector(
                'input[name="stream"]:checked'
            );


        if (!selectedStream) {

            alert("Please select your education stream.");

            return;
        }


        // Check career goal

        const selectedGoal =
            document.querySelector(
                'input[name="goal"]:checked'
            );


        if (!selectedGoal) {

            alert("Please select your career goal.");

            return;
        }


        // Check interests

        const selectedInterests =
            document.querySelectorAll(
                'input[name="interest"]:checked'
            );


        if (selectedInterests.length === 0) {

            alert("Please select at least one interest.");

            return;
        }


        // Save profile information temporarily
        // Backend baad mein connect karenge.

        const profileData = {

            name: fullName,

            ageGroup: ageGroup,

            education: education,

            stream: selectedStream.value,

            goal: selectedGoal.value,

            interests: Array.from(selectedInterests)
                .map(function (item) {
                    return item.value;
                })

        };


        // Browser mein temporary save

        localStorage.setItem(
            "careerCompassProfile",
            JSON.stringify(profileData)
        );


        alert(
            "Profile saved! Let's discover your career."
        );


        // ====================================================
        // IMPORTANT:
        // Existing questionnaire page par jaana hai.
        // career-quiz.html NAHI.
        // ====================================================

        window.location.href = "questionnaire.html";

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