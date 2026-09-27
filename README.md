# SUOMII

Website for SUOMII bespoke Finnish saunas. Live at https://suomii.vercel.app

`index.html` is the whole page — one file, no framework. Photos are separate
files in `img/`, served at two widths each so phones download the small one.
The enquiry form posts to a small serverless function in `api/`.

## Layout

| Path                        | What it is                                    |
| --------------------------- | --------------------------------------------- |
| `index.html`                | The built site. **Generated — do not edit.**  |
| `src/suomii.template.html`  | The real source. Edit this.                   |
| `src/build.py`              | Escapes the text, wraps the document, injects the photo paths. |
| `src/images.py`             | Resizes the photo library into `img/` and writes `img/manifest.json`. |
| `src/brand/`                | The logo, traced from the 2015 brand manual.  |
| `api/inquiry.js`            | Vercel function: receives the form, emails it via Resend. |
| `img/`                      | Generated photos + manifest. Committed.       |
| `CABIN DESIGNS/`            | Source photo library. Local only, git-ignored. |

## Rebuilding

```bash
python3 src/build.py          # normal case
python3 src/images.py         # only when the photo selection changes
```

`images.py` needs the photo library and macOS `sips`; `build.py` needs only the
committed `img/manifest.json`. Pushing to `main` deploys to Vercel.

## Brand

From the 2015 brand manual:

- **Logo** — white characters, always inside the blue rectangle or a white
  stroked frame (1 pt minimum). Never re-set as type, never recoloured, never
  stretched or placed in another shape. The vector lives in the template as one
  `<defs>` path (`#wm`) and is reused by every instance; `src/brand/` holds the
  same artwork as standalone SVG. Everything on this page sits on navy or on a
  photograph, so it uses the framed white version; `.logo--blue` is the primary
  lockup, kept for light backgrounds.
- **SUOMI blue** `#185594` (Pantone 7686C) — the `--blue` token.
- **Typeface** — Trebuchet MS, with Lucida Grande / Tahoma as fallbacks for
  devices that lack it (mainly Android).

## Languages

English, German, Slovak, Czech and Hungarian. All copy lives in the `T` object
at the top of the `<script>`; every key must exist in all five. The page
remembers the choice in `localStorage`.

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

1. **Encoding.** Every non-ASCII character is escaped, so accented German,
   Slovak, Czech and Hungarian render correctly even if a browser ignores the
   charset.
2. **Document wrapper.** Doctype, charset and the viewport meta — without the
   last one a phone lays the page out at ~980px and shrinks it.
3. **Photos.** Paths and `srcset` are injected from `img/manifest.json`.

## Still to do

- Native-speaker check of the German, Slovak, Czech and Hungarian copy.
- Descriptions for the five saunas: fill in the `DESC` object in
  `src/suomii.template.html`; an empty string shows a "coming soon" line.
- A photo of Kornel Szabo — the team section falls back to initials.
