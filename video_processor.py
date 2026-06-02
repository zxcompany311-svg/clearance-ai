import os
import re
import time
from pathlib import Path

from openai import OpenAI


def _safe_filename(name):
    stem = Path(name or "uploaded_video").stem
    suffix = Path(name or "uploaded_video.mp4").suffix.lower() or ".mp4"
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._") or "uploaded_video"
    return f"{stem}_{int(time.time())}{suffix}"


def save_uploaded_video(uploaded_file, output_dir="uploads/video_refs"):
    """
    Saves a Streamlit UploadedFile to disk and returns the local path.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, _safe_filename(uploaded_file.name))
    current_pos = None
    try:
        current_pos = uploaded_file.tell()
    except Exception:
        pass
    data = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    with open(output_path, "wb") as f:
        f.write(data)
    if current_pos is not None:
        try:
            uploaded_file.seek(current_pos)
        except Exception:
            pass
    return output_path


def analyze_local_video(video_path, max_samples=12, max_cut_points=10, max_frames_to_scan=900):
    """
    Extracts lightweight visual evidence from a local video:
    - basic metadata
    - evenly sampled frames as a montage
    - approximate scene/cut change timestamps

    Returns a dict safe for Streamlit display and LLM prompt context.
    """
    try:
        import imageio.v3 as iio
        import numpy as np
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError(
            "Local video analysis requires imageio, imageio-ffmpeg, numpy and pillow. "
            "Please install the updated requirements.txt first."
        ) from exc

    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    meta = iio.immeta(path, plugin="FFMPEG")
    fps = float(meta.get("fps") or 25.0)
    duration_meta = float(meta.get("duration") or 0.0)
    size = meta.get("size") or meta.get("source_size") or (0, 0)

    frames = []
    total_seen = 0
    for frame in iio.imiter(path, plugin="FFMPEG"):
        if total_seen < max_frames_to_scan:
            frames.append(frame)
        total_seen += 1
        if total_seen >= max_frames_to_scan and duration_meta > 0 and total_seen / fps >= min(duration_meta, 30):
            break

    if not frames:
        raise RuntimeError("No frames could be read from the uploaded video.")

    scanned_duration = len(frames) / fps if fps else duration_meta
    duration = duration_meta if duration_meta and duration_meta >= scanned_duration * 0.7 else scanned_duration
    duration = max(duration, scanned_duration)

    sample_count = min(max_samples, len(frames))
    sample_indices = []
    if sample_count == 1:
        sample_indices = [0]
    else:
        for i in range(sample_count):
            sample_indices.append(round(i * (len(frames) - 1) / (sample_count - 1)))

    sample_frames = []
    thumbs = []
    thumb_w = 180
    thumb_h = max(1, int(thumb_w * (size[1] / size[0]))) if size and size[0] else 320
    for sample_no, idx in enumerate(sample_indices):
        t = idx / fps if fps else 0
        pil = Image.fromarray(frames[idx]).convert("RGB")
        sample_frames.append({
            "index": int(idx),
            "time": round(t, 2),
            "label": f"{t:.1f}s"
        })
        thumb = pil.resize((thumb_w, thumb_h))
        draw = ImageDraw.Draw(thumb)
        draw.rectangle((0, 0, 80, 24), fill=(0, 0, 0))
        draw.text((6, 5), f"{t:.1f}s", fill=(255, 255, 255))
        thumbs.append(thumb)

    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    montage = Image.new("RGB", (thumb_w * cols, thumb_h * rows), (245, 245, 245))
    for i, thumb in enumerate(thumbs):
        montage.paste(thumb, ((i % cols) * thumb_w, (i // cols) * thumb_h))

    prev = None
    scores = []
    for i, frame in enumerate(frames):
        small = Image.fromarray(frame).resize((36, 80)).convert("L")
        arr = np.asarray(small, dtype=np.float32)
        if prev is not None:
            scores.append((float(np.mean(np.abs(arr - prev))), i / fps if fps else 0, i))
        prev = arr

    cut_points = []
    for score, t, idx in sorted(scores, reverse=True):
        if score < 18:
            break
        if all(abs(t - existing["time"]) > 0.35 for existing in cut_points):
            cut_points.append({"time": round(t, 2), "score": round(score, 1), "frame": int(idx)})
        if len(cut_points) >= max_cut_points:
            break
    cut_points = sorted(cut_points, key=lambda item: item["time"])

    avg_shot_len = round(duration / max(len(cut_points) + 1, 1), 2)
    rhythm = "fast cut" if avg_shot_len <= 1.5 else "medium cut" if avg_shot_len <= 3 else "slow cut"

    analysis = {
        "file_name": path.name,
        "fps": round(fps, 2),
        "duration": round(duration, 2),
        "scanned_duration": round(scanned_duration, 2),
        "size": size,
        "sample_frames": sample_frames,
        "cut_points": cut_points,
        "estimated_shots": len(cut_points) + 1,
        "avg_shot_len": avg_shot_len,
        "rhythm": rhythm,
        "montage_image": montage,
    }
    analysis["prompt_context"] = build_video_breakdown_context(analysis)
    return analysis


def build_video_breakdown_context(analysis):
    size = analysis.get("size") or (0, 0)
    cut_times = ", ".join([f"{item['time']}s" for item in analysis.get("cut_points", [])]) or "No strong hard cuts detected"
    sample_times = ", ".join([item["label"] for item in analysis.get("sample_frames", [])])
    return f"""Uploaded Reference Video Visual Analysis:
- File: {analysis.get('file_name')}
- Duration: about {analysis.get('duration')} seconds
- Resolution: {size[0]}x{size[1]}
- FPS: {analysis.get('fps')}
- Estimated shot count: {analysis.get('estimated_shots')}
- Average shot length: {analysis.get('avg_shot_len')} seconds ({analysis.get('rhythm')})
- Strong visual cut timestamps: {cut_times}
- Keyframe montage timestamps: {sample_times}

Use the attached keyframe montage as visual evidence. Extract the filming logic, camera movement, composition pattern, object staging, hand/action rhythm, pacing, and ending shot structure. Then transfer only the reusable shooting method to the user's own product and scene.
"""

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
        import yt_dlp
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
        import yt_dlp
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
