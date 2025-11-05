import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def run(state):
    tts_files = state.get("tts_files", [])
    image_files = state.get("image_files", [])
    shotlist = state.get("shotlist", [])

    # shotlist 타입 정리
    if isinstance(shotlist, dict):
        shots = shotlist.get("shots", [])
    elif isinstance(shotlist, list):
        shots = shotlist
    else:
        shots = []

    if not tts_files or not image_files or not shots:
        print("[video_agent] 스킵됨 (필수 자료 부족)")
        return state

    out_dir = "outputs/video"
    os.makedirs(out_dir, exist_ok=True)

    clips = []
    for i, (tts, img) in enumerate(zip(tts_files, image_files)):
        try:
            audio = AudioFileClip(tts)
            img_clip = ImageClip(img).set_duration(audio.duration)
            img_clip = img_clip.set_audio(audio)
            clips.append(img_clip)
        except Exception as e:
            print(f"[video_agent] shot {i+1} 오류: {e}")

    if not clips:
        print("[video_agent] 클립 없음 → 스킵")
        return state

    final = concatenate_videoclips(clips, method="compose")
    out_path = os.path.join(out_dir, "final_video.mp4")
    final.write_videofile(out_path, fps=24)

    state["video_file"] = out_path
    print(f"[video_agent] 저장됨: {out_path}")
    return state
