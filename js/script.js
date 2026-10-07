document.addEventListener("DOMContentLoaded", function () {

    /* ================= GET ELEMENTS ================= */

    const profileForm = document.getElementById("profileForm");

    const fullName = document.getElementById("fullName");
    const email = document.getElementById("email");
    const location = document.getElementById("location");

    const education = document.getElementById("education");
    const fieldOfStudy = document.getElementById("fieldOfStudy");

    const careerGoal = document.getElementById("careerGoal");
    const careerDescription = document.getElementById("careerDescription");

    const avatarPreview = document.getElementById("avatarPreview");

    const previewName = document.getElementById("previewName");
    const previewEmail = document.getElementById("previewEmail");

    const previewEducation = document.getElementById("previewEducation");
    const previewField = document.getElementById("previewField");
    const previewGoal = document.getElementById("previewGoal");

    const completionPercent = document.getElementById("completionPercent");
    const progressFill = document.getElementById("progressFill");

    const clearBtn = document.getElementById("clearBtn");

    const interestCheckboxes =
        document.querySelectorAll(".interest-option input");


    /* ================= LOAD SAVED PROFILE ================= */

    function loadProfile() {

        const savedProfile =
            JSON.parse(localStorage.getItem("careerProfile"));

        if (!savedProfile) {

            const loggedInUser =
                JSON.parse(localStorage.getItem("careerCompassUser"));

            if (loggedInUser && loggedInUser.email) {
                email.value = loggedInUser.email;
            }

            updatePreview();
            return;
        }


        fullName.value = savedProfile.fullName || "";

        email.value = savedProfile.email || "";

        location.value = savedProfile.location || "";

        education.value = savedProfile.education || "";

        fieldOfStudy.value =
            savedProfile.fieldOfStudy || "";

        careerGoal.value =
            savedProfile.careerGoal || "";

        careerDescription.value =
            savedProfile.careerDescription || "";


        /* Restore interests */

        if (Array.isArray(savedProfile.interests)) {

            interestCheckboxes.forEach(function (checkbox) {

                checkbox.checked =
                    savedProfile.interests.includes(
                        checkbox.value
                    );

            });

        }


        updatePreview();

    }


    /* ================= UPDATE PREVIEW ================= */

    function updatePreview() {

        const name =
            fullName.value.trim();

        const userEmail =
            email.value.trim();

        const educationValue =
            education.value;

        const fieldValue =
            fieldOfStudy.value.trim();

        const goalValue =
            careerGoal.value.trim();


        /* Name */

        if (name) {

            previewName.textContent = name;

        } else {

            previewName.textContent = "Your Name";

        }


        /* Email */

        if (userEmail) {

            previewEmail.textContent = userEmail;

        } else {

            previewEmail.textContent = "your@email.com";

        }


        /* Education */

        if (educationValue) {

            const selectedOption =
                education.options[
                    education.selectedIndex
                ];

            previewEducation.textContent =
                selectedOption.textContent;

        } else {

            previewEducation.textContent =
                "Not added";

        }


        /* Field */

        if (fieldValue) {

            previewField.textContent =
                fieldValue;

        } else {

            previewField.textContent =
                "Not added";

        }


        /* Career Goal */

        if (goalValue) {

            previewGoal.textContent =
                goalValue;

        } else {

            previewGoal.textContent =
                "Not added";

        }


        /* Avatar */

        if (name) {

            avatarPreview.textContent =
                name.charAt(0).toUpperCase();

        } else {

            avatarPreview.textContent = "✨";

        }


        updateProgress();

    }


    /* ================= PROFILE PROGRESS ================= */

    function updateProgress() {

        const fields = [

            fullName.value.trim(),

            email.value.trim(),

            location.value.trim(),

            education.value,

            fieldOfStudy.value.trim(),

            careerGoal.value.trim(),

            careerDescription.value.trim()

        ];


        const completed =
            fields.filter(function (value) {

                return value !== "";

            }).length;


        const percentage =
            Math.round(
                (completed / fields.length) * 100
            );


        completionPercent.textContent =
            percentage + "%";

        progressFill.style.width =
            percentage + "%";

    }


    /* ================= LIVE UPDATE ================= */

    fullName.addEventListener(
        "input",
        updatePreview
    );

    email.addEventListener(
        "input",
        updatePreview
    );

    location.addEventListener(
        "input",
        updatePreview
    );

    education.addEventListener(
        "change",
        updatePreview
    );

    fieldOfStudy.addEventListener(
        "input",
        updatePreview
    );

    careerGoal.addEventListener(
        "input",
        updatePreview
    );

    careerDescription.addEventListener(
        "input",
        updatePreview
    );


    interestCheckboxes.forEach(
        function (checkbox) {

            checkbox.addEventListener(
                "change",
                updatePreview
            );

        }
    );


    /* ================= SAVE PROFILE ================= */

    profileForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            const name =
                fullName.value.trim();

            const userEmail =
                email.value.trim();

            const userLocation =
                location.value.trim();

            const selectedEducation =
                education.value;

            const studyField =
                fieldOfStudy.value.trim();

            const goal =
                careerGoal.value.trim();

            const description =
                careerDescription.value.trim();


            /* Basic validation */

            if (!name) {

                alert("Please enter your full name.");

                fullName.focus();

                return;

            }


            if (!userEmail) {

                alert("Please enter your email address.");

                email.focus();

                return;

            }


            if (!selectedEducation) {

                alert("Please select your current education.");

                education.focus();

                return;

            }


            /* Collect interests */

            const selectedInterests = [];

            interestCheckboxes.forEach(
                function (checkbox) {

                    if (checkbox.checked) {

                        selectedInterests.push(
                            checkbox.value
                        );

                    }

                }
            );


            /* Profile object */

            const profileData = {

                fullName: name,

                email: userEmail,

                location: userLocation,

                education: selectedEducation,

                fieldOfStudy: studyField,

                interests: selectedInterests,

                careerGoal: goal,

                careerDescription: description

            };


            /* Save profile */

            localStorage.setItem(
                "careerProfile",
                JSON.stringify(profileData)
            );


            /* Keep login information updated */

            const existingUser =
                JSON.parse(
                    localStorage.getItem(
                        "careerCompassUser"
                    )
                ) || {};


            existingUser.name = name;

            existingUser.email = userEmail;


            localStorage.setItem(
                "careerCompassUser",
                JSON.stringify(existingUser)
            );


            /* Success */

            alert(
                "Your profile has been saved successfully!"
            );


            /* Continue to assessment */

            window.location.href =
                "questionnaire.html";

        }
    );


    /* ================= CLEAR FORM ================= */

    clearBtn.addEventListener(
        "click",
        function () {

            const confirmClear =
                confirm(
                    "Are you sure you want to clear your profile?"
                );


            if (!confirmClear) {
                return;
            }


            profileForm.reset();


            localStorage.removeItem(
                "careerProfile"
            );


            /* Restore email from logged-in user */

            const loggedInUser =
                JSON.parse(
                    localStorage.getItem(
                        "careerCompassUser"
                    )
                );


            if (
                loggedInUser &&
                loggedInUser.email
            ) {

                email.value =
                    loggedInUser.email;

            }


            updatePreview();

        }
    );


    /* ================= INITIAL LOAD ================= */

    loadProfile();

});