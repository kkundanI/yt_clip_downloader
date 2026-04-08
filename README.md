# 🎬 YouTube Clip Downloader OS

A simple, interactive, and powerful command-line tool built in Python to download entire YouTube videos or specific trimmed clips seamlessly. It supports both native YouTube Clip URLs and manual custom time-stamped trimming.

## ✨ Features

- **Native Clip Support:** Instantly download perfect clips using native `youtube.com/clip/...` URLs. No need to manually provide timestamps.
- **Custom Video Trimming:** Precisely extract any section of a standard YouTube video by simply providing the Start and End times.
- **Configurable Quality:** Choose exactly the resolution you want, from the absolute best available down to 144p, dynamically for each download.
- **High Quality:** Prompts and fetches your preferred quality video and audio streams available and merges them losslessly into a clean `.mkv` file.
- **Interactive CLI:** An extremely easy-to-use guided command-line interface.

## ⚙️ Prerequisites

You must have the following installed on your system:

1. **Python 3.7+**
2. [**ffmpeg**](https://ffmpeg.org/) (Crucial for accurately cutting/trimming videos and merging the high-quality audio and video streams together).

## 🚀 Installation

### 1. Install FFmpeg
The tool relies on `ffmpeg` heavily for processing video segments. Open your terminal as an Administrator and install it:
- **Windows:** `winget install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 2. Install Python Dependencies
Open your terminal in the project's folder, and install the required `yt-dlp` package from the `requirements.txt` file:
```cmd
pip install -r requirements.txt
```

## 💻 Usage

Run the script using Python:
```cmd
python yt_clip_downloader.py
```

Upon running, the script will explicitly ask you to choose your desired approach:

```text
Which approach would you like to use?
  [1] Approach 1: Download a YouTube Clip (provide a native clip URL)
  [2] Approach 2: Trim a standard YouTube Video (provide URL and start/end times)
```

Depending on your selection:

### [1] Approach 1: Native YouTube Clip URL
*Example: `https://youtube.com/clip/Ugkx...`*

If you select option 1, you will be prompted for a native clip URL (generated via YouTube's "Clip" button). The tool reads it automatically, securely fetches the boundaries pre-specified on YouTube, prompts you for the desired video quality, and downloads **only that exact segment**. 

### [2] Approach 2: Standard Video URL \& Custom Trimming
*Example: `https://youtube.com/watch?v=...`*

If you select option 2, you provide a standard video URL and you will be prompted to enter the precise `Start time` and `End time` using either `HH:MM:SS` or `MM:SS` formats (e.g., `01:30` to `02:00`). After entering the timestamps, the script will ask for your preferred video quality. It will then intelligently utilize zero-copy slicing to surgically extract only the requested segment, instead of downloading the whole multi-GB video.

### 🎛️ Quality Selection

For either approach, before downloading, you will be prompted to select your preferred video resolution:

```text
--- Download Quality Settings ---
  [0] Best Quality Available (Default)
  [1] 1080p
  [2] 720p
  [3] 480p
  [4] 360p
  [5] 240p
  [6] 144p
```

Simply enter the number corresponding to your choice and press Enter!

## 🛠️ Built With
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - The workhorse driving the stream extraction.
- **[FFmpeg](https://ffmpeg.org/)** - For ultra-fast stream slicing and audio/video muxing.
