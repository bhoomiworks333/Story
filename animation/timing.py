# Builds the story-time -> video-time warp so each voiceover line fits its scene window.
# Story time = the original 57 s animation timeline. Video time = the final cut.
import json
SUB = [(2.3, 5.0), (5.3, 7.9), (8.3, 11.3), (19.3, 21.3), (21.6, 23.7), (24.0, 27.5), (28.6, 30.6), (30.9, 34.3), (34.7, 37.2)]
STORY_END = 57.0
PAD = 0.35
durs = json.load(open('vo/vo_durs.json'))
pts = [(0.0, 0.0)]
v = 0.0; s = 0.0
for (a, b), d in zip(SUB, durs):
    v += a - s; pts.append((a, v))
    v += max(b - a, d + PAD); pts.append((b, v))
    s = b
v += STORY_END - s; pts.append((STORY_END, v))
starts = [p[1] for p in pts[1:-1:2]]
json.dump({'warp': pts, 'video_duration': round(v, 3), 'vo_starts': starts}, open('warp.json', 'w'), indent=1)
open('warp.js', 'w').write('window.WARP = ' + json.dumps(pts) + ';\nwindow.VIDEO_DURATION = ' + str(round(v, 3)) + ';\n')
print(round(v, 2), [round(x, 2) for x in starts])
