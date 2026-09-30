import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌깨기 게임",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌깨기")
st.write("게임 화면을 클릭한 뒤 ← → 또는 A / D 키를 사용하세요.")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    background: #111827;
    color: white;
    font-family: Arial, sans-serif;
}

body {
    text-align: center;
    user-select: none;
}

#gameContainer {
    width: 100%;
    max-width: 520px;
    margin: auto;
}

#info {
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin-bottom: 10px;
    font-size: 17px;
    font-weight: bold;
}

#gameCanvas {
    display: block;
    width: 500px;
    max-width: 100%;
    height: auto;

    background: #020617;
    border: 3px solid #38bdf8;
    border-radius: 10px;

    outline: none;
    cursor: pointer;
}

#gameCanvas:focus {
    border-color: #22c55e;
}

#message {
    height: 35px;
    margin-top: 10px;

    font-size: 23px;
    font-weight: bold;
    color: #facc15;
}

button {
    border: none;
    border-radius: 8px;

    padding: 11px 24px;

    background: #38bdf8;
    color: #082f49;

    font-size: 16px;
    font-weight: bold;

    cursor: pointer;
}

button:hover {
    background: #7dd3fc;
}

#help {
    margin-top: 10px;
    color: #94a3b8;
    font-size: 14px;
}
</style>
</head>

<body>

<div id="gameContainer">

    <div id="info">
        <div>점수: <span id="score">0</span></div>
        <div>목숨: <span id="lives">3</span></div>
        <div>레벨: <span id="level">1</span></div>
    </div>

    <canvas
        id="gameCanvas"
        width="500"
        height="500"
        tabindex="0">
    </canvas>

    <div id="message"></div>

    <button id="restartButton">
        🔄 다시 시작
    </button>

    <div id="help">
        ← → / A D : 이동 &nbsp; | &nbsp; 마우스/터치 : 패들 이동
    </div>

</div>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreText = document.getElementById("score");
const livesText = document.getElementById("lives");
const levelText = document.getElementById("level");
const messageText = document.getElementById("message");
const restartButton = document.getElementById("restartButton");


// ===============================
// 게임 변수
// ===============================

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = false;
let animationId = null;

let leftPressed = false;
let rightPressed = false;


// ===============================
// 공
// ===============================

const ball = {
    x: 250,
    y: 430,

    radius: 8,

    dx: 3,
    dy: -3
};


// ===============================
// 패들
// ===============================

const paddle = {
    width: 90,
    height: 12,

    x: 205,

    y: 465,

    speed: 7
};


// ===============================
// 벽돌
// ===============================

const brick = {
    rows: 5,
    columns: 8,

    width: 52,
    height: 20,

    padding: 8,

    offsetTop: 50,
    offsetLeft: 18
};

let bricks = [];


// ===============================
// 벽돌 생성
// ===============================

function createBricks() {

    bricks = [];

    for (let row = 0; row < brick.rows; row++) {

        bricks[row] = [];

        for (let col = 0; col < brick.columns; col++) {

            bricks[row][col] = {
                alive: true,
                x: 0,
                y: 0
            };
        }
    }
}


// ===============================
// 벽돌 색상
// ===============================

function getBrickColor(row) {

    const colors = [
        "#ef4444",
        "#f97316",
        "#eab308",
        "#22c55e",
        "#3b82f6"
    ];

    return colors[row % colors.length];
}


// ===============================
// 공 그리기
// ===============================

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#ffffff";

    ctx.fill();

    ctx.closePath();
}


// ===============================
// 패들 그리기
// ===============================

function drawPaddle() {

    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height,
        6
    );

    ctx.fillStyle = "#38bdf8";

    ctx.fill();

    ctx.closePath();
}


// ===============================
// 벽돌 그리기
// ===============================

