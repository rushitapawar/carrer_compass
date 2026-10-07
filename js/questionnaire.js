<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Career Assessment | Career Compass AI</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap"
        rel="stylesheet"
    >

    <style>

        :root {
            --plum: #443846;
            --plum-dark: #322936;
            --pink: #e998b3;
            --pink-light: #f6c4d3;
            --pink-soft: #fff1f5;
            --cream: #f7f5f2;
            --white: #ffffff;
            --text: #342d3b;
            --muted: #756d76;
            --border: #e4dcda;
            --shadow: 0 20px 55px rgba(68, 56, 70, 0.09);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "DM Sans", sans-serif;
            background:
                radial-gradient(
                    circle at 10% 15%,
                    rgba(246, 196, 211, 0.30),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 90% 45%,
                    rgba(233, 152, 179, 0.14),
                    transparent 25%
                ),
                var(--cream);
            color: var(--text);
            min-height: 100vh;
        }

        a {
            text-decoration: none;
            color: inherit;
        }

        button {
            font-family: inherit;
        }

        /* ================= NAVBAR ================= */

        .navbar {
            height: 82px;
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #eee7e5;

            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 0 6%;

            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand img {
            width: 130px;
            height: auto;
            display: block;
        }

        .nav-right {
            display: flex;
            align-items: center;
            gap: 28px;
        }

        .nav-links {
            display: flex;
            gap: 25px;
            align-items: center;
        }

        .nav-links a {
            color: var(--muted);
            font-size: 14px;
            font-weight: 600;
            transition: 0.25s ease;
        }

        .nav-links a:hover,
        .nav-links a.active {
            color: var(--plum);
        }

        .profile-btn {
            width: 42px;
            height: 42px;
            border-radius: 50%;

            display: flex;
            align-items: center;
            justify-content: center;

            background: var(--plum);
            color: white;

            font-size: 15px;
            font-weight: 700;

            box-shadow: 0 8px 20px rgba(68, 56, 70, 0.18);
        }

        /* ================= PAGE ================= */

        .assessment-page {
            width: min(980px, 92%);
            margin: auto;
            padding: 48px 0 80px;
        }

        /* ================= TOP AREA ================= */

        .assessment-heading {
            text-align: center;
            margin-bottom: 30px;
        }

        .eyebrow {
            color: var(--pink);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2.5px;
            margin-bottom: 10px;
        }

        .assessment-heading h1 {
            font-family: "Playfair Display", serif;
            color: var(--plum-dark);
            font-size: clamp(38px, 5vw, 54px);
            line-height: 1.1;
            margin-bottom: 12px;
        }

        .assessment-heading h1 span {
            color: var(--pink);
        }

        .assessment-heading p {
            max-width: 650px;
            margin: auto;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.7;
        }

        /* ================= PROGRESS ================= */

        .progress-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px 22px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(68, 56, 70, 0.05);
        }

        .progress-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .progress-label {
            color: var(--plum);
            font-size: 13px;
            font-weight: 700;
        }

        .progress-value {
            color: var(--muted);
            font-size: 13px;
        }

        .progress-container {
            width: 100%;
            height: 8px;
            background: #eee7e8;
            border-radius: 20px;
            overflow: hidden;
        }

        .progress-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(
                90deg,
                var(--pink),
                #d97899
            );
            border-radius: 20px;
            transition: width 0.45s ease;
        }

        /* ================= GUIDE CARD ================= */

        .guide-selection,
        .question-card {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid var(--border);
            border-radius: 30px;
            box-shadow: var(--shadow);
        }

        .guide-selection {
            padding: 48px;
            text-align: center;
        }

        .guide-selection h2 {
            font-family: "Playfair Display", serif;
            color: var(--plum-dark);
            font-size: 34px;
            margin-bottom: 10px;
        }

        .guide-selection h2 span {
            color: var(--pink);
        }

        .guide-selection > p {
            max-width: 620px;
            margin: 0 auto 30px;
            color: var(--muted);
            line-height: 1.7;
            font-size: 14px;
        }

        .guide-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }

        .guide-card {
            background: #fcfaf9;
            border: 1.5px solid transparent;
            border-radius: 22px;
            padding: 23px 12px;

            cursor: pointer;
            transition: 0.25s ease;
        }

        .guide-card:hover {
            transform: translateY(-5px);
            border-color: var(--pink-light);
            box-shadow: 0 12px 28px rgba(233, 152, 179, 0.13);
        }

        .guide-card.selected {
            border-color: var(--pink);
            background: var(--pink-soft);
            box-shadow:
                0 0 0 3px rgba(233, 152, 179, 0.10),
                0 12px 30px rgba(233, 152, 179, 0.12);
        }

        .guide-avatar {
            width: 78px;
            height: 78px;
            margin: 0 auto 13px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: #f8e8ee;

            font-size: 37px;

            transition: 0.25s ease;
        }

        .guide-card.selected .guide-avatar {
            transform: scale(1.06);
            background: #f5dce5;
        }

        .guide-card h3 {
            color: var(--plum);
            font-size: 16px;
            margin-bottom: 5px;
        }

        .guide-card small {
            color: var(--muted);
            font-size: 11px;
        }

        .start-btn {
            margin-top: 30px;

            border: none;
            border-radius: 30px;

            background: var(--plum);
            color: white;

            padding: 15px 32px;

            font-size: 14px;
            font-weight: 700;

            cursor: pointer;

            box-shadow: 0 10px 25px rgba(68, 56, 70, 0.16);

            transition: 0.25s ease;
        }

        .start-btn:hover {
            background: var(--plum-dark);
            transform: translateY(-2px);
        }

        /* ================= QUESTION CARD ================= */

        .question-card {
            display: none;
            padding: 43px;
            animation: questionAppear 0.35s ease;
        }

        @keyframes questionAppear {

            from {
                opacity: 0;
                transform: translateY(10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }

        }

        .question-number {
            display: inline-flex;
            align-items: center;

            background: var(--pink-soft);
            color: #805269;

            padding: 8px 14px;

            border-radius: 30px;

            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.6px;

            margin-bottom: 20px;
        }

        .guide-message {
            display: flex;
            align-items: center;
            gap: 12px;

            background: #fcf6f8;
            border: 1px solid #f1e2e7;

            border-radius: 17px;

            padding: 13px 16px;

            color: var(--muted);
            font-size: 13px;

            margin-bottom: 25px;
        }

        .mini-avatar {
            width: 42px;
            height: 42px;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: #f7e5eb;

            font-size: 22px;
        }

        .question-card h2 {
            font-family: "Playfair Display", serif;
            color: var(--plum-dark);

            font-size: clamp(25px, 4vw, 32px);
            line-height: 1.4;

            margin-bottom: 28px;
        }

        /* ================= OPTIONS ================= */

        .options {
            display: grid;
            gap: 13px;
        }

        .option {
            width: 100%;

            display: flex;
            align-items: center;
            gap: 14px;

            text-align: left;

            background: #fcfaf9;
            border: 1.5px solid var(--border);

            border-radius: 17px;

            padding: 17px 18px;

            color: var(--plum);

            font-size: 14px;
            line-height: 1.5;

            cursor: pointer;

            transition: 0.22s ease;
        }

        .option:hover {
            background: var(--pink-soft);
            border-color: var(--pink-light);
            transform: translateX(3px);
        }

        .option.selected {
            background: var(--pink-soft);
            border-color: var(--pink);

            box-shadow:
                0 0 0 3px rgba(233, 152, 179, 0.09);
        }

        .option-letter {
            width: 35px;
            height: 35px;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 50%;

            background: #eee8e9;
            color: var(--plum);

            font-size: 12px;
            font-weight: 700;
        }

        .option.selected .option-letter {
            background: var(--pink);
            color: white;
        }

        /* ================= ACTIONS ================= */

        .question-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;

            margin-top: 32px;
            padding-top: 25px;

            border-top: 1px solid #eee7e5;
        }

        .back-btn,
        .next-btn {
            border-radius: 25px;

            padding: 13px 25px;

            font-size: 13px;
            font-weight: 700;

            cursor: pointer;

            transition: 0.25s ease;
        }

        .back-btn {
            background: white;
            color: var(--plum);
            border: 1px solid #d8d0d2;
        }

        .back-btn:hover {
            background: #f5f1f0;
        }

        .next-btn {
            background: var(--plum);
            color: white;
            border: none;

            min-width: 125px;
        }

        .next-btn:hover:not(:disabled) {
            background: var(--plum-dark);
            transform: translateY(-1px);
        }

        .next-btn:disabled {
            opacity: 0.45;
            cursor: not-allowed;
        }

        /* ================= FOOTER ================= */

        footer {
            background: var(--plum-dark);
            color: white;
            padding: 42px 6%;
        }

        .footer-inner {
            max-width: 980px;
            margin: auto;

            display: flex;
            justify-content: space-between;
            align-items: center;

            gap: 30px;
        }

        .footer-logo img {
            width: 105px;
            filter: brightness(0) invert(1);
            margin-bottom: 8px;
        }

        .footer-text {
            color: #d9d0d8;
            font-size: 12px;
        }

        .footer-links {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }

        .footer-links a {
            color: #eee6ec;
            font-size: 13px;
        }

        .footer-links a:hover {
            color: var(--pink-light);
        }

        /* ================= RESPONSIVE ================= */

        @media (max-width: 850px) {

            .nav-links {
                display: none;
            }

            .guide-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .guide-selection,
            .question-card {
                padding: 30px 22px;
            }

        }

        @media (max-width: 550px) {

            .navbar {
                padding: 0 20px;
            }

            .brand img {
                width: 110px;
            }

            .assessment-page {
                width: 94%;
                padding-top: 30px;
            }

            .guide-grid {
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }

            .guide-avatar {
                width: 65px;
                height: 65px;
                font-size: 30px;
            }

            .question-actions {
                gap: 10px;
            }

            .back-btn,
            .next-btn {
                padding: 12px 18px;
            }

            .footer-inner {
                flex-direction: column;
                align-items: flex-start;
            }

        }

    </style>
