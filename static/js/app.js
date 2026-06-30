const video = document.getElementById('video');
const predictedLetterField = document.getElementById('predictedLetter');
const confidenceText = document.getElementById('confidenceText');
const matchText = document.getElementById('matchText');
const targetButton = document.getElementById('randomButton');
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const targetLetterField = document.getElementById('targetLetter');
const targetImage = document.getElementById('targetImage');

let currentTarget = 'A';
let updateInterval = null;
let nextTargetTimer = null;
const captureCanvas = document.createElement('canvas');

function updateTarget(letter) {
  currentTarget = letter;
  targetLetterField.textContent = letter;
  targetImage.src = `/static/signs/Huruf ${letter}.png`;
  matchText.textContent = '';
}

function chooseRandomTarget() {
  if (!letters || !letters.length) return;
  const randomLetter = letters[Math.floor(Math.random() * letters.length)];
  updateTarget(randomLetter);
}

function showStatus(message, isSuccess = false) {
  matchText.textContent = message;
  matchText.style.color = isSuccess ? '#065f46' : '#7c2d12';

  if (isSuccess) {
    if (nextTargetTimer) {
      clearTimeout(nextTargetTimer);
    }
    nextTargetTimer = setTimeout(() => {
      chooseRandomTarget();
      nextTargetTimer = null;
    }, 1400);
  } else if (nextTargetTimer) {
    clearTimeout(nextTargetTimer);
    nextTargetTimer = null;
  }
}

async function setupCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('Webcam tidak didukung di browser ini.');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    await video.play();
  } catch (err) {
    console.error('Gagal membuka webcam:', err);
    alert('Tidak dapat mengakses webcam. Pastikan izin diberikan.');
  }
}

function captureFrameDataUrl() {
  if (!video.videoWidth || !video.videoHeight) return null;
  captureCanvas.width = video.videoWidth;
  captureCanvas.height = video.videoHeight;
  const ctx = captureCanvas.getContext('2d');
  ctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
  return captureCanvas.toDataURL('image/jpeg', 0.8);
}

async function requestPrediction() {
  const dataUrl = captureFrameDataUrl();
  if (!dataUrl) {
    return;
  }

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl }),
    });

    const payload = await response.json();
    const letter = payload.letter || 'Tidak terdeteksi';
    predictedLetterField.textContent = letter;
    confidenceText.textContent = payload.confidence ? `Kepercayaan: ${payload.confidence}` : '';

    if (currentTarget && letter === currentTarget && payload.recognized) {
      showStatus('Benar! Huruf Anda cocok.', true);
    } else if (currentTarget && letter === currentTarget && !payload.recognized) {
      showStatus('Prediksi cocok tetapi kepercayaan rendah. Ulangi dengan posisi lebih jelas.', false);
    } else if (letter !== 'Tidak terdeteksi') {
      showStatus('Salah. Silakan coba lagi.', false);
    } else {
      showStatus('Pose tidak terdeteksi. Pastikan tangan terlihat jelas.', false);
    }
  } catch (err) {
    console.error('Kesalahan prediksi:', err);
  }
}

function startSimulation() {
  if (!modelReady) {
    alert('Model belum tersedia. Jalankan train_model.py untuk menghasilkan model.pkl.');
    return;
  }

  startButton.disabled = true;
  stopButton.disabled = false;
  if (!video.srcObject) {
    setupCamera().then(() => {
      requestPrediction();
      updateInterval = setInterval(requestPrediction, 1400);
    });
  } else {
    requestPrediction();
    updateInterval = setInterval(requestPrediction, 1400);
  }
}

function stopSimulation() {
  startButton.disabled = false;
  stopButton.disabled = true;
  clearInterval(updateInterval);
  updateInterval = null;
  matchText.textContent = 'Simulasi dihentikan.';
  matchText.style.color = '#475569';
}

document.addEventListener('DOMContentLoaded', () => {
  updateTarget(currentTarget);
  targetButton.addEventListener('click', chooseRandomTarget);
  startButton.addEventListener('click', startSimulation);
  stopButton.addEventListener('click', stopSimulation);
});
