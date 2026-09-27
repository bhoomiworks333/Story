// 2D canvas content for the in-scene screens and paper: visitor register, chat, lock screen, spreadsheet, AlfaGate app.
// The chat UI is a generic messenger (no third-party branding). The AlfaGate UI is a PLACEHOLDER design in the brand
// purple until real app screenshots are supplied.
import { rng, clamp, range, easeOut, smooth } from './util.js';

export const PURPLE = '#7548E6', PURPLE_D = '#5A33C4', INK = '#1d2a6b';

function rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }
function text(c, s, x, y, font, color, align = 'left') { c.font = font; c.fillStyle = color; c.textAlign = align; c.textBaseline = 'alphabetic'; c.fillText(s, x, y); }

// ---------------- visitor register (both pages of an open book), 2048 × 1434
const REG = { W: 2048, H: 1434 };
const COLS = [['Date', 0.08], ['Visitor name', 0.25], ['Flat', 0.09], ['Purpose', 0.17], ['Mobile', 0.18], ['In', 0.07], ['Out', 0.07], ['Sign', 0.09]];
const ENTRIES = [
  ['26/9', 'Ramesh Kumar', 'B-304', 'Plumber', '98XXXXX210', '9:10', '10:05'],
  ['26/9', 'Swiggy', 'A-1102', 'Delivery', '—', '9:24', '9:31'],
  ['26/9', 'Anita Joshi', 'C-701', 'Guest', '97XXXXX455', '9:40', ''],
  ['26/9', 'Amazon', 'A-404', 'Parcel', '—', '10:02', '10:06'],
  ['26/9', 'Vikas (maid)', 'B-1203', 'Staff', '99XXXXX038', '10:15', ''],
  ['26/9', 'Suresh Electric', 'Club', 'AC repair', '88XXXXX771', '10:30', ''],
  ['26/9', 'Neha & family', 'A-1204', 'Guest', '98XXXXX623', '10:48', ''],
  ['26/9', 'Blinkit', 'C-305', 'Delivery', '—', '11:02', '11:09'],
  ['26/9', 'Tanker (water)', '—', 'Supply', '97XXXXX912', '11:20', ''],
  ['26/9', 'Rohit Sharma', 'B-802', 'Guest', '96XXXXX104', '11:34', ''],
  ['26/9', 'Courier', 'A-603', 'Docs', '—', '11:50', '11:53'],
  ['26/9', 'Pest control', 'C-1101', 'Service', '90XXXXX347', '12:05', ''],
];
export const LIVE_ENTRY = ['26/9', 'Rahul Verma', 'A-1204', 'Guest', '98XXXXX582', '12:18', ''];

