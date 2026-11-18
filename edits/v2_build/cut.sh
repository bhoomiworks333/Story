set -e
S=/tmp/claude-0/-home-user-Story/36acd9cc-27ae-5c99-99b1-9679f0dc2ed8/scratchpad; U=/root/.claude/uploads/36acd9cc-27ae-5c99-99b1-9679f0dc2ed8
cd $S/seg; rm -f *.mp4 list.txt
declare -A F=([DRIVE]=$U/d3001bbf-IMG_6676.MOV [YARD]=$U/01a52146-1118_1.mp4 [ENT]=$U/12912e0b-1118_13.mp4 [RAW]=$U/f1d9dd26-1118_11.mp4 [LINE]=$U/d8df977a-1118_12.mp4)
i=0
while read src ss d; do
 [ -z "$src" ] && continue
 i=$((i+1)); n=$(printf %02d $i)
 VF=""; [ "$src" = DRIVE ] && VF="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
 ffmpeg -nostdin -v error -y -ss $ss -t $d -i "${F[$src]}" -vf "${VF}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p,setsar=1" -af "aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.05,afade=t=out:st=$(echo "$d-0.05"|bc):d=0.05" -c:v libx264 -preset fast -crf 18 -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k $n.mp4
 echo "file '$n.mp4'" >> list.txt
done < $S/shots.txt
ffmpeg -nostdin -v error -y -f lavfi -i "color=c=0x15122E:s=1080x1920:r=30:d=3.6" -f lavfi -i "anullsrc=r=48000:cl=stereo" -t 3.6 -c:v libx264 -crf 18 -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k 99.mp4; echo "file '99.mp4'" >> list.txt
ffmpeg -nostdin -v error -y -f concat -safe 0 -i list.txt -c copy ../base_v2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ../base_v2.mp4
