import os
import yt_dlp
import whisper
import subprocess
import re

def get_youtube_url():
    url = input("🎬 유튜브 URL을 입력하세요: ").strip()
    if not url.startswith("http"):
        raise ValueError("❌ 유효하지 않은 URL입니다.")
    return url

def get_save_directory():
    dir_path = input("💾 저장 폴더 (기본: 현재 폴더): ").strip()
    if dir_path == "":
        dir_path = os.getcwd()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"📁 폴더 생성됨: {dir_path}")
    return dir_path

def clean_filename(filename):
    """
    Windows에서 사용할 수 없는 문자와 모든 종류의 공백(앞, 뒤, 중간 포함) 제거
    """
    # 특수문자 제거 (Windows 금지)
    filename = re.sub(r'[<>:"/\\|?*\n\r\t♪]', '', filename)
    # 모든 공백 완전 제거
    filename = re.sub(r'\s+', '', filename)
    return filename

def download_youtube_with_ytdlp(url, save_path):
    """
    yt-dlp로 최고화질 영상 다운로드 (파일명 정리 포함)
    """
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
        video_title = info.get('title', 'video')
        extension = info.get('ext', 'mp4')
        safe_title = clean_filename(video_title)
        output_filename = f"{safe_title}.{extension}"
        outtmpl = os.path.join(save_path, output_filename)

        # 실제 다운로드 (깨끗한 파일명으로)
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"\n✅ 다운로드 완료: {outtmpl}")
        return outtmpl

    except Exception as e:
        print(f"❌ 다운로드 중 오류 발생: {e}")
        return None

def generate_subtitle_whisper(video_path):
    """
    Whisper로 SRT 자막 생성 (파일명 오류 대응 포함)
    """
    print("🧠 Whisper 모델 로딩 중...")
    model = whisper.load_model("base")  # 필요시 'small', 'medium', 'large' 가능

    print("🗣️ 음성 인식 중...")
    result = model.transcribe(video_path)

    srt_path = os.path.splitext(video_path)[0] + ".srt"
    print(f"💬 SRT 생성 중: {srt_path}")

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"]):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")

    print(f"✅ 자막 저장 완료: {srt_path}")

def burn_subtitle_to_video(video_path):
    """
    ffmpeg를 사용하여 자막(srt)을 mp4에 하드코딩하여 내장된 영상 생성
    """
    srt_path = os.path.splitext(video_path)[0] + ".srt"
    output_path = os.path.splitext(video_path)[0] + "_subtitled.mp4"

    if not os.path.exists(srt_path):
        print("❗ SRT 자막 파일이 존재하지 않습니다.")
        return

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy",  # 오디오는 재인코딩하지 않음
        output_path
    ]

    print("🎞️ 자막을 영상에 하드코딩 중...")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 자막 삽입 완료! ▶ {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 자막 삽입 중 오류 발생:", e)

def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    print("📥 유튜브 동영상 다운로드 & 자막 생성 및 영상 자막 내장 스크립트")
    try:
        url = get_youtube_url()
        folder = get_save_directory()
        video_path = download_youtube_with_ytdlp(url, folder)
        if video_path and os.path.exists(video_path):
            generate_subtitle_whisper(video_path)
            burn_subtitle_to_video(video_path)
        else:
            print("⚠️ 영상 다운로드에 실패했습니다.")
    except ValueError as ve:
        print(f"입력 오류: {ve}")
    except KeyboardInterrupt:
        print("\n⛔ 사용자에 의해 작업이 중단되었습니다.")

if __name__ == "__main__":
    main()
