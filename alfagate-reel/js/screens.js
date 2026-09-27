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

// ---------------- AlfaGate app: recreation of the real Home screen (layout, colours, modules taken from the supplied
// screenshots). Drawn in the screenshot's own 272 × 592 pt space and scaled up. Resident data is fictional.
export const APP = { primary: '#8f5cff', primaryD: '#7a45f5', light: '#efe9ff', ink: '#14131a', grey: '#6b6f7b', bg: '#f5f7fa', red: '#ef4444' };
export function drawApp(c, t, icon) {
  // t: seconds since the app shot started
  const S = PH.W / 272;
  c.save(); c.scale(S, S);
  c.fillStyle = APP.bg; c.fillRect(0, 0, 272, 592);
  // status bar + Dynamic Island
  text(c, '12:19', 34, 22, '600 10.5px Inter', APP.ink);
  c.fillStyle = '#000'; rr(c, 94, 9, 84, 24, 12); c.fill();
  c.fillStyle = APP.ink; for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(222, 21, 1.6 + i * 2.2, Math.PI * 1.25, Math.PI * 1.75); c.lineWidth = 1.4; c.strokeStyle = APP.ink; c.stroke(); }
  rr(c, 234, 14, 20, 10, 3); c.lineWidth = 1; c.stroke(); c.fillRect(236, 16, 15, 6);
  // top buttons
  const sq = (x) => { c.fillStyle = '#fff'; c.strokeStyle = '#e6e8ee'; c.lineWidth = 1; rr(c, x, 50, 26, 26, 8); c.fill(); c.stroke(); };
  sq(11); c.fillStyle = APP.ink; for (let i = 0; i < 3; i++) c.fillRect(18, 58 + i * 4.5, 12, 1.5);
  sq(236); c.fillStyle = APP.ink; c.beginPath(); c.moveTo(243, 69); c.quadraticCurveTo(243, 57, 249, 57); c.quadraticCurveTo(255, 57, 255, 69); c.closePath(); c.fill(); c.fillRect(247.5, 69.5, 3, 2);
  const badge = t > 1.05 ? '2' : '3';
  c.fillStyle = APP.red; c.beginPath(); c.arc(257, 53, 6, 0, 7); c.fill(); text(c, badge, 257, 56, '700 7.5px Inter', '#fff', 'center');
  // greeting
  text(c, 'Good Afternoon', 11, 94, '500 9.5px Inter', APP.grey);
  text(c, 'Aarav Kapoor', 11, 115, '700 16px Inter', APP.ink);
  text(c, 'Unit A-1204  -  Primary', 11, 131, '500 8.5px Inter', APP.grey);
  c.fillStyle = APP.primary; c.beginPath(); c.arc(14, 142, 3.2, Math.PI, 0); c.lineTo(14, 148); c.closePath(); c.fill(); c.fillStyle = '#fff'; c.beginPath(); c.arc(14, 142, 1.2, 0, 7); c.fill();
  text(c, 'Green Valley Residency', 21, 146, '600 8.5px Inter', APP.primary);
  // illustration (building + trees) in light purple, as on the real screen
  c.fillStyle = '#e8e0ff'; rr(c, 200, 134, 60, 8, 3); c.fill();
  c.fillStyle = '#f3efff'; c.strokeStyle = '#d6c9ff'; c.lineWidth = 1.2; rr(c, 214, 92, 32, 44, 2); c.fill(); c.stroke();
  c.fillStyle = '#ddd2ff'; for (const x of [206, 252]) { c.beginPath(); c.moveTo(x, 122); c.lineTo(x - 5, 134); c.lineTo(x + 5, 134); c.closePath(); c.fill(); c.fillRect(x - 0.6, 134, 1.2, 3); }
  // maintenance card
  const card = (x, y, w, h, r = 14) => { c.fillStyle = '#fff'; c.shadowColor = 'rgba(20,20,60,0.06)'; c.shadowBlur = 8; c.shadowOffsetY = 2; rr(c, x, y, w, h, r); c.fill(); c.shadowColor = 'transparent'; };
  card(11, 172, 250, 74);
  c.fillStyle = APP.light; c.beginPath(); c.arc(40, 209, 17, 0, 7); c.fill();
  c.fillStyle = APP.primary; rr(c, 32, 202, 16, 13, 3); c.fill(); c.fillStyle = '#fff'; rr(c, 42, 206, 8, 5, 2); c.fill();
  text(c, 'Maintenance Due', 66, 190, '500 8.5px Inter', APP.grey);
  const paid = range(t, 2.05, 2.3);
  text(c, '₹3,500', 66, 216, '800 20px Manrope', APP.primary);
  text(c, 'Due Date: 15 Oct 2026', 66, 232, '500 7.5px Inter', APP.grey);
  const btn = c.createLinearGradient(176, 0, 250, 0); btn.addColorStop(0, '#9d6bff'); btn.addColorStop(1, APP.primaryD);
  const press = range(t, 1.75, 1.85) * (1 - range(t, 1.85, 2.0));
  c.save(); c.translate(213, 207); c.scale(1 - press * 0.05, 1 - press * 0.05); c.translate(-213, -207);
  c.fillStyle = btn; rr(c, 176, 194, 74, 26, 9); c.fill();
  text(c, 'Pay Now  ›', 213, 210.5, '600 9px Inter', '#fff', 'center');
  c.restore();
  // pending visitor requests (horizontal cards)
  text(c, 'Pending Visitor Requests', 11, 265, '700 11px Inter', APP.ink);
  text(c, 'View All', 261, 265, '600 9px Inter', APP.primary, 'right');
  const reqs = [['Rahul Verma', 'Gate 1', 'just now', 'guest'], ['Amazon Deli...', 'Gate 1', '2 min ago', 'deliv'], ['Courier Per...', 'Gate 1', '15 min ago', 'truck'], ['Blinkit Deli...', 'Gate 2', '45 min ago', 'deliv']];
  const gone = easeOut(range(t, 1.0, 1.35)), shift = easeOut(range(t, 1.25, 1.65)) * 110;
  reqs.forEach(([n, g, tm, kind], i) => {
    let x = 11 + i * 110 - (i > 0 ? shift : 0);
    if (i === 0) { if (gone >= 1) return; c.globalAlpha = 1 - gone; x -= gone * 20; }
    card(x, 277, 100, 72, 12);
    const ic = kind === 'truck' ? ['#fff1e0', '#f59e0b'] : kind === 'guest' ? ['#fde7f0', '#ec4899'] : [APP.light, APP.primary];
    c.fillStyle = ic[0]; c.beginPath(); c.arc(x + 23, 297, 12, 0, 7); c.fill();
    drawIcon(c, kind === 'guest' ? 6 : kind === 'truck' ? 8 : 7, x + 23, 297, ic[1], 0.42);
    text(c, n, x + 39, 294, '700 8.5px Inter', APP.ink); text(c, g, x + 39, 305, '500 7px Inter', APP.grey);
    text(c, tm, x + 8, 321, '500 7px Inter', APP.grey);
    c.lineWidth = 0.8; c.strokeStyle = '#c9b6ff'; rr(c, x + 8, 327, 41, 15, 5); c.stroke(); text(c, '◎ Approve', x + 28.5, 337.5, '600 6.5px Inter', APP.primary, 'center');
    c.strokeStyle = '#f5b3b3'; rr(c, x + 53, 327, 39, 15, 5); c.stroke(); text(c, '⊗ Reject', x + 72.5, 337.5, '600 6.5px Inter', APP.red, 'center');
    c.globalAlpha = 1;
  });
  // quick actions
  card(11, 388, 250, 138);
  text(c, 'Quick Actions', 23, 411, '700 11px Inter', APP.ink);
  [['Visitors', '#ece6ff', APP.primary, 0], ['Complaints', '#fff3d6', '#f59e0b', 2], ['Notices', '#ece6ff', APP.primary, 3], ['Emergency', '#fde2e2', APP.red, 4]].forEach(([l, bg, fg, ic], i) => {
    const x = 47 + i * 59;
    c.fillStyle = bg; rr(c, x - 17, 458, 34, 34, 10); c.fill();
    drawIcon(c, ic, x, 475, fg, 0.55);
    text(c, l, x, 505, '500 8px Inter', APP.ink, 'center');
  });
  // bottom navigation
  c.fillStyle = '#fff'; c.fillRect(0, 526, 272, 66); c.fillStyle = '#eceef2'; c.fillRect(0, 526, 272, 0.8);
  [['Home', 5, 33], ['Visitors', 0, 102], ['Complaints', 2, 169], ['Profile', 6, 237]].forEach(([l, ic, x], i) => {
    if (i === 0) { c.fillStyle = APP.light; rr(c, x - 17, 531, 34, 19, 9.5); c.fill(); }
    drawIcon(c, ic, x, 541, i === 0 ? APP.primary : '#8e929c', 0.42);
    text(c, l, x, 562, `${i === 0 ? 600 : 500} 7.5px Inter`, i === 0 ? APP.primary : '#8e929c', 'center');
  });
  // taps: Approve on the guest, Pay Now, then the Complaints quick action; payment confirmation toast
  const tap = (x, y, t0) => { const u = range(t, t0, t0 + 0.45); if (u > 0 && u < 1) { c.fillStyle = `rgba(143,92,255,${0.35 * (1 - u)})`; c.beginPath(); c.arc(x, y, 6 + u * 30, 0, 7); c.fill(); } };
  tap(39, 334, 0.7); tap(213, 207, 1.75); tap(106, 475, 2.95);
  if (paid > 0) {
    const k = paid * (1 - range(t, 3.3, 3.6)), y = 40 + (1 - easeOut(paid)) * -30;
    c.globalAlpha = k; card(40, y, 192, 30, 15);
    c.fillStyle = '#22c55e'; c.beginPath(); c.arc(56, y + 15, 7, 0, 7); c.fill();
    c.strokeStyle = '#fff'; c.lineWidth = 1.6; c.beginPath(); c.moveTo(52.5, y + 15); c.lineTo(55.5, y + 18); c.lineTo(60, y + 12); c.stroke();
    text(c, 'Maintenance paid · ₹3,500', 70, y + 18.5, '600 8.5px Inter', APP.ink); c.globalAlpha = 1;
  }
  c.restore();
}
// line icons: 0 visitors, 1 wallet, 2 complaint (warning), 3 notices (megaphone), 4 emergency (shield), 5 home, 6 person, 7 scooter, 8 truck
export function drawIcon(c, i, x, y, col = PURPLE, s = 1) {
  c.save(); c.translate(x, y); c.scale(s, s); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = 3.2; c.lineCap = 'round'; c.lineJoin = 'round';
  const circ = (cx, cy, r) => { c.beginPath(); c.arc(cx, cy, r, 0, 7); c.fill(); };
  if (i === 0) { circ(0, -8, 6); circ(-12, -5, 4.5); circ(12, -5, 4.5); c.beginPath(); c.ellipse(0, 10, 12, 7, 0, Math.PI, 0); c.fill(); c.beginPath(); c.ellipse(-14, 9, 7, 5, 0, Math.PI, 0); c.fill(); c.beginPath(); c.ellipse(14, 9, 7, 5, 0, Math.PI, 0); c.fill(); }
  if (i === 1) { c.beginPath(); c.roundRect(-14, -10, 28, 21, 4); c.fill(); c.fillStyle = '#fff'; c.beginPath(); c.roundRect(3, -3, 13, 8, 3); c.fill(); }
  if (i === 2) { c.beginPath(); c.moveTo(0, -15); c.lineTo(15, 12); c.lineTo(-15, 12); c.closePath(); c.fill(); c.fillStyle = '#fff'; c.fillRect(-1.6, -5, 3.2, 9); circ(0, 8, 2); }
  if (i === 3) { c.beginPath(); c.moveTo(-12, -4); c.lineTo(4, -12); c.lineTo(4, 12); c.lineTo(-12, 4); c.closePath(); c.fill(); c.fillRect(-15, -4, 4, 8); c.lineWidth = 2.6; c.beginPath(); c.arc(6, 0, 9, -0.7, 0.7); c.stroke(); c.fillRect(-10, 4, 4, 9); }
  if (i === 4) { c.beginPath(); c.moveTo(0, -15); c.lineTo(13, -9); c.quadraticCurveTo(13, 8, 0, 15); c.quadraticCurveTo(-13, 8, -13, -9); c.closePath(); c.fill(); c.fillStyle = '#fff'; c.fillRect(-1.8, -7, 3.6, 12); c.fillRect(-6, -3, 12, 3.6); }
  if (i === 5) { c.beginPath(); c.moveTo(-13, -1); c.lineTo(0, -13); c.lineTo(13, -1); c.lineTo(10, -1); c.lineTo(10, 12); c.lineTo(-10, 12); c.lineTo(-10, -1); c.closePath(); c.fill(); c.fillStyle = '#fff'; c.fillRect(-3, 4, 6, 8); }
  if (i === 6) { circ(0, -6, 7); c.beginPath(); c.ellipse(0, 12, 12, 8, 0, Math.PI, 0); c.fill(); }
  if (i === 7) { c.lineWidth = 3; c.beginPath(); c.arc(-9, 8, 4.5, 0, 7); c.stroke(); c.beginPath(); c.arc(10, 8, 4.5, 0, 7); c.stroke(); c.beginPath(); c.moveTo(-9, 8); c.lineTo(-2, 0); c.lineTo(8, 0); c.lineTo(10, 8); c.stroke(); c.fillRect(-14, -8, 10, 8); c.beginPath(); c.moveTo(6, -8); c.lineTo(8, 0); c.stroke(); }
  if (i === 8) { c.fillRect(-15, -8, 18, 14); c.beginPath(); c.moveTo(4, -3); c.lineTo(11, -3); c.lineTo(15, 2); c.lineTo(15, 6); c.lineTo(4, 6); c.closePath(); c.fill(); c.fillStyle = '#fff'; circ(-9, 8, 3.5); circ(9, 8, 3.5); c.fillStyle = col; circ(-9, 8, 2); circ(9, 8, 2); }
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
