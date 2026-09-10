const N = 30;
const DECAY = 0.08;
const LR = 0.4;
const TRACE_DECAY = 0.5;
const SPARSITY = 3;

const VOCAB = {
    cat: 1,
    meow: 2,
    dog: 3,
    bark: 4,
    car: 10,
    tree: 11,
    cloud: 12,
    phone: 13,
    shoe: 14,
    lamp: 15,
    rain: 16,
    book: 17
};

let sequence = [
    "cat", "meow", "cat", "meow",
    "cat", "meow", "cat", "meow",
    "car", "tree", "cloud", "phone"
];

let history = [];
let associations = [];
let currentStep = 0;
let playing = false;
let timer = null;
let pairA="cat";
let pairB="meow";

const heatmap = document.getElementById("heatmap");
const chart = document.getElementById("chart");

const heatCtx = heatmap.getContext("2d");
const chartCtx = chart.getContext("2d");

const sequenceEl = document.getElementById("sequence");
const stepNumber = document.getElementById("stepNumber");
const currentWord = document.getElementById("currentWord");
const associationValue = document.getElementById("associationValue");
const memoryState = document.getElementById("memoryState");
const playButton = document.getElementById("playButton");
const resetButton = document.getElementById("resetButton");
const experimentTitle = document.getElementById("experimentTitle");
const associationTitle = document.getElementById("associationTitle");


// ---------------------------------------------------------
// Deterministic 3-neuron representation for each word
// ---------------------------------------------------------

function activeNeurons(symbolId) {

    let x = symbolId * 99991;
    let chosen = [];

    while (chosen.length < SPARSITY) {

        x = (x * 16807) % 2147483647;

        let index = Math.abs(x) % N;

        if (!chosen.includes(index)) {
            chosen.push(index);
        }
    }

    return chosen;
}


// ---------------------------------------------------------
// Hebbian memory model
// ---------------------------------------------------------

function createMatrix() {

    return Array.from(
        { length: N },
        () => Array(N).fill(0)
    );
}


function outerProduct(a, b) {

    const result = createMatrix();

    for (const i of a) {
        for (const j of b) {
            result[i][j] += LR;
            result[j][i] += LR;
        }
    }

    for (let i = 0; i < N; i++) {
        result[i][i] = 0;
    }

    return result;
}


function runSimulation(words) {

    let W = createMatrix();

    let trace = Array(N).fill(0);

    let matrices = [];
    let curve = [];

    for (const word of words) {

        const neurons = activeNeurons(VOCAB[word]);

        // Hebbian update:
        // previous activity trace strengthens
        // connections to the current active neurons.

        const update = createMatrix();

        for (let i = 0; i < N; i++) {

            for (const j of neurons) {

                update[i][j] +=
                    trace[i] * LR;

                update[j][i] +=
                    trace[i] * LR;
            }
        }

        for (let i = 0; i < N; i++) {

            update[i][i] = 0;

            for (let j = 0; j < N; j++) {

                W[i][j] =
                    W[i][j] * (1 - DECAY)
                    + update[i][j];
            }
        }

        // Current activity becomes recent trace.
        for (let i = 0; i < N; i++) {
            trace[i] *= TRACE_DECAY;
        }

        for (const neuron of neurons) {
            trace[neuron] += 1;
        }

        matrices.push(
            W.map(row => [...row])
        );

        curve.push(
            associationStrength(
                W,
                pairA,
                pairB
            )
        );
    }

    return {
        matrices,
        curve
    };
}


function associationStrength(W, wordA, wordB) {

    const a = activeNeurons(VOCAB[wordA]);
    const b = activeNeurons(VOCAB[wordB]);

    let value = 0;

    for (const i of a) {
        for (const j of b) {
            value += W[i][j];
        }
    }

    return value;
}


// ---------------------------------------------------------
// Rendering
// ---------------------------------------------------------

function renderSequence() {

    sequenceEl.innerHTML = "";

    sequence.forEach((word, index) => {

        const token = document.createElement("div");

        token.className = "token";

        if (index === currentStep) {
            token.classList.add("active");
        }

        token.textContent = word;

        sequenceEl.appendChild(token);
    });
}


function renderHeatmap() {

    const matrix = history[currentStep];

    if (!matrix) return;

    const size = 420;

    heatmap.width = size;
    heatmap.height = size;

    heatCtx.clearRect(0, 0, size, size);

    let max = 0;

    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            max = Math.max(max, matrix[i][j]);
        }
    }

    max = Math.max(max, 1);

    const cell = size / N;

    for (let i = 0; i < N; i++) {

        for (let j = 0; j < N; j++) {

            const value = matrix[i][j];

            const intensity =
                Math.min(1, value / max);

            const brightness =
                Math.round(15 + intensity * 240);

            heatCtx.fillStyle =
                `rgb(${brightness},${brightness},${brightness})`;

            heatCtx.fillRect(
                j * cell,
                i * cell,
                cell + 1,
                cell + 1
            );
        }
    }

    // Highlight currently active neurons

    const word = sequence[currentStep];

    if (VOCAB[word]) {

        const neurons =
            activeNeurons(VOCAB[word]);

        heatCtx.strokeStyle = "#ffffff";
        heatCtx.lineWidth = 2;

        for (const neuron of neurons) {

            const y = neuron * cell;

            heatCtx.strokeRect(
                0,
                y,
                size,
                cell
            );

            const x = neuron * cell;

            heatCtx.strokeRect(
                x,
                0,
                cell,
                size
            );
        }
    }
}


