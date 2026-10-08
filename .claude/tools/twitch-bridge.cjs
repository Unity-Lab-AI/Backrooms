// twitch-bridge.cjs — Twitch chat -> Unity Plays RimWorld inbox.
//
//   node .claude/tools/twitch-bridge.cjs <channel>        (or TWITCH_CHANNEL in .claude/.env)
//
// Reads the channel's chat anonymously over Twitch IRC (no token needed to read) and posts each
// chat line to the studio's /api/say as "<user>: <message>", so the studio-watch -> studio-pump
// loop answers viewers exactly like messages typed into the window.
const net = require('net');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ENV = path.join(__dirname, '..', '.env');
function env() {
  const o = {};
  try { for (const l of fs.readFileSync(ENV, 'utf8').split(/\r?\n/)) { const m = l.match(/^\s*([A-Z_]+)\s*=\s*(.*)$/); if (m) o[m[1]] = m[2].trim(); } } catch (e) {}
  return o;
}
const channel = (process.argv[2] || env().TWITCH_CHANNEL || '').replace(/^#/, '').toLowerCase();
if (!channel) { console.error('usage: node twitch-bridge.cjs <channel>  (or TWITCH_CHANNEL in .claude/.env)'); process.exit(1); }
const STUDIO = process.env.STUDIO_URL || 'http://127.0.0.1:4317';

function say(text) {
  const data = JSON.stringify({ text: text, persona: 'unity' });
  const u = new URL(STUDIO + '/api/say');
  const r = http.request({ hostname: u.hostname, port: u.port, path: u.pathname, method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } });
  r.on('error', (e) => console.error('studio:', e.message));
  r.end(data);
}

function connect() {
  const s = net.connect(6667, 'irc.chat.twitch.tv');
  let buf = '';
  s.on('connect', () => {
    s.write('CAP REQ :twitch.tv/tags\r\n');
    s.write('NICK justinfan' + Math.floor(10000 + Math.random() * 80000) + '\r\n');
    s.write('JOIN #' + channel + '\r\n');
    console.log('twitch-bridge: reading #' + channel);
  });
  s.on('data', (d) => {
    buf += d.toString('utf8');
    let i;
    while ((i = buf.indexOf('\r\n')) >= 0) {
      const line = buf.slice(0, i); buf = buf.slice(i + 2);
      if (line.startsWith('PING')) { s.write('PONG :tmi.twitch.tv\r\n'); continue; }
      const m = line.match(/(?:display-name=([^;]*);.*)?:(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)$/);
      if (m) {
        const who = m[1] || m[2];
        const text = m[3].trim();
        if (text) { console.log(who + ': ' + text); say('[twitch] ' + who + ': ' + text); }
      }
    }
  });
  s.on('close', () => { console.log('twitch-bridge: disconnected, retrying in 5s'); setTimeout(connect, 5000); });
  s.on('error', (e) => console.error('twitch-bridge:', e.message));
}
connect();
