#!/bin/sh
# encode.sh <frames folder> <out.mp4> [width]: frames at their real rate, H.264
fps=$(cat "$1/fps.txt")
ffmpeg -v error -y -framerate "$fps" -i "$1/f%05d.jpg" -vf "scale=${3:-1280}:-2:flags=lanczos,fps=12" \
  -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart -an "$2"
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate -of default=nw=1 "$2"
ffmpeg -v error -i "$2" -f null - && echo decodes
