set -e
S=/tmp/claude-0/-home-user-Story/36acd9cc-27ae-5c99-99b1-9679f0dc2ed8/scratchpad/hol; U=/root/.claude/uploads/36acd9cc-27ae-5c99-99b1-9679f0dc2ed8; cd $S
C2=$U/346dfe44-11241.mp4; C3=$U/3317536f-11242.mp4; C4=$U/3fd5b750-11243.mp4
G="eq=contrast=1.07:saturation=1.14:gamma=0.98,colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.04,vignette=angle=PI/5"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -an"
FF="ffmpeg -nostdin -v error -y"
# P1: walk, normal then 0.5x slow-mo (motion-interpolated), slow push
$FF -ss 1.2 -t 0.6 -i $C3 -vf "scale=1080:1920,fps=30" $ENC p1a.mp4
$FF -ss 1.8 -t 0.9 -i $C3 -vf "scale=1080:1920,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir,setpts=2*PTS,fps=30" $ENC p1b.mp4
$FF -i p1a.mp4 -i p1b.mp4 -filter_complex "[0][1]concat=n=2:v=1,scale=2160:3840,zoompan=z='1+0.0008*on':d=1:x='iw/2-iw/zoom/2':y='ih*0.6-ih/zoom*0.6':s=1080x1920:fps=30,$G" $ENC p1.mp4
# P2: wide under the arch, slow push toward him
$FF -ss 1.0 -t 2.6 -i $C4 -vf "zoompan=z='1+0.0019*on':d=1:x='(iw-iw/zoom)*0.75':y='(ih-ih/zoom)*0.65':s=1080x1920:fps=30,$G" $ENC p2.mp4
# P3: 3-panel 'everywhere' split, panels appear one by one
$FF -ss 1.5 -t 2.0 -i $C3 -ss 1.0 -t 2.0 -i $C4 -ss 9.3 -t 2.0 -i $C2 -f lavfi -t 2 -i "color=black:s=1080x1920:r=30" -filter_complex "\
[0]scale=1080:1920,fps=30,crop=1080:632:0:1180,$G[a];[1]scale=1080:1920,fps=30,crop=1080:632:0:880,$G[b];[2]scale=1080:1920,fps=30,crop=1080:632:0:1150,$G[c];\
[3][a]overlay=0:0:enable='gte(t,0)'[x];[x][b]overlay=0:644:enable='gte(t,0.35)'[y];[y][c]overlay=0:1288:enable='gte(t,0.7)'" $ENC -t 2 p3.mp4
# P4: push-in, then punch zoom onto the laptop in the last 0.5s
$FF -ss 5.5 -t 3.8 -i $C2 -vf "zoompan=z='if(lt(on,99),1,min(1.7,1+0.7*(on-99)/6))':d=1:x='(iw-iw/zoom)*0.6':y='(ih-ih/zoom)*0.76':s=1080x1920:fps=30,$G" $ENC p4.mp4
# join: whip-blur into P2, hard cut into split, zoom transition into P4
$FF -i p1.mp4 -i p2.mp4 -i p3.mp4 -i p4.mp4 -filter_complex "\
[0][1]xfade=transition=hblur:duration=0.25:offset=2.15[v1];[v1][2]xfade=transition=fade:duration=0.08:offset=4.42[v2];[v2][3]xfade=transition=zoomin:duration=0.3:offset=6.12,noise=alls=3:allf=t,format=yuv420p[v]" -map "[v]" -c:v libx264 -preset slow -crf 18 -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 video.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4); echo dur $D
# ambience: quiet room tone from the arch clip, under where music will go
$FF -ss 0 -t $D -i $C4 -vn -af "highpass=f=100,afftdn=nf=-35,loudnorm=I=-24:TP=-3,afade=t=in:d=0.3,afade=t=out:st=$(echo "$D-0.4"|bc):d=0.4" -c:a aac -b:a 192k amb.m4a
$FF -i video.mp4 -i amb.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart /home/user/Story/edits/founder_holiday_v3_creative.mp4
