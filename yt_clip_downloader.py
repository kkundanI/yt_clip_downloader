import os
import sys
import re
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

def _update_ytdlp():
    """Ask yt-dlp to update itself (run once at session start)."""
    print("=> Checking for yt-dlp updates... ", end="", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--update"],
            check=False,
            capture_output=True,
            text=True,
        )
        # yt-dlp prints "yt-dlp is up to date" or "Updated yt-dlp to ..."
        output = (result.stdout + result.stderr).strip()
        if "up to date" in output.lower():
            print("already up to date.")
        elif "updated" in output.lower():
            print("updated to latest version.")
        else:
            print("done.")
    except Exception:
        print("skipped (could not run update check).")


def run_ytdlp(url, format_spec="bestvideo+bestaudio/best", section=None):
    """Run yt-dlp to download the video or clip."""
    output_dir = os.getcwd()

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", format_spec,
        "--merge-output-format", "mkv",
        "--no-playlist",          # never download a whole playlist by accident
        "-o", "%(title)s_%(id)s.%(ext)s",
    ]

    if section:
        # --download-sections "*start-end" tells yt-dlp to cut via ffmpeg.
        # --force-keyframes-at-cuts ensures frame-accurate cuts (avoids drift).
        cmd.extend([
            "--download-sections", section,
            "--force-keyframes-at-cuts",
        ])

    cmd.append(url)

    try:
        print("\n=> Running yt-dlp...")
        print("   Command: " + " ".join(cmd) + "\n")
        subprocess.run(cmd, check=True)
        print("\n=== Download completed successfully! ===")
        print(f"    Saved to: {output_dir}")
    except subprocess.CalledProcessError as exc:
        print("\n[!] yt-dlp exited with an error (exit code " + str(exc.returncode) + ").")
        print("    Check that the URL is correct and that yt-dlp is up to date.")
    except KeyboardInterrupt:
        print("\n\n[!] Download canceled by user.")

QUALITY_MAP = {
    '0': "bestvideo+bestaudio/best",
    '1': "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    '2': "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    '3': "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    '4': "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
    '5': "bestvideo[height<=240]+bestaudio/best[height<=240]/best",
    '6': "bestvideo[height<=144]+bestaudio/best[height<=144]/best",
}

def get_quality_preference():
    """Prompt the user to pick a quality. Loops until a valid choice or blank (default)."""
    while True:
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
            return QUALITY_MAP['0']  # default

        if q_choice in QUALITY_MAP:
            return QUALITY_MAP[q_choice]

        print(f"[!] '{q_choice}' is not a valid option. Please enter a number between 0 and 6.")


# Valid YouTube domains for URL validation
_YT_DOMAINS = re.compile(
    r'^https?://(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/'
)


def prompt_url(label):
    """
    Prompt for a YouTube URL, looping until the user enters a non-empty string
    that starts with a recognised YouTube domain.
    """
    while True:
        try:
            url = input(f"Enter {label}: ").strip()
        except KeyboardInterrupt:
            return None

        if not url:
            print("[!] URL cannot be empty. Please try again.")
            continue

        if not _YT_DOMAINS.match(url):
            print(
                "[!] That doesn't look like a YouTube URL.\n"
                "    Expected: https://youtube.com/... or https://youtu.be/..."
            )
            continue

        return url


# Accepts  H:MM:SS  HH:MM:SS  M:SS  MM:SS  (hours optional, 1-2 digits each)
_TS_PATTERN = re.compile(
    r'^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$'
)


def parse_timestamp(ts):
    """
    Parse a timestamp string (HH:MM:SS or MM:SS) into total seconds.
    Returns an int on success, or raises ValueError with a human-readable
    message on failure.
    """
    m = _TS_PATTERN.match(ts.strip())
    if not m:
        raise ValueError(
            f"'{ts}' is not a valid timestamp. "
            "Use HH:MM:SS or MM:SS format (e.g. 01:30 or 1:02:30)."
        )

    hours   = int(m.group(1)) if m.group(1) is not None else 0
    minutes = int(m.group(2))
    seconds = int(m.group(3))

    if minutes > 59:
        raise ValueError(f"Minutes value '{minutes}' is out of range (0-59).")
    if seconds > 59:
        raise ValueError(f"Seconds value '{seconds}' is out of range (0-59).")

    return hours * 3600 + minutes * 60 + seconds


