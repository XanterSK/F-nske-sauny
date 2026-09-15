// Vercel serverless function: POST /api/inquiry
// Receives the enquiry form and emails it to SUOMII through Resend (https://resend.com).
//
// Environment variables (Vercel -> Project -> Settings -> Environment Variables):
//   RESEND_API_KEY  required. Without it the endpoint answers 503 and the page
//                   falls back to opening the visitor's mail app, pre-filled.
//   INQUIRY_TO      optional, comma-separated. Default: agnes.kozenkow@suomii.com
//   INQUIRY_FROM    optional. Default: "SUOMII <onboarding@resend.dev>".
//                   Resend's test sender only delivers to the Resend account's own
//                   address; verify suomii.com in Resend to send anywhere.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// single-line fields: trimmed, capped, no line breaks (keeps the subject header clean)
const line = (v, max) => String(v == null ? '' : v).replace(/[\r\n]+/g, ' ').trim().slice(0, max);
const block = (v, max) => String(v == null ? '' : v).trim().slice(0, max);
const esc = (v) => v.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'method_not_allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ error: 'bad_json' }); }
  }
  body = body || {};

  // honeypot filled in: pretend success so bots learn nothing
  if (body.company) return res.status(200).json({ ok: true });

  const d = {
    name: line(body.name, 120),
    email: line(body.email, 160),
    phone: line(body.phone, 40),
    place: line(body.place, 160),
    message: block(body.message, 4000),
    design: line(body.design, 40),
    type: line(body.type, 80),
    lang: line(body.lang, 5),
  };

  if (!d.name || !EMAIL_RE.test(d.email) || body.consent !== true) {
    return res.status(422).json({ error: 'invalid' });
  }

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(503).json({ error: 'not_configured' });

  const rows = [
    ['Design', d.design],
    ['Type', d.type],
    ['Name', d.name],
    ['Email', d.email],
    ['Phone', d.phone],
    ['Location', d.place],
    ['Language', d.lang.toUpperCase()],
  ].filter(([, v]) => v);

  const html =
    '<table style="font-family:Arial,sans-serif;font-size:15px;border-collapse:collapse">' +
    rows.map(([k, v]) =>
      `<tr><td style="padding:6px 18px 6px 0;color:#864c2c">${k}</td><td style="padding:6px 0">${esc(v)}</td></tr>`
    ).join('') +
    '</table>' +
    (d.message ? `<p style="font-family:Arial,sans-serif;font-size:15px;white-space:pre-wrap">${esc(d.message)}</p>` : '');

  const text = rows.map(([k, v]) => `${k}: ${v}`).join('\n') + (d.message ? `\n\n${d.message}` : '');

  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: process.env.INQUIRY_FROM || 'SUOMII <onboarding@resend.dev>',
      to: (process.env.INQUIRY_TO || 'agnes.kozenkow@suomii.com').split(',').map((x) => x.trim()).filter(Boolean),
      reply_to: d.email,
      subject: `SUOMII - ${d.design} / ${d.type} - ${d.name}`,
      html,
      text,
    }),
  });

  if (!r.ok) {
    console.error('resend failed', r.status, await r.text());
    return res.status(502).json({ error: 'send_failed' });
  }
  return res.status(200).json({ ok: true });
};