export function makeRegister() {
  const base = document.createElement('canvas'); base.width = REG.W; base.height = REG.H;
  const c = base.getContext('2d'), R = rng(5);
  // paper with slight yellowing towards the edges and the spine shadow
  c.fillStyle = '#efe8d6'; c.fillRect(0, 0, REG.W, REG.H);
  for (let i = 0; i < 9000; i++) { c.fillStyle = `rgba(120,100,70,${R() * 0.05})`; c.fillRect(R() * REG.W, R() * REG.H, 2, 2); }
  for (const side of [0, 1]) {
    const g = c.createLinearGradient(side ? REG.W : 0, 0, REG.W / 2, 0);
    g.addColorStop(0, 'rgba(150,120,70,0.25)'); g.addColorStop(0.08, 'rgba(150,120,70,0)'); g.addColorStop(0.92, 'rgba(60,40,20,0)'); g.addColorStop(1, 'rgba(60,40,20,0.35)');
    c.fillStyle = g; c.fillRect(side ? REG.W / 2 : 0, 0, REG.W / 2, REG.H);
  }
  const rows = []; // [x0, width] per page
  for (const page of [0, 1]) {
    const x0 = page * REG.W / 2 + 70, w = REG.W / 2 - 140;
    rows.push([x0, w]);
    text(c, page ? 'Page 148' : 'VISITOR REGISTER · MAIN GATE', x0 + (page ? w : 0), 70, '600 26px Inter', '#6b5f4c', page ? 'right' : 'left');
    c.strokeStyle = 'rgba(180,60,60,0.55)'; c.lineWidth = 2; c.beginPath(); c.moveTo(x0, 100); c.lineTo(x0 + w, 100); c.stroke();
    let x = x0; c.strokeStyle = 'rgba(60,90,160,0.35)'; c.lineWidth = 1.5;
    for (const [name, f] of COLS) { text(c, name, x + 8, 135, '600 22px Inter', '#5b5242'); c.beginPath(); c.moveTo(x, 100); c.lineTo(x, REG.H - 60); c.stroke(); x += w * f; }
    c.beginPath(); c.moveTo(x0 + w, 100); c.lineTo(x0 + w, REG.H - 60); c.stroke();
    for (let y = 150; y < REG.H - 60; y += 48) { c.beginPath(); c.moveTo(x0, y); c.lineTo(x0 + w, y); c.stroke(); }
  }
  // handwritten entries: left page full, right page half
  const hand = (s, x, y, rot, size = 30) => { c.save(); c.translate(x, y); c.rotate(rot); text(c, s, 0, 0, `${size}px Kalam`, INK); c.restore(); };
  const writeRow = (page, row, e) => {
    const [x0, w] = rows[page]; let x = x0; const y = 150 + 48 * (row + 1) - 12;
    e.forEach((s, i) => { hand(s, x + 8 + (R() - 0.5) * 6, y + (R() - 0.5) * 4, (R() - 0.5) * 0.03, s.length > 12 ? 26 : 30); x += w * COLS[i][1]; });
    // signature squiggle
    c.strokeStyle = INK; c.lineWidth = 2.2; c.beginPath(); const sx = x + 10; c.moveTo(sx, y - 6);
    for (let k = 0; k < 6; k++) c.quadraticCurveTo(sx + k * 12 + 6, y - 22 + R() * 20, sx + k * 12 + 12, y - 6);
    c.stroke();
  };
  for (let i = 0; i < 24; i++) writeRow(0, i, ENTRIES[i % ENTRIES.length]);
  for (let i = 0; i < 11; i++) writeRow(1, i, ENTRIES[(i + 5) % ENTRIES.length]);
  // one entry scratched out
  c.strokeStyle = INK; c.lineWidth = 3; c.beginPath(); c.moveTo(rows[1][0] + 10, 150 + 48 * 7 - 22); c.lineTo(rows[1][0] + 520, 150 + 48 * 7 - 26); c.stroke();

  const live = document.createElement('canvas'); live.width = REG.W; live.height = REG.H;
  const lc = live.getContext('2d');
  // the entry being written now: row 11 on the right page; returns pen-tip position in texture px
  const row = 11, [x0, w] = rows[1], y = 150 + 48 * (row + 1) - 12;
  const cells = []; { let x = x0; LIVE_ENTRY.forEach((s, i) => { cells.push([s, x + 8]); x += w * COLS[i][1]; }); }
  function draw(u) { // u: 0..1 writing progress
    lc.clearRect(0, 0, REG.W, REG.H); lc.drawImage(base, 0, 0);
    lc.font = '30px Kalam'; lc.fillStyle = INK; lc.textAlign = 'left';
    const total = cells.reduce((a, [s]) => a + s.length, 0); let chars = Math.floor(u * total), tip = [cells[0][1], y];
    for (const [s, x] of cells) {
      if (chars <= 0) break;
      const part = s.slice(0, chars); lc.fillText(part, x, y); tip = [x + lc.measureText(part).width, y - 8]; chars -= s.length;
    }
    return { tip, W: REG.W, H: REG.H };
  }
  return { canvas: live, draw };
}

// ---------------- phone screen, 720 × 1560 (360 × 780 pt @2x)
export const PH = { W: 720, H: 1560 };
function statusBar(c, dark = false, time = '12:18') {
  const col = dark ? '#fff' : '#111';
  text(c, time, 52, 58, '600 30px Inter', col);
  c.fillStyle = col; for (let i = 0; i < 4; i++) c.fillRect(560 + i * 12, 50 - i * 6, 8, 8 + i * 6);
  rr(c, 620, 34, 52, 26, 7); c.strokeStyle = col; c.lineWidth = 2.5; c.stroke(); c.fillRect(624, 38, 34, 18);
}

