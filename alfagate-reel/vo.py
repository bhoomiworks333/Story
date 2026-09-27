# Generates the Hinglish voiceover with Kokoro (hm_psi). Text is Devanagari so the Hindi voice pronounces it naturally;
# subtitles use the Roman lines. Output: vo/vo_N.wav + vo/vo.json (durations).
import json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = sys.argv[1] if len(sys.argv) > 1 else '.'
LINES = [
 ("क्या आपको पता है… साढ़े चार हज़ार साल पहले भी, लोग अपनी सोसाइटी इतनी ऑर्गनाइज़्ड रखते थे?", "Kya aapko pata hai… 4,500 saal pehle bhi, log apni society itni organized rakhte the?"),
 ("मोहनजोदड़ो में, कवर्ड ड्रेनेज।", "Mohenjo-daro mein, covered drainage."),
 ("हड़प्पा में, प्लान्ड स्ट्रीट्स।", "Harappa mein, planned streets."),
 ("धोलावीरा में, वॉटर मैनेजमेंट।", "Dholavira mein, water management."),
 ("गेट पे, आज भी रजिस्टर।", "Gate pe, aaj bhi register."),
 ("मेंटेनेंस, व्हाट्सऐप पे।", "Maintenance, WhatsApp pe."),
 ("कंप्लेंट्स अलग। हिसाब अलग।", "Complaints alag. Hisaab alag."),
 ("टेक्नोलॉजी इतनी आगे आ गई…", "Technology itni aage aa gayi…"),
 ("तो सोसाइटी मैनेजमेंट क्यों नहीं?", "…toh society management kyun nahi?"),
 ("ऑर्गनाइज़्ड रहना, हमें हमेशा से आता था। बस, टूल्स बदल गए।", "Organized rehna humein hamesha se aata tha. Bas tools badal gaye."),
 ("विज़िटर्स, मेंटेनेंस, कंप्लेंट्स… सब एक ऐप में।", "Visitors, maintenance, complaints… sab ek app mein."),
 ("अल्फ़ागेट। अपनी सोसाइटी को, स्मार्टर तरीके से मैनेज कीजिए।", "AlfaGate. Apni society ko smarter tareeke se manage kijiye."),
]
k = Kokoro(f"{M}/kokoro-v1.0.onnx", f"{M}/voices-v1.0.bin")
out = []
for i, (hi, ro) in enumerate(LINES):
    s, sr = k.create(hi, voice="hm_psi", speed=1.08, lang="hi")
    # trim leading/trailing silence
    a = np.abs(s) > 0.01; idx = np.where(a)[0]
    s = s[max(0, idx[0] - 800): idx[-1] + 2400]
    sf.write(f"vo/vo_{i}.wav", s, sr)
    out.append({"i": i, "text": ro, "dur": round(len(s) / sr, 3)})
    print(i, round(len(s) / sr, 2), ro)
json.dump({"sr": sr, "lines": out}, open("vo/vo.json", "w"), ensure_ascii=False, indent=1)
