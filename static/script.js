const feed = document.getElementById('feed');
const placeholder = document.getElementById('placeholder');

const btnWebcam = document.getElementById('btn-webcam');
const btnVideo = document.getElementById('btn-video');

const videoPanel = document.getElementById('video-panel');
const videoSelect = document.getElementById('video-select');
const loadVideoBtn = document.getElementById('load-video-btn');

const uploadInput = document.getElementById('video-upload');
const uploadBtn = document.getElementById('upload-btn');
const uploadStatus = document.getElementById('upload-status');

const statusText = document.getElementById('status-text');
const reloadBtn = document.getElementById('reload-btn');

let currentMode = 'webcam';
let currentFilename = '';

function showFeed(url, label) {
  feed.src = url;
  feed.style.display = 'block';

  placeholder.style.display = 'none';

  statusText.textContent = `Source: ${label}`;
}

function showPlaceholder(title, text) {
  feed.src = '';
  feed.style.display = 'none';

  placeholder.style.display = 'flex';

  placeholder.querySelector('.placeholder-title').textContent = title;
  placeholder.querySelector('.placeholder-text').textContent = text;
}

function startWebcam() {
  currentMode = 'webcam';
  currentFilename = '';

  showFeed(
    `/video_feed?mode=webcam&t=${Date.now()}`,
    'Live Camera'
  );
}

function startVideo(filename) {
  if (!filename) return;

  currentMode = 'video';
  currentFilename = filename;

  showFeed(
    `/video_feed?mode=video&filename=${encodeURIComponent(filename)}&t=${Date.now()}`,
    `Video: ${filename}`
  );
}

async function refreshVideoList(selectFilename = '') {
  try {
    const res = await fetch('/videos');
    const data = await res.json();
    
    videoSelect.innerHTML = '<option value="">Select a video...</option>';
    
    data.videos.forEach(name => {
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name;
      videoSelect.appendChild(option);
    });

    if (selectFilename) {
      videoSelect.value = selectFilename;
    }
  } catch (error) {
    console.error('Failed to load video list:', error);
  }
}

/* -----------------------------
   Live Camera
----------------------------- */
btnWebcam.addEventListener('click', () => {
  btnWebcam.classList.add('active');
  btnVideo.classList.remove('active');

  videoPanel.classList.remove('visible');

  startWebcam();
});

/* -----------------------------
   Video Mode
----------------------------- */
btnVideo.addEventListener('click', async () => {
  btnVideo.classList.add('active');
  btnWebcam.classList.remove('active');

  videoPanel.classList.add('visible');

  /* Do NOT automatically start a video. */
  showPlaceholder(
    'No video selected',
    'Select a video from the list or upload one'
  );

  await refreshVideoList();
});

/* -----------------------------
   Load Selected Video
----------------------------- */
loadVideoBtn.addEventListener('click', () => {
  const filename = videoSelect.value;

  if (!filename) {
    showPlaceholder(
      'No video selected',
      'Choose a video from the list first'
    );
    return;
  }

  startVideo(filename);
});

/* -----------------------------
   Upload Video
----------------------------- */
uploadBtn.addEventListener('click', async () => {
  const file = uploadInput.files[0];

  if (!file) {
    uploadStatus.textContent = 'Choose a video first';
    return;
  }

  uploadStatus.textContent = 'Uploading...';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/upload_video', {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    
    if (data.error) {
      uploadStatus.textContent = `Error: ${data.error}`;
      return;
    }
    
    uploadStatus.textContent = 'Upload complete';
    await refreshVideoList(data.filename);
    startVideo(data.filename);
  } catch (error) {
    uploadStatus.textContent = 'Upload failed';
    console.error(error);
  }
});

/* -----------------------------
   Restart Stream
----------------------------- */
reloadBtn.addEventListener('click', () => {
  if (currentMode === 'webcam') {
    startWebcam();
  } else if (currentFilename) {
    startVideo(currentFilename);
  }
});

/* -----------------------------
   Default Init
----------------------------- */
startWebcam();