</head>

<body>

    <!-- ================= NAVBAR ================= -->

    <nav class="navbar">

        <a href="index.html" class="brand">
            <img
                src="../images/logo.png"
                alt="Career Compass AI"
            >
        </a>

        <div class="nav-right">

            <div class="nav-links">

                <a href="index.html">
                    Home
                </a>

                <a href="about.html">
                    About
                </a>

                <a href="how-it-works.html">
                    How It Works
                </a>

                <a
                    href="questionnaire.html"
                    class="active"
                >
                    Assessment
                </a>

                <a href="contact.html">
                    Contact
                </a>

            </div>

            <a
                href="profile.html"
                class="profile-btn"
            >
                A
            </a>

        </div>

    </nav>


    <!-- ================= MAIN ================= -->

    <main class="assessment-page">

        <section class="assessment-heading">

            <div class="eyebrow">
                CAREER DISCOVERY ASSESSMENT
            </div>

            <h1>
                Discover your
                <span>career direction.</span>
            </h1>

            <p>
                Answer honestly and choose what feels most like you.
                Your responses will help Career Compass AI understand
                your interests and create your personalized career profile.
            </p>

        </section>


        <!-- ================= PROGRESS ================= -->

        <div class="progress-card">

            <div class="progress-top">

                <span
                    class="progress-label"
                    id="progressText"
                >
                    Choose your career guide
                </span>

                <span
                    class="progress-value"
                    id="questionCount"
                >
                    Step 1
                </span>

            </div>

            <div class="progress-container">

                <div
                    class="progress-bar"
                    id="progressBar"
                ></div>

            </div>

        </div>


        <!-- ================= GUIDE SELECTION ================= -->

        <section
            class="guide-selection"
            id="guideSelection"
        >

            <h2>
                Choose your
                <span>career guide</span>
            </h2>

            <p>
                Pick a guide who will accompany you through
                your career discovery journey.
            </p>


            <div class="guide-grid">

                <div
                    class="guide-card"
                    data-name="Ava"
                    data-icon="👩‍💼"
                >

                    <div class="guide-avatar">
                        👩‍💼
                    </div>

                    <h3>Ava</h3>

                    <small>
                        Friendly & Creative
                    </small>

                </div>


                <div
                    class="guide-card"
                    data-name="Leo"
                    data-icon="👨‍💻"
                >

                    <div class="guide-avatar">
                        👨‍💻
                    </div>

                    <h3>Leo</h3>

                    <small>
                        Analytical & Smart
                    </small>

                </div>


                <div
                    class="guide-card"
                    data-name="Maya"
                    data-icon="👩‍🎨"
                >

                    <div class="guide-avatar">
                        👩‍🎨
                    </div>

                    <h3>Maya</h3>

                    <small>
                        Curious & Supportive
                    </small>

                </div>


                <div
                    class="guide-card"
                    data-name="Noah"
                    data-icon="🧑‍🚀"
                >

                    <div class="guide-avatar">
                        🧑‍🚀
                    </div>

                    <h3>Noah</h3>

                    <small>
                        Ambitious & Bold
                    </small>

                </div>

            </div>


            <button
                class="start-btn"
                id="startBtn"
            >
                Start Assessment →
            </button>

        </section>


        <!-- ================= QUESTION ================= -->

        <section
            class="question-card"
            id="questionCard"
        >

            <div
                class="question-number"
                id="questionNumber"
            >
                QUESTION 1 OF 25
            </div>


            <div class="guide-message">

                <div
                    class="mini-avatar"
                    id="miniAvatar"
                >
                    ✨
                </div>

                <span id="guideMessage">
                    Choose the answer that feels most like you.
                </span>

            </div>


            <h2 id="questionText">
                Question goes here
            </h2>


            <div
                class="options"
                id="optionsContainer"
            ></div>


            <div class="question-actions">

                <button
                    type="button"
                    class="back-btn"
                    id="backBtn"
                >
                    ← Back
                </button>

                <button
                    type="button"
                    class="next-btn"
                    id="nextBtn"
                    disabled
                >
                    Next →
                </button>

            </div>

        </section>

    </main>


    <!-- ================= FOOTER ================= -->

    <footer>

        <div class="footer-inner">

            <div>

                <div class="footer-logo">

                    <img
                        src="../images/logo.png"
                        alt="Career Compass AI"
                    >

                </div>

                <div class="footer-text">
                    Helping you discover a career that fits you.
                </div>

            </div>


            <div class="footer-links">

                <a href="about.html">
                    About
                </a>

                <a href="how-it-works.html">
                    How It Works
                </a>

                <a href="privacy.html">
                    Privacy
                </a>

                <a href="contact.html">
                    Contact
                </a>

            </div>

        </div>

    </footer>


    <script src="../js/questionnaire.js"></script>

</body>
</html>