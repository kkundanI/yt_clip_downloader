import sys
import subprocess
import shutil

def check_ffmpeg():
    """Check if ffmpeg is available on the system."""
    if not shutil.which("ffmpeg"):
        print("+" + "-"*78 + "+")
        print("| WARNING: 'ffmpeg' was not found on your system!                            |")
        print("| ffmpeg is REQUIRED for downloading specific sections of videos             |")
        print("| and merging high-quality video and audio together properly.                |")
        print("|                                                                            |")
        print("| Please install it via:                                                     |")
        print("| Windows: 'winget install ffmpeg' or download from ffmpeg.org               |")
        print("| Mac: 'brew install ffmpeg'                                                 |")
        print("| Linux: 'sudo apt install ffmpeg'                                           |")
        print("+" + "-"*78 + "+\n")

def run_ytdlp(url, format_spec="bestvideo+bestaudio/best", section=None):
    """Run yt-dlp to download the video or clip."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", format_spec,
        "--merge-output-format", "mkv",
        # Save output in current directory with title and video ID
        "-o", "%(title)s_%(id)s.%(ext)s",
    ]
    
    if section:
        # The syntax for sections in yt-dlp is --download-sections "*start-end"
        # The '*' tells yt-dlp to process it via ffmpeg based on time.
        cmd.extend(["--download-sections", section])
        
    cmd.append(url)
    
    try:
        print("\n=> Running yt-dlp...")
        print("   Command: " + " ".join(cmd) + "\n")
        # Run process and wait for it to finish natively in the console
        subprocess.run(cmd, check=True)
        print("\n=== Download completed successfully! ===")
    except subprocess.CalledProcessError as e:
        print("\n[!] An error occurred during the download process.")
        print("    Ensure the URL is correct and yt-dlp is fully up-to-date.")
    except KeyboardInterrupt:
        print("\n\n[!] Download canceled by user.")

def get_quality_preference():
    print("\n--- Download Quality Settings ---")
    print("  [0] Best Quality Available (Default)")
    print("  [1] 1080p")
    print("  [2] 720p")
    print("  [3] 480p")
    print("  [4] 360p")
    print("  [5] 240p")
    print("  [6] 144p")
    
    try:
        q_choice = input("\nEnter your quality choice (0-6) [Default: 0]: ").strip()
    except KeyboardInterrupt:
        return None
        
    if not q_choice:
        q_choice = '0'
        
    quality_map = {
        '0': "bestvideo+bestaudio/best",
        '1': "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        '2': "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        '3': "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        '4': "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
        '5': "bestvideo[height<=240]+bestaudio/best[height<=240]/best",
        '6': "bestvideo[height<=144]+bestaudio/best[height<=144]/best"
    }
    
    # If invalid choice, default to best
    return quality_map.get(q_choice, "bestvideo+bestaudio/best")

def main():
    print("=========================================")
    print("       YouTube Clip Downloader OS        ")
    print("=========================================\n")
    
    check_ffmpeg()
    
    # Attempt to check if yt_dlp is installed python module
    try:
        import yt_dlp
    except ImportError:
        print("[!] ERROR: 'yt-dlp'python package is not installed.")
        print("    Please install it using: pip install yt-dlp")
        return

    print("Which approach would you like to use?")
    print("  [1] Approach 1: Download a YouTube Clip (provide a native clip URL)")
    print("  [2] Approach 2: Trim a standard YouTube Video (provide URL and start/end times)")
    
    try:
        choice = input("\nEnter your choice (1/2): ").strip()
    except KeyboardInterrupt:
        print("\nExiting...")
        return

    if choice == '1':
        print("\n=== Approach 1: Native YouTube Clip ===")
        try:
            url = input("Enter YouTube clip URL: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            return
            
        if not url:
            print("URL is required. Exiting...")
            return
            
        fmt = get_quality_preference()
        if not fmt:
            print("\nExiting...")
            return
            
        print("Downloading the exact clip as configured on YouTube...")
        run_ytdlp(url, format_spec=fmt)
        
    elif choice == '2':
        print("\n=== Approach 2: Trim Standard YouTube Video ===")
        try:
            url = input("Enter standard YouTube video URL: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            return
            
        if not url:
            print("URL is required. Exiting...")
            return
            
        print("\n--- Trim Settings ---")
        print("Enter timestamps in HH:MM:SS or MM:SS format (e.g. 01:30)")
        try:
            start_time = input("Start time: ").strip()
            end_time = input("End time: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            return
            
        if not start_time or not end_time:
            print("[!] Start and end times are required for trimming. Exiting...")
            return
            
        fmt = get_quality_preference()
        if not fmt:
            print("\nExiting...")
            return
            
        section_param = f"*{start_time}-{end_time}"
        print(f"\nPreparation complete. Will trim video from {start_time} to {end_time}.")
        run_ytdlp(url, format_spec=fmt, section=section_param)
        
    else:
        print(f"[!] Invalid choice '{choice}'. Please run the script again and select 1 or 2.")

if __name__ == "__main__":
    main()
