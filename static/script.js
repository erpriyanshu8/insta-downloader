// Theme Management
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('.icon');
    icon.textContent = theme === 'light' ? '🌙' : '☀️';
}

// Form Handling
const form = document.getElementById('downloadForm');
const urlInput = document.getElementById('urlInput');
const submitBtn = document.getElementById('submitBtn');
const statusMessage = document.getElementById('statusMessage');
const resultSection = document.getElementById('resultSection');
const singleResult = document.getElementById('singleResult');
const profileResult = document.getElementById('profileResult');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    
    if (!url) {
        showStatus('Please enter a URL or username', 'error');
        return;
    }
    
    // Reset UI
    hideResults();
    setLoading(true);
    showStatus('Link received successfully ✅', 'success');
    
    setTimeout(() => {
        showStatus('Validating input...', 'info');
    }, 500);
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Download failed');
        }
        
        showStatus(data.message, 'success');
        
        if (data.type === 'single') {
            showSingleResult(data);
        } else if (data.type === 'profile') {
            showProfileResult(data);
        }
        
        // Scroll to result
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
        
    } catch (error) {
        showStatus(error.message, 'error');
    } finally {
        setLoading(false);
    }
});

function showSingleResult(data) {
    const captionText = document.getElementById('captionText');
    const downloadVideoBtn = document.getElementById('downloadVideoBtn');
    const copyCaptionBtn = document.getElementById('copyCaptionBtn');
    
    captionText.textContent = data.caption || 'No caption available';
    downloadVideoBtn.href = data.video_url;
    downloadVideoBtn.download = data.filename;
    
    copyCaptionBtn.onclick = () => {
        navigator.clipboard.writeText(data.caption || '').then(() => {
            const originalText = copyCaptionBtn.textContent;
            copyCaptionBtn.textContent = '✅ Copied!';
            setTimeout(() => {
                copyCaptionBtn.textContent = originalText;
            }, 2000);
        });
    };
    
    singleResult.style.display = 'block';
    profileResult.style.display = 'none';
    resultSection.style.display = 'block';
}

function showProfileResult(data) {
    const postCount = document.getElementById('postCount');
    const downloadZipBtn = document.getElementById('downloadZipBtn');
    
    postCount.textContent = data.post_count;
    downloadZipBtn.href = data.zip_url;
    downloadZipBtn.download = data.filename;
    
    profileResult.style.display = 'block';
    singleResult.style.display = 'none';
    resultSection.style.display = 'block';
}

function hideResults() {
    resultSection.style.display = 'none';
    singleResult.style.display = 'none';
    profileResult.style.display = 'none';
}

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    urlInput.disabled = isLoading;
    
    if (isLoading) {
        submitBtn.classList.add('loading');
    } else {
        submitBtn.classList.remove('loading');
    }
}

function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            if (statusMessage.classList.contains('success')) {
                statusMessage.style.display = 'none';
            }
        }, 5000);
    }
}

// Auto-focus input on load
window.addEventListener('load', () => {
    urlInput.focus();
});