const CHAT = [
  ['Mehta (A-402)', '#c2185b', 'Maintenance kab tak jama karna hai?', '12:02'],
  ['Sharma (B-1103)', '#1565c0', 'Maine payment kar diya, update kab hoga??', '12:04'],
  ['Priya (C-701)', '#2e7d32', 'Lift B phir se band hai. Third time this week', '12:05'],
  ['Secretary', '#6a1b9a', 'Receipt kal bhejta hoon. Excel update ho raha hai', '12:07'],
  ['Kapoor (A-1204)', '#ef6c00', 'Gate pe mere guest ko 20 min roka!', '12:09'],
  ['Iyer (B-506)', '#00838f', 'UPI number kaunsa hai society ka?', '12:10'],
  ['Mehta (A-402)', '#c2185b', 'Tanker ka hisaab kaun dega?', '12:12'],
  ['Joshi (C-305)', '#5d4037', 'Complaint kahan likhein? Register ya group?', '12:13'],
  ['Sharma (B-1103)', '#1565c0', '???', '12:14'],
];
export function drawChat(c, n, scroll = 0) {
  c.fillStyle = '#ece5dd'; c.fillRect(0, 0, PH.W, PH.H);
  // subtle wallpaper texture
  c.fillStyle = 'rgba(0,0,0,0.025)'; for (let y = 0; y < PH.H; y += 60) for (let x = (y / 60) % 2 * 30; x < PH.W; x += 60) c.fillRect(x, y, 6, 6);
  c.fillStyle = '#37474f'; c.fillRect(0, 0, PH.W, 190);
  statusBar(c, true);
  c.fillStyle = '#90a4ae'; c.beginPath(); c.arc(110, 135, 34, 0, 7); c.fill();
  text(c, 'GV', 110, 146, '700 28px Inter', '#fff', 'center');
  text(c, 'Green Valley Residents', 164, 128, '600 32px Inter', '#fff');
  text(c, '486 members', 164, 164, '400 24px Inter', 'rgba(255,255,255,0.75)');
  let y = PH.H - 170 + scroll;
  const msgs = CHAT.slice(0, Math.max(0, Math.floor(n)));
  const pop = n - Math.floor(n);
  for (let i = msgs.length - 1; i >= 0; i--) {
    const [who, col, msg, tm] = msgs[i];
    c.font = '400 30px Inter'; const lines = wrap(c, msg, 480);
    const h = 70 + lines.length * 40;
    y -= h + 18; if (y < 180) break;
    const s = i === msgs.length - 1 ? easeOut(clamp(pop * 3 + (n >= CHAT.length ? 1 : 0))) : 1;
    c.save(); c.translate(40, y + h); c.scale(s, s); c.translate(-40, -(y + h));
    c.globalAlpha = s; c.fillStyle = '#fff'; c.shadowColor = 'rgba(0,0,0,0.12)'; c.shadowBlur = 4; c.shadowOffsetY = 2;
    rr(c, 40, y, 560, h, 18); c.fill(); c.shadowColor = 'transparent';
    text(c, who, 64, y + 42, '600 26px Inter', col);
    lines.forEach((l, k) => text(c, l, 64, y + 84 + k * 40, '400 30px Inter', '#111'));
    text(c, tm, 580, y + h - 16, '400 22px Inter', '#888', 'right');
    c.restore();
  }
  c.fillStyle = '#f6f6f6'; c.fillRect(0, PH.H - 130, PH.W, 130);
  rr(c, 30, PH.H - 110, 560, 76, 38); c.fillStyle = '#fff'; c.fill();
  text(c, 'Message', 70, PH.H - 62, '400 28px Inter', '#999');
  c.fillStyle = '#607d8b'; c.beginPath(); c.arc(640, PH.H - 72, 38, 0, 7); c.fill();
}
function wrap(c, s, w) { const words = s.split(' '), out = []; let line = ''; for (const wd of words) { const tst = line ? line + ' ' + wd : wd; if (c.measureText(tst).width > w && line) { out.push(line); line = wd; } else line = tst; } out.push(line); return out; }