function drawBricks() {

    for (let row = 0; row < brick.rows; row++) {

        for (let col = 0; col < brick.columns; col++) {

            const b = bricks[row][col];

            if (!b.alive) {
                continue;
            }

            b.x =
                brick.offsetLeft +
                col * (brick.width + brick.padding);

            b.y =
                brick.offsetTop +
                row * (brick.height + brick.padding);

            ctx.beginPath();

            ctx.roundRect(
                b.x,
                b.y,
                brick.width,
                brick.height,
                4
            );

            ctx.fillStyle =
                getBrickColor(row);

            ctx.fill();

            ctx.closePath();
        }
    }
}


// ===============================
// 게임 화면
// ===============================

function drawBackground() {

    ctx.fillStyle = "#020617";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );
}


// ===============================
// 벽돌 충돌 검사
// ===============================

function checkBrickCollision() {

    for (let row = 0; row < brick.rows; row++) {

        for (let col = 0; col < brick.columns; col++) {

            const b = bricks[row][col];

            if (!b.alive) {
                continue;
            }

            if (
                ball.x + ball.radius > b.x &&
                ball.x - ball.radius < b.x + brick.width &&
                ball.y + ball.radius > b.y &&
                ball.y - ball.radius < b.y + brick.height
            ) {

                b.alive = false;

                ball.dy = -ball.dy;

                score += 10;

                scoreText.textContent = score;

                return;
            }
        }
    }
}


// ===============================
// 패들 충돌
// ===============================

function checkPaddleCollision() {

    if (ball.dy <= 0) {
        return;
    }

    if (
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width
    ) {

        // 공이 패들의 어느 부분을 맞았는지 계산
        const hitPosition =
            (ball.x - paddle.x) /
            paddle.width;

        // -1 ~ +1
        const relative =
            hitPosition * 2 - 1;

        const speed =
            Math.sqrt(
                ball.dx * ball.dx +
                ball.dy * ball.dy
            );

        ball.dx =
            relative * speed * 0.8;

        ball.dy =
            -Math.abs(speed * 0.6);

        // 패들 내부에 공이 들어가는 현상 방지
        ball.y =
            paddle.y - ball.radius - 1;
    }
}


// ===============================
// 모든 벽돌 제거 확인
// ===============================

function allBricksDestroyed() {

    for (let row = 0; row < brick.rows; row++) {

        for (let col = 0; col < brick.columns; col++) {

            if (bricks[row][col].alive) {
                return false;
            }
        }
    }

    return true;
}


// ===============================
// 공 초기화
// ===============================

function resetBall() {

    ball.x = canvas.width / 2;
    ball.y = 430;

    const direction =
        Math.random() < 0.5 ? -1 : 1;

    ball.dx = 3 * direction;
    ball.dy = -3;

    paddle.x =
        canvas.width / 2 -
        paddle.width / 2;
}


// ===============================
// 목숨 잃음
// ===============================

function loseLife() {

    lives--;

    livesText.textContent = lives;

    if (lives <= 0) {

        gameOver();

        return;
    }

    resetBall();
}


// ===============================
// 게임 오버
// ===============================

function gameOver() {

    gameRunning = false;

    messageText.textContent =
        "💥 GAME OVER";

    cancelAnimationFrame(animationId);
}


// ===============================
// 게임 클리어
// ===============================

function gameClear() {

    gameRunning = false;

    messageText.textContent =
        "🎉 게임 클리어!";

    cancelAnimationFrame(animationId);
}


// ===============================
// 다음 레벨
// ===============================

function nextLevel() {

    level++;

    levelText.textContent = level;

    createBricks();

    resetBall();

    // 레벨이 올라갈수록 빨라짐
    const speedBonus =
        3 + (level - 1) * 0.7;

    ball.dx =
        ball.dx >= 0
            ? speedBonus
            : -speedBonus;

    ball.dy = -speedBonus;
}


// ===============================
// 패들 이동
// ===============================

function movePaddle() {

    if (leftPressed) {

        paddle.x -= paddle.speed;
    }

    if (rightPressed) {

        paddle.x += paddle.speed;
    }

    // 화면 밖으로 못 나가게
    if (paddle.x < 0) {

        paddle.x = 0;
    }

    if (
        paddle.x + paddle.width >
        canvas.width
    ) {

        paddle.x =
            canvas.width -
            paddle.width;
    }
}