function renderChart() {

    const values = associations;

    const width = chart.clientWidth;
    const height = chart.clientHeight;

    chart.width = width;
    chart.height = height;

    chartCtx.clearRect(0, 0, width, height);

    if (values.length < 2) return;

    const left = 45;
    const right = 15;
    const top = 20;
    const bottom = 35;

    const graphWidth =
        width - left - right;

    const graphHeight =
        height - top - bottom;

    const max =
        Math.max(...values, 1) * 1.1;

    chartCtx.strokeStyle = "#252a34";
    chartCtx.lineWidth = 1;

    for (let i = 0; i <= 4; i++) {

        const y =
            top + graphHeight * i / 4;

        chartCtx.beginPath();
        chartCtx.moveTo(left, y);
        chartCtx.lineTo(width - right, y);
        chartCtx.stroke();
    }

    chartCtx.strokeStyle = "#ffffff";
    chartCtx.lineWidth = 3;

    chartCtx.beginPath();

    values.forEach((value, index) => {

        const x =
            left +
            graphWidth *
            index / (values.length - 1);

        const y =
            top +
            graphHeight *
            (1 - value / max);

        if (index === 0)
            chartCtx.moveTo(x, y);
        else
            chartCtx.lineTo(x, y);
    });

    chartCtx.stroke();

    const value = values[currentStep];

    const x =
        left +
        graphWidth *
        currentStep / (values.length - 1);

    const y =
        top +
        graphHeight *
        (1 - value / max);

    chartCtx.fillStyle = "#ffffff";

    chartCtx.beginPath();
    chartCtx.arc(x, y, 6, 0, Math.PI * 2);
    chartCtx.fill();
}


function updateText() {

    const value = associations[currentStep] || 0;

    stepNumber.textContent = currentStep;
    currentWord.textContent =
        sequence[currentStep] || "—";

        associationValue.textContent =
        `${pairA} ↔ ${pairB} Association`;

    if (value < 1) {
        memoryState.textContent = "Not learned";
    }
    else if (value < 15) {
        memoryState.textContent = "Weak";
    }
    else if (value < 30) {
        memoryState.textContent = "Established";
    }
    else {
        memoryState.textContent = "Strong";
    }
}


function render() {

    renderSequence();
    renderHeatmap();
    renderChart();
    updateText();
}


// ---------------------------------------------------------
// Controls
// ---------------------------------------------------------

function reset() {

    stop();

    currentStep = 0;

    const result =
        runSimulation(sequence);

    history = result.matrices;
    associations = result.curve;

    render();
}


function play() {

    if (playing) {
        stop();
        return;
    }

    playing = true;

    playButton.textContent = "Ⅱ Pause";

    timer = setInterval(() => {

        if (currentStep >= sequence.length - 1) {
            stop();
            return;
        }

        currentStep++;

        render();

    }, 650);
}


function stop() {

    playing = false;

    clearInterval(timer);

    playButton.textContent = "▶ Play";
}


playButton.addEventListener(
    "click",
    play
);


resetButton.addEventListener(
    "click",
    reset
);


// ---------------------------------------------------------
// Add word buttons
// ---------------------------------------------------------

function createSandboxControls() {

    const sandbox =
        document.querySelector(".sandbox");

    const box =
        document.createElement("div");

    box.style.marginTop = "25px";

    box.innerHTML = `
        <div class="label">BUILD YOUR OWN SEQUENCE</div>

        <div id="wordButtons"
             style="
                display:flex;
                flex-wrap:wrap;
                gap:8px;
                margin:12px 0;
             ">
        </div>

        <div id="customSequence"
             style="
                min-height:45px;
                padding:12px;
                border:1px solid #303641;
                border-radius:8px;
                color:#aeb6c4;
                margin-bottom:12px;
             ">
        </div>

        <button id="runCustom">
            Run My Sequence
        </button>

        <button id="clearCustom">
            Clear
        </button>
    `;

    sandbox.appendChild(box);

    const buttons =
        document.getElementById("wordButtons");

    const custom =
        document.getElementById("customSequence");

    Object.keys(VOCAB).forEach(word => {

        const button =
            document.createElement("button");

        button.textContent = word;

        button.addEventListener(
            "click",
            () => {

                sequence.push(word);

                renderCustomSequence();
            }
        );

        buttons.appendChild(button);
    });


    function renderCustomSequence() {

        custom.innerHTML =
            sequence
                .map(word => `<span class="token">${word}</span>`)
                .join(" → ");
    }


    document
        .getElementById("clearCustom")
        .addEventListener(
            "click",
            () => {

                sequence = [];

                stop();

                history = [];
                associations = [];
                currentStep = 0;

                custom.textContent =
                    "Add words above...";

                render();
            }
        );


    document
        .getElementById("runCustom")
        .addEventListener(
            "click",
            () => {

                if (sequence.length < 2) {
                    alert("Add at least two words.");
                    return;
                }

                stop();

                currentStep = 0;

                const result =
                    runSimulation(sequence);

                history = result.matrices;
                associations = result.curve;

                render();
            }
        );

    renderCustomSequence();
}


// ---------------------------------------------------------
// Start
// ---------------------------------------------------------

createSandboxControls();

reset();