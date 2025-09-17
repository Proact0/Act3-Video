import os
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

# 오디오 / 이미지 경로 확인
audio_dir = "outputs/audio"
image_dir = "outputs/images"
out_dir = "outputs/video"

os.makedirs(out_dir, exist_ok=True)

tts_files = sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")])
image_files = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(".jpg")])

print("오디오 파일:", tts_files)
print("이미지 파일:", image_files)

if not tts_files or not image_files:
    raise RuntimeError("오디오 또는 이미지 파일이 없습니다!")

clips = []
for i, audio_path in enumerate(tts_files):
    img_path = image_files[i] if i < len(image_files) else image_files[-1]

    audio_clip = AudioFileClip(audio_path)
    img_clip = (
        ImageClip(img_path)
        .set_duration(audio_clip.duration)
        .set_audio(audio_clip)
        .resize((720, 1280))  # 세로 비율
    )
    clips.append(img_clip)

# 이어붙이기
final = concatenate_videoclips(clips, method="compose")
out_path = os.path.join(out_dir, "final.mp4")
final.write_videofile(out_path, fps=24)

print(f"✅ 최종 영상 생성 완료: {out_path}")

