"""Render Harvey reel cards (1080x960 CSS px, exported at 2x) and overlays as transparent PNGs."""
import asyncio, sys, base64
from playwright.async_api import async_playwright
OUT = sys.argv[1]; HEADER_PNG = sys.argv[2]
Y = "#FFD600"
hdr = base64.b64encode(open(HEADER_PNG, "rb").read()).decode()
BASE = """<style>*{margin:0;padding:0;box-sizing:border-box}html,body{background:transparent}
body{font-family:Inter,Montserrat,'Noto Color Emoji',sans-serif;color:#fff}
.card{width:1080px;height:960px;background:#111;border-radius:32px;position:relative;overflow:hidden}
.safe{position:absolute;left:0;right:0;top:60px;height:770px;display:flex;flex-direction:column;align-items:center;justify-content:center}
</style>"""
def card(inner): return BASE + f'<div class="card"><div class="safe">{inner}</div></div>'
CAL = '<svg width="96" height="96" viewBox="0 0 24 24" fill="none" stroke="#FFD600" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/><path d="M8.5 15l2.3 2.3 4.7-4.6"/></svg>'
cards = {
"card_blank": card(""),
"card_repo": card(f'<img src="data:image/png;base64,{hdr}" style="width:1000px;border-radius:18px;box-shadow:0 10px 40px rgba(0,0,0,.6)">'),
"card_inputs_1": card(f'''<div style="width:900px;display:flex;flex-direction:column;gap:70px">
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:{Y};line-height:1">1</span><span style="font-size:76px;font-weight:700">What you sell</span></div>
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:#333;line-height:1">2</span><span style="font-size:76px;font-weight:700;visibility:hidden">Who you sell to</span></div></div>'''),
"card_inputs_0": card('''<div style="width:900px;display:flex;flex-direction:column;gap:70px">
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:#333;line-height:1">1</span><span style="font-size:76px;font-weight:700;visibility:hidden">What you sell</span></div>
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:#333;line-height:1">2</span><span style="font-size:76px;font-weight:700;visibility:hidden">Who you sell to</span></div></div>'''),
"card_inputs_2": card(f'''<div style="width:900px;display:flex;flex-direction:column;gap:70px">
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:{Y};line-height:1">1</span><span style="font-size:76px;font-weight:700">What you sell</span></div>
 <div style="display:flex;align-items:center;gap:40px"><span style="font-size:170px;font-weight:800;color:{Y};line-height:1">2</span><span style="font-size:76px;font-weight:700">Who you sell to</span></div></div>'''),
"card_email": card('''<div style="width:940px;background:#fff;color:#202124;border-radius:22px;overflow:hidden;font-family:Inter,sans-serif;box-shadow:0 10px 40px rgba(0,0,0,.5)">
 <div style="background:#f2f6fc;padding:22px 34px;font-size:30px;font-weight:600;color:#1f1f1f;display:flex;justify-content:space-between"><span>New message</span><span style="color:#5f6368">— ⤢ ✕</span></div>
 <div style="padding:16px 34px;border-bottom:1px solid #e0e0e0;font-size:29px;color:#5f6368">To&nbsp; <span style="color:#202124">Dana Ruiz &lt;dana@&hellip;&gt;</span></div>
 <div style="padding:16px 34px;border-bottom:1px solid #e0e0e0;font-size:30px;font-weight:600">Your "book online" button 404s</div>
 <div style="padding:24px 34px 30px;font-size:30px;line-height:1.45">Hi Dana,<br>Saw Maple &amp; Pine Dental just opened a second clinic. Congrats! Heads up: the booking link on your new page is broken.<br>We fix exactly this for dental teams. Worth a 15-min call?<br>— Sam</div>
 <div style="padding:0 34px 28px"><span style="display:inline-block;background:#0b57d0;color:#fff;font-weight:600;font-size:28px;padding:14px 34px;border-radius:999px">Send</span></div></div>'''),
"card_reply": card('''<div style="width:900px;display:flex;flex-direction:column;gap:26px;font-family:Inter,sans-serif">
 <div style="align-self:flex-end;max-width:640px;background:#2b2b2b;color:#ddd;font-size:34px;line-height:1.35;padding:24px 32px;border-radius:34px 34px 8px 34px">…worth a 15-min call?</div>
 <div style="font-size:28px;color:#9a9a9a;margin-left:12px">Dana · Maple &amp; Pine Dental</div>
 <div style="align-self:flex-start;max-width:760px;background:#fff;color:#111;font-size:58px;font-weight:700;line-height:1.2;padding:32px 44px;border-radius:44px 44px 44px 10px">Sounds interesting. Thursday?</div></div>'''),
"card_booking": card(f'''<div style="display:flex;flex-direction:column;align-items:center;gap:34px;text-align:center">
 <div style="width:170px;height:170px;border-radius:40px;background:#1d1d1d;display:flex;align-items:center;justify-content:center">{CAL}</div>
 <div style="font-size:74px;font-weight:800;line-height:1.1">Sends your<br><span style="color:{Y}">booking link</span></div>
 <div style="font-size:34px;color:#9a9a9a;font-weight:500">auto-booking: on the roadmap</div></div>'''),
"card_heartbeat": card(f'''<div style="position:relative;width:560px;height:560px">
 <div style="position:absolute;inset:0;border-radius:50%;border:10px solid #2a2a2a"></div>
 <div style="position:absolute;top:-6px;left:50%;transform:translateX(-50%);background:#111;padding:0 22px;font-size:62px;font-weight:800">Wake</div>
 <div style="position:absolute;bottom:62px;right:-70px;background:#111;padding:6px 18px;font-size:62px;font-weight:800">Work</div>
 <div style="position:absolute;bottom:62px;left:-74px;background:#111;padding:6px 18px;font-size:62px;font-weight:800">Sleep</div>
 <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column">
  <div style="font-size:30px;color:#9a9a9a;font-weight:600;letter-spacing:2px">HEARTBEAT</div>
  <div style="font-size:64px;font-weight:800;color:{Y};margin-top:8px">every 15 min</div>
  <div style="font-size:26px;color:#777;margin-top:6px">(default)</div></div></div>'''),
"card_cost": card(f'''<div style="display:flex;flex-direction:column;align-items:center;gap:46px;text-align:center">
 <div style="font-size:96px;font-weight:800">Free <span style="color:{Y}">code</span></div>
 <div style="width:120px;height:6px;background:#333;border-radius:3px"></div>
 <div style="font-size:66px;font-weight:700;line-height:1.2">Runs on<br>Claude Pro / Max</div>
 <div style="font-size:30px;color:#9a9a9a">no API bill · open source (MIT)</div></div>'''),
}
overlays = {
"pill_opensource": f'<div style="display:inline-block;background:{Y};color:#000;font-weight:800;font-size:64px;letter-spacing:2px;padding:20px 54px;border-radius:999px">OPEN SOURCE</div>',
"label_approve": '<div style="display:inline-block;background:rgba(0,0,0,.72);color:#fff;font-weight:600;font-size:34px;padding:14px 30px;border-radius:999px">(after you approve, by default)</div>',
"label_demo": '<div style="display:inline-block;background:rgba(0,0,0,.65);color:#fff;font-weight:600;font-size:26px;padding:9px 20px;border-radius:999px">Harvey README · demo data</div>',
"cta": '<div style="display:inline-block;background:#fff;color:#000;font-weight:800;font-size:76px;padding:26px 50px;border-radius:24px">Comment <span style="background:#FFD600;padding:0 14px;border-radius:10px">HARVEY</span> <span style="font-family:\'Noto Color Emoji\'">👇</span></div>',
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 960}, device_scale_factor=2)
        for k, html in cards.items():
            await pg.set_content(BASE.replace("<style>", "<style>") + html if False else html); await pg.evaluate("document.fonts.ready")
            await (await pg.query_selector(".card")).screenshot(path=f"{OUT}/{k}.png", omit_background=True)
        for k, html in overlays.items():
            await pg.set_content(BASE + html); await pg.evaluate("document.fonts.ready")
            await (await pg.query_selector("body > div")).screenshot(path=f"{OUT}/{k}.png", omit_background=True)
        await b.close()
asyncio.run(main())