const NOTIFS = [
  ['Green Valley Residents', '47 new messages'], ['Committee (Official)', 'Sharma: Audit ke bills kahan hain?'], ['Security Desk', 'Missed call (3)'],
  ['Green Valley Residents', 'Priya: Lift B complaint kiska kaam hai?'], ['Maintenance Group', 'Iyer: Receipt nahi mila'], ['Unknown number', 'Aapka guest gate pe hai'],
  ['Green Valley Residents', '96 new messages'], ['Treasurer', 'Excel sheet mein galti hai'], ['Security Desk', 'Missed call (5)'],
  ['Parking Group', 'Kisi ne meri jagah car lagayi'], ['Green Valley Residents', '128 new messages'], ['Committee (Official)', 'Meeting kal 8 baje'],
];
export function drawLock(c, n, t, dim = 1) {
  const g = c.createLinearGradient(0, 0, PH.W, PH.H); g.addColorStop(0, '#2a3440'); g.addColorStop(1, '#10151b');
  c.fillStyle = g; c.fillRect(0, 0, PH.W, PH.H);
  statusBar(c, true);
  text(c, '12:18', PH.W / 2, 300, '500 150px Inter', 'rgba(255,255,255,0.92)', 'center');
  text(c, 'Friday, 26 September', PH.W / 2, 360, '500 30px Inter', 'rgba(255,255,255,0.8)', 'center');
  const k = Math.min(NOTIFS.length, Math.floor(n));
  for (let i = 0; i < k; i++) {
    const idx = k - 1 - i, [app, msg] = NOTIFS[idx];
    const y = 430 + i * 118, s = i === 0 ? easeOut(clamp((n - k) * 4 + 0.25)) : 1;
    if (y > PH.H - 140) break;
    c.globalAlpha = s; c.fillStyle = 'rgba(255,255,255,0.16)'; rr(c, 30, y, PH.W - 60, 104, 26); c.fill();
    c.fillStyle = app.startsWith('Security') ? '#e57373' : app.startsWith('Unknown') ? '#9e9e9e' : '#81c784';
    rr(c, 52, y + 24, 56, 56, 14); c.fill();
    text(c, app, 128, y + 44, '600 26px Inter', '#fff'); text(c, msg, 128, y + 82, '400 25px Inter', 'rgba(255,255,255,0.85)');
    text(c, 'now', PH.W - 56, y + 44, '400 22px Inter', 'rgba(255,255,255,0.6)', 'right');
    c.globalAlpha = 1;
  }
  if (dim < 1) { c.fillStyle = `rgba(0,0,0,${1 - dim})`; c.fillRect(0, 0, PH.W, PH.H); }
}