def prompt_timestamp(label):
    """
    Prompt for a timestamp, looping until the user enters one in a
    recognised format (HH:MM:SS or MM:SS) with valid component ranges.
    Returns the raw string on success, or None if the user presses Ctrl-C.
    """
    while True:
        try:
            ts = input(f"{label} (HH:MM:SS or MM:SS): ").strip()
        except KeyboardInterrupt:
            return None

        if not ts:
            print("[!] Timestamp cannot be empty. Please try again.")
            continue

        try:
            parse_timestamp(ts)   # validates format + range
            return ts             # valid — hand back the original string
        except ValueError as exc:
            print(f"[!] Invalid timestamp — {exc}")


def main():
    print("=========================================")
    print("       YouTube Clip Downloader OS        ")
    print("=========================================\n")

    check_ffmpeg()

    # Check if yt_dlp is installed
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("[!] ERROR: 'yt-dlp' python package is not installed.")
        print("    Please install it using: pip install yt-dlp")
        return

    # Update yt-dlp once per session, before the first download
    _update_ytdlp()

    # ── Main menu loop ────────────────────────────────────────────────────────
    while True:
        print("\nWhich approach would you like to use?")
        print("  [1] Approach 1: Download a YouTube Clip (provide a native clip URL)")
        print("  [2] Approach 2: Trim a standard YouTube Video (provide URL and start/end times)")
        print("  [Q] Quit")

        try:
            choice = input("\nEnter your choice (1 / 2 / Q): ").strip().lower()
        except KeyboardInterrupt:
            print("\nExiting...")
            return

        if choice == 'q':
            print("Goodbye!")
            return

        elif choice == '1':
            print("\n=== Approach 1: Native YouTube Clip ===")

            url = prompt_url("YouTube clip URL")
            if url is None:           # Ctrl-C
                print("\nExiting...")
                return

            fmt = get_quality_preference()
            if fmt is None:           # Ctrl-C
                print("\nExiting...")
                return

            print("Downloading the exact clip as configured on YouTube...")
            run_ytdlp(url, format_spec=fmt)

        elif choice == '2':
            print("\n=== Approach 2: Trim Standard YouTube Video ===")

            url = prompt_url("standard YouTube video URL")
            if url is None:
                print("\nExiting...")
                return

            print("\n--- Trim Settings ---")
            print("Enter timestamps in HH:MM:SS or MM:SS format (e.g. 01:30 or 1:02:30)")

            # Loop until the user provides a logically valid start/end pair
            while True:
                start_time = prompt_timestamp("Start time")
                if start_time is None:
                    break                 # Ctrl-C — handled below

                end_time = prompt_timestamp("End time")
                if end_time is None:
                    start_time = None     # treat as Ctrl-C at outer level
                    break

                # Logical range check: end must be strictly after start
                if parse_timestamp(end_time) <= parse_timestamp(start_time):
                    print(
                        f"[!] End time ({end_time}) must be later than "
                        f"start time ({start_time}). Please try again."
                    )
                    continue              # re-ask both timestamps

                break                    # both timestamps are valid

            if start_time is None or end_time is None:
                print("\nExiting...")
                return

            fmt = get_quality_preference()
            if fmt is None:
                print("\nExiting...")
                return

            section_param = f"*{start_time}-{end_time}"
            print(f"\nPreparation complete. Will trim video from {start_time} to {end_time}.")
            run_ytdlp(url, format_spec=fmt, section=section_param)

        else:
            print(f"[!] '{choice}' is not a valid choice. Please enter 1, 2, or Q.")
            # Loop continues — user is NOT forced to restart the script.


if __name__ == "__main__":
    main()
