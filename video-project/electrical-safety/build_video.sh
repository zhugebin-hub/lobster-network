#!/bin/bash
# Create video from images with audio and subtitles

cd /home/admin/.openclaw/workspace/video-project/electrical-safety

# Create concat list with proper durations
# Total target: ~55 seconds (matching audio ~54s)
cat > concat_list.txt << 'EOF'
file 'opening.jpg'
duration 5
file 'slide1.jpg'
duration 5
file 'slide2.jpg'
duration 8
file 'slide3.jpg'
duration 8
file 'slide4.jpg'
duration 8
file 'slide5.jpg'
duration 8
file 'slide6.jpg'
duration 8
file 'ending.jpg'
duration 5
EOF

# Create the video from image sequence
# Using ffmpeg concat demuxer
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -i audio.mp3 \
  -vf "scale=1920:1080,format=yuv420p" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k -ar 44100 \
  -shortest \
  -movflags +faststart \
  video_no_subs.mp4 2>&1 | tail -5

echo "Video created (without subtitles)"
ls -la video_no_subs.mp4