// ---------------- AlfaGate app (placeholder UI)
export function drawApp(c, t, icon) {
  // t: seconds since the app shot started
  c.fillStyle = '#f5f3fb'; c.fillRect(0, 0, PH.W, PH.H);
  const hg = c.createLinearGradient(0, 0, PH.W, 330); hg.addColorStop(0, PURPLE); hg.addColorStop(1, PURPLE_D);
  c.fillStyle = hg; rr(c, 0, -40, PH.W, 370, 48); c.fill();
  statusBar(c, true, '9:41');
  if (icon) { c.save(); rr(c, 44, 96, 72, 72, 18); c.clip(); c.drawImage(icon, 44, 96, 72, 72); c.restore(); }
  text(c, 'Good morning, Aarav', 136, 128, '700 32px Manrope', '#fff');
  text(c, 'Green Valley Residency · A-1204', 136, 166, '500 24px Inter', 'rgba(255,255,255,0.85)');
  // quick tiles
  const tiles = [['Visitors', '2 waiting'], ['Maintenance', '₹3,500 due'], ['Complaints', '1 open'], ['Payments', 'History']];
  tiles.forEach(([a, b], i) => {
    const x = 36 + i * 164, y = 216;
    c.fillStyle = '#fff'; c.shadowColor = 'rgba(60,30,140,0.18)'; c.shadowBlur = 16; c.shadowOffsetY = 6; rr(c, x, y, 148, 150, 24); c.fill(); c.shadowColor = 'transparent';
    c.fillStyle = 'rgba(117,72,230,0.12)'; c.beginPath(); c.arc(x + 44, y + 48, 26, 0, 7); c.fill();
    drawIcon(c, i, x + 44, y + 48);
    text(c, a, x + 18, y + 104, '600 21px Inter', '#1f1b2e'); text(c, b, x + 18, y + 132, '500 19px Inter', '#6f6a80');
  });
  // cards
  const card = (y, h) => { c.fillStyle = '#fff'; c.shadowColor = 'rgba(40,20,90,0.12)'; c.shadowBlur = 18; c.shadowOffsetY = 6; rr(c, 36, y, PH.W - 72, h, 28); c.fill(); c.shadowColor = 'transparent'; };
  const tap = (x, y, t0) => { const u = range(t, t0, t0 + 0.45); if (u > 0 && u < 1) { c.fillStyle = `rgba(117,72,230,${0.35 * (1 - u)})`; c.beginPath(); c.arc(x, y, 20 + u * 90, 0, 7); c.fill(); } };
  const pill = (x, y, s, bg, fg) => { c.font = '600 21px Inter'; const w = c.measureText(s).width + 32; c.fillStyle = bg; rr(c, x, y, w, 40, 20); c.fill(); text(c, s, x + 16, y + 27, '600 21px Inter', fg); };
  // 1 visitor approval
  let y = 410; card(y, 250);
  text(c, 'VISITOR AT MAIN GATE', 68, y + 52, '700 20px Inter', PURPLE);
  c.fillStyle = '#d9cff7'; c.beginPath(); c.arc(106, y + 118, 38, 0, 7); c.fill(); text(c, 'RV', 106, y + 128, '700 26px Inter', PURPLE_D, 'center');
  text(c, 'Rahul Verma', 164, y + 110, '700 30px Manrope', '#1f1b2e'); text(c, 'Guest · arrived 12:18', 164, y + 146, '500 22px Inter', '#6f6a80');
  const ap = range(t, 0.95, 1.25);
  if (ap < 1) {
    c.globalAlpha = 1 - ap;
    c.strokeStyle = '#d6d1e4'; c.lineWidth = 2; rr(c, 68, y + 178, 280, 52, 26); c.stroke(); text(c, 'Deny', 208, y + 212, '600 24px Inter', '#6f6a80', 'center');
    c.fillStyle = PURPLE; rr(c, 368, y + 178, 280, 52, 26); c.fill(); text(c, 'Approve', 508, y + 212, '600 24px Inter', '#fff', 'center');
    c.globalAlpha = 1;
  }
  if (ap > 0) { c.globalAlpha = ap; c.fillStyle = '#e7f6ec'; rr(c, 68, y + 178, 580, 52, 26); c.fill(); text(c, '✓  Approved · guard notified', 358, y + 212, '600 24px Inter', '#1e8e4a', 'center'); c.globalAlpha = 1; }
  tap(508, y + 204, 0.7);
  // 2 maintenance
  y = 690; card(y, 190);
  text(c, 'MAINTENANCE · SEPTEMBER', 68, y + 52, '700 20px Inter', PURPLE);
  text(c, '₹3,500', 68, y + 116, '800 44px Manrope', '#1f1b2e'); text(c, 'Due 5 Oct', 68, y + 154, '500 22px Inter', '#6f6a80');
  const pd = range(t, 1.95, 2.25);
  if (pd < 1) { c.globalAlpha = 1 - pd; c.fillStyle = PURPLE; rr(c, 448, y + 94, 200, 56, 28); c.fill(); text(c, 'Pay now', 548, y + 130, '600 24px Inter', '#fff', 'center'); c.globalAlpha = 1; }
  if (pd > 0) { c.globalAlpha = pd; pill(468, y + 102, '✓ Paid', '#e7f6ec', '#1e8e4a'); text(c, 'Receipt #AG-2291', 648, y + 170, '500 20px Inter', '#6f6a80', 'right'); c.globalAlpha = 1; }
  tap(548, y + 122, 1.7);
  // 3 complaint tracking
  y = 910; card(y, 200);
  text(c, 'COMPLAINT #118', 68, y + 52, '700 20px Inter', PURPLE);
  text(c, 'Lift B not working', 68, y + 104, '700 30px Manrope', '#1f1b2e');
  const steps = ['Raised', 'Assigned', 'In progress']; const prog = 1 + (t > 2.7 ? 1 : 0) + (t > 3.1 ? 0 : 0);
  steps.forEach((s, i) => {
    const x = 80 + i * 200, done = i <= prog, active = i === prog;
    c.fillStyle = done ? PURPLE : '#ddd8ea'; c.beginPath(); c.arc(x, y + 150, active ? 13 : 10, 0, 7); c.fill();
    if (i < 2) { c.fillStyle = i < prog ? PURPLE : '#ddd8ea'; c.fillRect(x + 14, y + 148, 172, 4); }
    text(c, s, x - 12, y + 186, `${active ? 600 : 500} 20px Inter`, done ? '#1f1b2e' : '#9a95ab');
  });
  // bottom nav
  c.fillStyle = '#fff'; c.fillRect(0, PH.H - 150, PH.W, 150); c.fillStyle = '#ece8f5'; c.fillRect(0, PH.H - 150, PH.W, 2);
  ['Home', 'Visitors', 'Payments', 'Complaints', 'More'].forEach((s, i) => {
    const x = 72 + i * 144; c.fillStyle = i === 0 ? PURPLE : '#b3aec2'; rr(c, x - 18, PH.H - 118, 36, 36, 10); c.fill();
    text(c, s, x, PH.H - 50, `${i === 0 ? 600 : 500} 19px Inter`, i === 0 ? PURPLE : '#8c879c', 'center');
  });
}
// simple line icons for the four modules
export function drawIcon(c, i, x, y, col = PURPLE, s = 1) {
  c.save(); c.translate(x, y); c.scale(s, s); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = 3.2; c.lineCap = 'round'; c.lineJoin = 'round';
  if (i === 0) { c.beginPath(); c.arc(0, -6, 7, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 16, 14, Math.PI * 1.1, Math.PI * 1.9); c.stroke(); }          // visitor
  if (i === 1) { c.beginPath(); c.moveTo(-12, 12); c.lineTo(-12, -4); c.lineTo(0, -14); c.lineTo(12, -4); c.lineTo(12, 12); c.closePath(); c.stroke(); c.strokeRect(-4, 2, 8, 10); } // home / maintenance
  if (i === 2) { c.beginPath(); c.moveTo(-12, -12); c.lineTo(12, -12); c.lineTo(12, 6); c.lineTo(0, 6); c.lineTo(-6, 13); c.lineTo(-6, 6); c.lineTo(-12, 6); c.closePath(); c.stroke(); c.beginPath(); c.moveTo(0, -6); c.lineTo(0, -1); c.stroke(); } // complaint
  if (i === 3) { c.strokeRect(-13, -9, 26, 18); c.beginPath(); c.moveTo(-13, -3); c.lineTo(13, -3); c.stroke(); c.fillRect(4, 3, 5, 3); } // payment card
  c.restore();
}

