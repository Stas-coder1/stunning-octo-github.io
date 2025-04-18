<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Clicker Game</title>
    <link rel="stylesheet" href="style.css">
    <style>
        /* Prevent scrolling on the body itself */
        html, body {
            overflow: hidden;
            height: 100%;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="score-display">Очки: <span id="score">0</span></div>
        <div id="timer-display">Время: <span id="time-left">30</span></div>
        <div id="play-area">
            <!-- Falling items will be added here by JS -->
        </div>
        <div id="message-overlay">
            <span id="message-text"></span>
        </div>
    </div>
    <button id="start-button">Старт</button>

    <script src="https://stunning-octo-github.io"></script>
</body>
</html>
