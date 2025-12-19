# 🚀 Instagram Public Downloader - Production Platform

A **production-ready**, **secure**, and **scalable** web platform for downloading public Instagram reels and posts.

## ✨ Features

### Core Functionality
- ✅ **Single Post Download** - Download individual reels/posts directly (no ZIP)
- ✅ **Profile Bulk Download** - Download all public videos from a profile (as ZIP)
- ✅ **Smart Input Detection** - Automatically detects URL type or username
- ✅ **Caption Extraction** - Extract and display captions with copy functionality
- ✅ **Progress Tracking** - Real-time status updates and loaders

### Security & Performance
- 🔒 **Input Sanitization** - Prevents injection attacks and path traversal
- ⏱️ **Rate Limiting** - IP-based throttling (20 requests/minute)
- 🧹 **Auto Cleanup** - Files deleted after 30 minutes
- 🚫 **Public Content Only** - No login required, respects privacy
- ⚡ **Optimized Downloads** - Efficient video handling and compression

### User Experience
- 🎨 **Modern UI** - Clean, responsive design with dark/light mode
- 📱 **Mobile-First** - Fully responsive on all devices
- 🔄 **Real-time Feedback** - Status messages and progress indicators
- 💾 **Direct Downloads** - Single files downloaded directly, no unnecessary ZIPs

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask, Instaloader
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Server**: Gunicorn
- **Deployment**: Render/Railway compatible

## 📋 Installation

### Prerequisites
- Python 3.11 or higher
- pip

### Setup

1. **Clone the repository**
2. **Create virtual environment**
3. **Install dependencies**
4. **Create required directories**
5. **Run the application**
6. **Access the application**