// ---------------- spreadsheet on the laptop, 1280 × 800
export function makeSheet() {
  const cv = document.createElement('canvas'); cv.width = 1280; cv.height = 800; const c = cv.getContext('2d');
  c.fillStyle = '#fff'; c.fillRect(0, 0, 1280, 800);
  c.fillStyle = '#217346'; c.fillRect(0, 0, 1280, 44); text(c, 'Society_Accounts_FINAL_v7 (2).xlsx', 20, 30, '600 20px Inter', '#fff');
  c.fillStyle = '#f3f3f3'; c.fillRect(0, 44, 1280, 60); text(c, 'fx   =SUM(D4:D38)-E12', 20, 82, '400 18px Inter', '#333');
  const cols = ['', 'Date', 'Head', 'Paid by', 'Amount', 'Receipt?', 'Remarks'], widths = [44, 110, 260, 220, 140, 120, 386];
  let x = 0; c.fillStyle = '#e8e8e8'; c.fillRect(0, 104, 1280, 30);
  cols.forEach((s, i) => { text(c, s || '', x + 8, 126, '600 17px Inter', '#444'); x += widths[i]; });
  const rows = [['01/09', 'Security salary', 'Bank', '84,000', 'Y', ''], ['03/09', 'Lift AMC', 'Cash', '12,500', '?', 'check with Mehta ji'], ['05/09', 'Water tanker ×6', 'UPI (Sharma)', '9,600', 'N', 'bill pending'],
    ['07/09', 'Garden', 'Cash', '4,200', 'Y', ''], ['09/09', 'Plumber B-304', '??', '1,200', 'N', 'who paid?'], ['12/09', 'Electricity common', 'Bank', '38,450', 'Y', ''],
    ['15/09', 'Diwali decor adv.', 'Cash', '15,000', 'N', 'committee approval?'], ['18/09', 'CCTV repair', 'UPI', '3,800', '?', ''], ['21/09', 'Tanker', 'Cash', '1,600', 'N', 'duplicate?'],
    ['24/09', 'Lift B repair', '—', '#REF!', '', 'ERROR'], ['', '', '', '', '', ''], ['', 'TOTAL', '', '#VALUE!', '', 'doesn\'t match bank']];
  rows.forEach((r, j) => {
    const y = 134 + j * 44; c.strokeStyle = '#ddd'; c.lineWidth = 1; c.beginPath(); c.moveTo(0, y + 44); c.lineTo(1280, y + 44); c.stroke();
    text(c, String(j + 4), 12, y + 29, '400 16px Inter', '#888'); let xx = 44;
    r.forEach((s, i) => { const bad = s.startsWith('#') || s === '?' || s === 'N' || s === 'ERROR'; if (bad && s) { c.fillStyle = '#ffe3e0'; c.fillRect(xx, y, widths[i + 1], 44); } text(c, s, xx + 8, y + 29, '400 18px Inter', bad ? '#c62828' : '#222'); xx += widths[i + 1]; });
  });
  x = 0; for (const w of widths) { x += w; c.strokeStyle = '#ddd'; c.beginPath(); c.moveTo(x, 104); c.lineTo(x, 800); c.stroke(); }
  return cv;
}
