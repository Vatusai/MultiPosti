# MultiPosti

**Modular Multi-Platform Video Publishing System**

MultiPosti is a modular, extensible application that automatically takes videos and publishes them across multiple social media platforms with AI-generated content. Built with a clean, modular architecture for easy maintenance and platform additions.

## 🏗️ New Modular Architecture

The project has been completely reorganized into a modular structure:

```
MultiPosti/
├── src/                          # Source code
│   ├── core/                     # Core functionality
│   │   ├── credentials_manager.py    # Centralized credentials management
│   │   ├── base_platform.py         # Base class for all platforms
│   │   └── platform_manager.py      # Platform management hub
│   └── platforms/                # Platform implementations
│       ├── youtube/              # YouTube implementation ✅
│       │   ├── youtube_platform.py  # YouTube API integration
│       │   └── setup_auth.py        # YouTube authentication setup
│       ├── facebook/             # Facebook/Instagram 🚧
│       │   └── facebook_platform.py
│       └── tiktok/               # TikTok 🚧
│           └── tiktok_platform.py
├── credentials/                  # Credentials storage (organized by platform)
│   ├── youtube/
│   │   ├── client_secret.json    # OAuth credentials
│   │   ├── youtube_token.json    # Access tokens (auto-generated)
│   │   └── api_key.txt          # API key (if needed)
│   ├── facebook/                 # Facebook credentials
│   └── tiktok/                   # TikTok credentials
├── scripts/                      # Main application scripts
│   └── main.py                   # CLI interface
├── data/                         # Application data
│   └── videos_to_publish/        # Videos ready for upload
└── config/                       # Configuration files
```

## 🚀 Quick Start (New Structure)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup YouTube (Working Now!)
```bash
# Your client_secret.json is already in credentials/youtube/
python src/platforms/youtube/setup_auth.py
```

### 3. Test the New System
```bash
# List platforms and status
python scripts/main.py list

# Upload a video
python scripts/main.py upload video.mp4 --platforms youtube --title "My Video" --description "Test upload"
```

### 4. Use Programmatically
```python
from src.core import PlatformManager

manager = PlatformManager()
manager.authenticate_platform('youtube')
result = manager.upload_video_to_platform('youtube', 'video.mp4', 'Title', 'Description')
```

## 🔑 Step 1: API Authentication (Legacy Info)

### 📹 YouTube (YouTube Data API v3)
- Create app in Google Cloud Console
- Activate YouTube Data API
- Obtain `client_id` and `client_secret`
- OAuth 2.0 flow → `access_token` and `refresh_token`

### 📱 Instagram & Facebook (Graph API)
- Create app in Meta for Developers
- Requires Business account + connected Instagram
- Required permissions:
  - `instagram_basic`
  - `pages_show_list`
  - `pages_read_engagement`
  - `pages_manage_posts`
  - `instagram_content_publish`

### 📱 TikTok (Content Posting API)
- Create app in TikTok Developers Console
- Activate permissions: `video.upload`, `video.publish`
- OAuth flow implementation

## 🎯 Step 2: Video Upload

Each uploader implements:
```python
upload_video(video_path, title, description, hashtags)
```

## 🤖 Step 3: Content Generator

Uses Claude or GPT to generate:
- **Engaging titles** optimized for each platform
- **Descriptions** with call-to-action
- **Platform-specific hashtags** for maximum reach

## 📆 Step 4: Automation

When a new video is saved:
1. Scheduler is triggered
2. Video is uploaded to all platforms simultaneously
3. Response, IDs, and links are saved for tracking

## 🚀 Features

- **Multi-platform publishing**: One-click publishing to TikTok, Instagram, Facebook, and YouTube
- **AI-powered content generation**: Automatic title, description, and hashtag creation
- **Authentication management**: Secure OAuth flows for all platforms
- **Scheduling system**: Automated video processing and publishing
- **Response tracking**: Save all upload responses and generated links

## 🛠️ Technology Stack

- **Backend**: FastAPI or Flask
- **AI Integration**: Claude or OpenAI GPT
- **Database**: SQLite for token storage
- **APIs**: TikTok Content Posting, Meta Graph API, YouTube Data API v3
- **Authentication**: OAuth 2.0 flows

## 📋 Setup Requirements

1. API credentials for all platforms
2. Business accounts for Instagram/Facebook
3. Developer apps registered on each platform
4. Python environment with required dependencies

## 🎵 DigiViolin Integration

Supports direct integration with DigiViolin streams for seamless video processing and publishing workflow.