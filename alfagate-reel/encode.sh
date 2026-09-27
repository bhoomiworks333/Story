#!/bin/sh
# Encodes frames/ + soundtrack.wav into the final reel (H.264, 1080x1920, 24 fps, AAC).
set -e
cd "$(dirname "$0")"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
mkdir -p ../output
$FF -y -loglevel error -framerate 24 -i frames/f%05d.jpg -i soundtrack.wav -c:v libx264 -pix_fmt yuv420p -crf 17 -preset slow \
  -profile:v high -c:a aac -b:a 192k -shortest -movflags +faststart ../output/alfagate_reel.mp4
echo ../output/alfagate_reel.mp4
