document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const imagePreview = document.getElementById('imagePreview');
    const previewContainer = document.getElementById('previewContainer');
    const uploadContent = document.getElementById('uploadContent');
    const removeBtn = document.getElementById('removeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Results DOM
    const resultsPanel = document.getElementById('resultsPanel');
    const scorePath = document.getElementById('scorePath');
    const scoreText = document.getElementById('scoreText');
    const verdictTitle = document.getElementById('verdictTitle');
    const explanationText = document.getElementById('explanationText');
    const errorBanner = document.getElementById('errorBanner');

    // Badges & Details
    const c2paBadge = document.getElementById('c2paBadge');
    const watermarkBadge = document.getElementById('watermarkBadge');
    const metadataBadge = document.getElementById('metadataBadge');
    const forensicBadge = document.getElementById('forensicBadge');
    const traceList = document.getElementById('traceList');

    let selectedFile = null;

    // --- Drag & Drop Handlers ---

    dropZone.addEventListener('click', () => {
        if (!selectedFile) fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // prevent clicking dropZone
        resetUI();
    });

    function handleFileSelect(file) {
        // Validate basic rules on frontend
        const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            showError("Invalid file type. Please upload a JPEG, PNG, or WEBP.");
            return;
        }

        if (file.size > 50 * 1024 * 1024) { // 50MB
            showError("File too large. Maximum size is 50MB.");
            return;
        }

        selectedFile = file;
        hideError();

        // Show Preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            uploadContent.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            analyzeBtn.disabled = false;
            resultsPanel.classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    function resetUI() {
        selectedFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        uploadContent.classList.remove('hidden');
        previewContainer.classList.add('hidden');
        analyzeBtn.disabled = true;
        resultsPanel.classList.add('hidden');
        hideError();
    }

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove('hidden');
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    // --- API Integration ---

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI Loading State
        analyzeBtn.disabled = true;
        analyzeBtn.querySelector('span').textContent = 'Analyzing...';
        loadingSpinner.classList.remove('hidden');
        resultsPanel.classList.add('hidden');
        hideError();

        // Ensure path uses localhost:8000 where our FastAPI Docker is bound
        const apiUrl = 'http://localhost:8000/api/v1/analyze';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
            console.error('Analysis error:', error);
            showError(`Analysis Failed: ${error.message}`);
        } finally {
            // Restore btn
            analyzeBtn.disabled = false;
            analyzeBtn.querySelector('span').textContent = 'Analyze Image';
            loadingSpinner.classList.add('hidden');
        }
    });

    function renderResults(data) {
        resultsPanel.classList.remove('hidden');

        // Process Score
        const probabilityPercent = Math.round(data.ai_generated_probability * 100);
        scoreText.textContent = `${probabilityPercent}%`;

        // Animate Circle
        // SVG Circle arc length is 100, so dasharray maps cleanly to percentage 
        scorePath.setAttribute('stroke-dasharray', `${probabilityPercent}, 100`);

        // Colorize based on threat level
        scorePath.parentElement.classList.remove('score-real', 'score-mixed', 'score-ai');
        if (probabilityPercent < 30) {
            scorePath.parentElement.classList.add('score-real');
            verdictTitle.textContent = "Likely Authentic";
            verdictTitle.style.color = "var(--success)";
        } else if (probabilityPercent >= 30 && probabilityPercent < 70) {
            scorePath.parentElement.classList.add('score-mixed');
            verdictTitle.textContent = "Mixed Signals";
            verdictTitle.style.color = "var(--warning)";
        } else {
            scorePath.parentElement.classList.add('score-ai');
            verdictTitle.textContent = "AI Generated";
            verdictTitle.style.color = "var(--danger)";
        }

        explanationText.textContent = data.explanation;

        // C2PA
        if (data.c2pa_verified) {
            c2paBadge.textContent = "Verified";
            c2paBadge.className = "badge safe";
        } else {
            c2paBadge.textContent = "Unverified";
            c2paBadge.className = "badge neutral";
        }

        // Watermark
        if (data.watermark_detected) {
            watermarkBadge.textContent = "Detected";
            watermarkBadge.className = "badge detected";
        } else {
            watermarkBadge.textContent = "None";
            watermarkBadge.className = "badge safe";
        }

        // Metadata
        if (data.metadata_ai_hint) {
            metadataBadge.textContent = "AI Flags Found";
            metadataBadge.className = "badge detected";
        } else {
            metadataBadge.textContent = "Clean";
            metadataBadge.className = "badge safe";
        }

        // Forensic Traces Array
        traceList.innerHTML = '';
        if (data.forensic_signals && data.forensic_signals.length > 0) {
            forensicBadge.textContent = `${data.forensic_signals.length} Signals`;
            forensicBadge.className = "badge detected";

            data.forensic_signals.forEach(sig => {
                const tr = document.createElement('div');
                tr.className = 'trace-item';
                // format like: "diffusion_synthetic_noise" -> "Diffusion Synthetic Noise"
                tr.textContent = sig.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                traceList.appendChild(tr);
            });
        } else {
            forensicBadge.textContent = "None";
            forensicBadge.className = "badge safe";
        }
    }
});
