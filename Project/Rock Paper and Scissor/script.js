let playerScore = 0;
let computerScore = 0;
const playerScoreDisplay = document.getElementById('player-score');
const computerScoreDisplay = document.getElementById('computer-score');
const resultDisplay = document.getElementById('result');
const playerHand = document.querySelector('.player-hand');
const computerHand = document.querySelector('.computer-hand');
const choices = document.querySelectorAll('.choice');
const resetBtn = document.getElementById('reset');

// Game options
const options = ['rock', 'paper', 'scissors'];
const emojis = {
    'rock': '✊',
    'paper': '✋',
    'scissors': '✌️'
};

// Add event listeners to buttons
choices.forEach(choice => {
    choice.addEventListener('click', function () {
        const playerChoice = this.id;
        playRound(playerChoice);
    });
});

// Reset button
resetBtn.addEventListener('click', resetGame);

// Main game function
function playRound(playerChoice) {
    // Disable buttons during animation
    choices.forEach(button => button.disabled = true);

    // Reset hands to rock (starting position)
    playerHand.textContent = '✊';
    computerHand.textContent = '✊';
    resultDisplay.textContent = "";

    // Add shake animation
    playerHand.classList.add('shake');
    computerHand.classList.add('shake-computer');

    // Wait for animation to finish
    setTimeout(() => {
        // Remove shake animation
        playerHand.classList.remove('shake');
        computerHand.classList.remove('shake-computer');

        // Get computer choice
        const computerChoice = getComputerChoice();

        // Update hand displays
        playerHand.textContent = emojis[playerChoice];
        computerHand.textContent = emojis[computerChoice];

        // Determine winner
        const result = getWinner(playerChoice, computerChoice);
        updateScore(result);
        displayResult(result, playerChoice, computerChoice);

        // Re-enable buttons
        choices.forEach(button => button.disabled = false);
    }, 2000);
}

// Get computer's random choice
function getComputerChoice() {
    const randomIndex = Math.floor(Math.random() * 3);
    return options[randomIndex];
}

// Determine winner
function getWinner(player, computer) {
    if (player === computer) {
        return 'draw';
    }

    if (
        (player === 'rock' && computer === 'scissors') ||
        (player === 'paper' && computer === 'rock') ||
        (player === 'scissors' && computer === 'paper')
    ) {
        return 'player';
    } else {
        return 'computer';
    }
}

// Update score
function updateScore(result) {
    if (result === 'player') {
        playerScore++;
        playerScoreDisplay.textContent = playerScore;
    } else if (result === 'computer') {
        computerScore++;
        computerScoreDisplay.textContent = computerScore;
    }
}

// Display result message
function displayResult(result, playerChoice, computerChoice) {
    if (result === 'player') {
        resultDisplay.textContent = `You win! ${playerChoice} beats ${computerChoice}`;
        resultDisplay.style.color = 'green';
    } else if (result === 'computer') {
        resultDisplay.textContent = `You lose! ${computerChoice} beats ${playerChoice}`;
        resultDisplay.style.color = 'red';
    } else {
        resultDisplay.textContent = `It's a draw! Both chose ${playerChoice}`;
        resultDisplay.style.color = 'yellow';
    }
}

// Reset game
function resetGame() {
    playerScore = 0;
    computerScore = 0;
    playerScoreDisplay.textContent = '0';
    computerScoreDisplay.textContent = '0';
    resultDisplay.textContent = 'Choose an option!';
    resultDisplay.style.color = '#333';
    playerHand.textContent = '✊';
    computerHand.textContent = '✊';
}