// ===============================
// 공 이동
// ===============================

function moveBall() {

    ball.x += ball.dx;
    ball.y += ball.dy;


    // 왼쪽 벽
    if (
        ball.x - ball.radius <= 0
    ) {

        ball.x = ball.radius;

        ball.dx =
            Math.abs(ball.dx);
    }


    // 오른쪽 벽
    if (
        ball.x + ball.radius >=
        canvas.width
    ) {

        ball.x =
            canvas.width -
            ball.radius;

        ball.dx =
            -Math.abs(ball.dx);
    }


    // 위쪽 벽
    if (
        ball.y - ball.radius <= 0
    ) {

        ball.y = ball.radius;

        ball.dy =
            Math.abs(ball.dy);
    }


    // 아래쪽
    if (
        ball.y - ball.radius >
        canvas.height
    ) {

        loseLife();

        return;
    }
}


// ===============================
// 게임 루프
// ===============================

function gameLoop() {

    if (!gameRunning) {
        return;
    }

    drawBackground();

    movePaddle();

    moveBall();

    checkPaddleCollision();

    checkBrickCollision();

    drawBricks();

    drawPaddle();

    drawBall();


    // 벽돌을 전부 깨면
    if (allBricksDestroyed()) {

        if (level >= 3) {

            gameClear();

            return;
        }

        nextLevel();
    }


    animationId =
        requestAnimationFrame(gameLoop);
}


// ===============================
// 게임 시작
// ===============================

function startGame() {

    if (animationId !== null) {

        cancelAnimationFrame(
            animationId
        );
    }

    score = 0;
    lives = 3;
    level = 1;

    scoreText.textContent = "0";
    livesText.textContent = "3";
    levelText.textContent = "1";

    messageText.textContent = "";

    leftPressed = false;
    rightPressed = false;

    createBricks();

    resetBall();

    gameRunning = true;

    canvas.focus();

    gameLoop();
}


// ===============================
// 키보드 입력
// ===============================

window.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "ArrowLeft" ||
            event.key.toLowerCase() === "a"
        ) {

            event.preventDefault();

            leftPressed = true;
        }

        if (
            event.key === "ArrowRight" ||
            event.key.toLowerCase() === "d"
        ) {

            event.preventDefault();

            rightPressed = true;
        }
    }
);


window.addEventListener(
    "keyup",
    function(event) {

        if (
            event.key === "ArrowLeft" ||
            event.key.toLowerCase() === "a"
        ) {

            event.preventDefault();

            leftPressed = false;
        }

        if (
            event.key === "ArrowRight" ||
            event.key.toLowerCase() === "d"
        ) {

            event.preventDefault();

            rightPressed = false;
        }
    }
);


// ===============================
// 마우스 이동
// ===============================

canvas.addEventListener(
    "mousemove",
    function(event) {

        const rect =
            canvas.getBoundingClientRect();

        const scaleX =
            canvas.width / rect.width;

        const mouseX =
            (event.clientX - rect.left)
            * scaleX;

        paddle.x =
            mouseX -
            paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;
        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width -
                paddle.width;
        }
    }
);


// ===============================
// 터치 이동
// ===============================

canvas.addEventListener(
    "touchmove",
    function(event) {

        event.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const scaleX =
            canvas.width / rect.width;

        const touch =
            event.touches[0];

        const touchX =
            (touch.clientX - rect.left)
            * scaleX;

        paddle.x =
            touchX -
            paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;
        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width -
                paddle.width;
        }
    },
    {
        passive: false
    }
);


// ===============================
// 게임 화면 클릭
// ===============================

canvas.addEventListener(
    "click",
    function() {

        canvas.focus();
    }
);


// ===============================
// 재시작 버튼
// ===============================

restartButton.addEventListener(
    "click",
    function() {

        startGame();

        canvas.focus();
    }
);


// ===============================
// 최초 시작
// ===============================

startGame();

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=650,
    scrolling=False
)
