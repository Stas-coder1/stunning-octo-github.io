const gameContainer = document.getElementById('game-container');
const playArea = document.getElementById('play-area');
const scoreDisplay = document.getElementById('score');
const startButton = document.getElementById('start-button');
const timerDisplay = document.getElementById('time-left');
const messageOverlay = document.getElementById('message-overlay');
const messageText = document.getElementById('message-text');

let score = 0;
let gameInterval = null;
let spawnInterval = null;
let timerInterval = null;
let timeLeft = 0;

const GAME_DURATION = 30; // seconds
const SPAWN_RATE = 450; // milliseconds - faster spawn
const ITEM_FALL_SPEED = 3; // seconds - how long it takes to fall

function updateScore(newScore) {
    score = newScore;
    scoreDisplay.textContent = score;
}

function updateTimerDisplay() {
    timerDisplay.textContent = timeLeft;
}

function showMessage(text, duration = 1500) {
    messageText.textContent = text;
    messageOverlay.classList.add('visible');
    if (duration > 0) {
        setTimeout(() => {
            messageOverlay.classList.remove('visible');
        }, duration);
    }
}

function hideMessage() {
     messageOverlay.classList.remove('visible');
}

function createPointItem() {
    const item = document.createElement('div');
    item.classList.add('point-item');

    // Random horizontal position
    const maxX = playArea.clientWidth - 40; // item width
    item.style.left = `${Math.random() * maxX}px`;

    // Set fall duration via animation
    item.style.animationDuration = `${ITEM_FALL_SPEED}s`;

    // --- Click/Tap Handling ---
    const handleClick = (event) => {
        // Prevent event bubbling (optional but good practice)
        event.stopPropagation();

        // Check if already collected (robustness)
        if (item.classList.contains('collected')) return;

        updateScore(score + 1);
        item.classList.add('collected');

        // Clean up after animation
        item.addEventListener('animationend', () => {
            if (item.parentNode) {
                item.parentNode.removeChild(item);
            }
        }, { once: true }); // Ensure this runs only once

        // Remove the listener to prevent multiple clicks on the same item
        item.removeEventListener('click', handleClick);
        item.removeEventListener('touchstart', handleClick); // Also remove touch listener
    };

    item.addEventListener('click', handleClick);
    // Add touch event listener for mobile
    item.addEventListener('touchstart', (event) => {
        event.preventDefault(); // Prevent potential double event firing (click)
        handleClick(event);
    }, { passive: false });

    playArea.appendChild(item);

    // Remove item if it reaches the bottom without being clicked
    setTimeout(() => {
        // Only remove if it wasn't collected
        if (item.parentNode && !item.classList.contains('collected')) {
            item.parentNode.removeChild(item);
        }
    }, ITEM_FALL_SPEED * 1000); // Match fall duration
}

function startGame() {
    console.log("Starting game...");
    updateScore(0);
    timeLeft = GAME_DURATION;
    updateTimerDisplay();
    startButton.disabled = true;
    startButton.style.animation = 'none'; // Stop pulse animation
    hideMessage();
    playArea.innerHTML = ''; // Clear previous items

    // Clear any existing intervals
    if (spawnInterval) clearInterval(spawnInterval);
    if (timerInterval) clearInterval(timerInterval);

    // Start spawning items
    spawnInterval = setInterval(createPointItem, SPAWN_RATE);

    // Start game timer
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        if (timeLeft <= 0) {
            endGame();
        }
        // Flash timer when low
        if (timeLeft <= 5) {
             timerDisplay.parentElement.style.backgroundColor = timeLeft % 2 === 0 ? 'rgba(255, 100, 100, 0.8)' : 'rgba(255, 255, 255, 0.7)';
        } else {
             timerDisplay.parentElement.style.backgroundColor = 'rgba(255, 255, 255, 0.7)'; // Reset color
        }
    }, 1000);
}

function endGame() {
    console.log("Game over!");
    clearInterval(spawnInterval);
    clearInterval(timerInterval);
    spawnInterval = null;
    timerInterval = null;

    showMessage(`Конец игры!\nОчки: ${score}`, 0); // Show final score indefinitely until restart

    startButton.disabled = false;
    startButton.style.animation = ''; // Restore pulse animation
    timerDisplay.parentElement.style.backgroundColor = 'rgba(255, 255, 255, 0.7)'; // Reset timer bg

    // Optional: Add a delay before removing remaining items for visual effect
    setTimeout(() => {
        const remainingItems = playArea.querySelectorAll('.point-item:not(.collected)');
        remainingItems.forEach(item => {
             // Add a fade-out effect or just remove
             item.style.opacity = '0';
             item.style.transition = 'opacity 0.5s ease';
             setTimeout(() => {
                if(item.parentNode) item.parentNode.removeChild(item);
             }, 500);
        });
    }, 500); // Delay before clearing field
}

// --- Event Listeners ---
startButton.addEventListener('click', startGame);

// Prevent default drag behavior which can interfere with clicks/taps
gameContainer.addEventListener('dragstart', (e) => e.preventDefault());

// Initial setup
updateTimerDisplay(); // Show initial time
showMessage("Нажми Старт!", 0); // Show initial message