# SUOMII

Website for SUOMII bespoke Finnish saunas. Live at https://suomii.vercel.app

`index.html` is the whole page — a single self-contained file. Every photo is
embedded as base64, so it runs without a build step or network.
The enquiry form posts to a small serverless function in `api/`.

## Layout

| Path                        | What it is                                    |
| --------------------------- | --------------------------------------------- |
| `index.html`                | The built site. **Generated — do not edit.**  |
| `src/suomii.template.html`  | The real source. Edit this.                   |
| `src/build.py`              | Escapes the text, embeds the photos, writes `index.html`. |
| `src/encode.py`             | Resizes and base64-encodes the photos (run by `build.py` when needed). |
| `api/inquiry.js`            | Vercel function: receives the form, emails it via Resend. |
| `CABIN DESIGNS/`            | Source photo library. Local only, git-ignored. |

## Rebuilding

```bash
python3 src/build.py
```

Needs the photo library present locally. Pushing to `main` deploys to Vercel.

## Enquiry form

The form sends name, email, phone, location, message and the chosen
design × type to `POST /api/inquiry`, which emails it through
[Resend](https://resend.com). Set these in Vercel → Project → Settings →
Environment Variables:

| Variable         | Needed   | Value                                              |
| ---------------- | -------- | -------------------------------------------------- |
| `RESEND_API_KEY` | yes      | API key from Resend                                |
| `INQUIRY_TO`     | no       | Recipients, comma-separated. Default `agnes.kozenkow@suomii.com` |
| `INQUIRY_FROM`   | no       | Sender. Default `SUOMII <onboarding@resend.dev>`   |

Until `RESEND_API_KEY` is set, the endpoint answers 503 and the page opens the
visitor's mail app with everything pre-filled, so no enquiry is lost.
Resend's test sender only delivers to the Resend account's own address — to send
to `suomii.com` addresses, verify the `suomii.com` domain in Resend.

## Why the build step

1. **Encoding.** Every non-ASCII character is escaped, so accented Slovak,
   Czech and Hungarian render correctly even if a browser ignores the charset.
2. **Photos.** They are resized, re-compressed and inlined as base64.

## Still to do

- Native-speaker check of the Slovak, Czech and Hungarian copy.
- Descriptions for the five saunas: fill in the `DESC` object in
  `src/suomii.template.html`; an empty string shows a "coming soon" line.
