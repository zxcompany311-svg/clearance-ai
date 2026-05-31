import os
import yt_dlp
from openai import OpenAI

def get_video_metadata(url):
    """
    Extracts video metadata (title, description, tags) using yt-dlp.
    Does not download the video file itself.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "tags": info.get("tags", []),
                "duration": info.get("duration", 0),
            }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

def extract_audio_from_url(url, output_dir="temp"):
    """
    Downloads raw audio format (webm/m4a) from video URL using yt-dlp.
    Avoids post-processing with FFmpeg since FFmpeg is not installed.
    """
    os.makedirs(output_dir, exist_ok=True)
    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Ensure the downloaded file exists
            if os.path.exists(filename):
                return filename
            # Fallback check if extension was changed by yt-dlp during download
            video_id = info.get('id', '')
            if video_id:
                for f in os.listdir(output_dir):
                    if f.startswith(video_id) and os.path.isfile(os.path.join(output_dir, f)):
                        return os.path.join(output_dir, f)
            return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def transcribe_audio(audio_path, api_key, base_url):
    """
    Transcribes downloaded audio using OpenAI Whisper API.
    """
    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            # Extract transcription content
            if hasattr(transcription, "text"):
                return transcription.text
            elif isinstance(transcription, dict):
                return transcription.get("text", "")
            return str(transcription)
    except Exception as e:
        print(f"Whisper transcription error: {e}")
        raise e
