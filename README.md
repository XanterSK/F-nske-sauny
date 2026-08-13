# SUOMII

Website for SUOMII bespoke Finnish saunas.

`index.html` is the whole site — a single self-contained file. Every photo is
embedded as base64, so it needs no server, no build step and no network to run.
Open it by double-clicking, or let Vercel serve it as-is.

## Layout

| Path                        | What it is                                    |
| --------------------------- | --------------------------------------------- |
| `index.html`                | The built site. **Generated — do not edit.**  |
| `src/suomii.template.html`  | The real source. Edit this.                   |
| `src/build.py`              | Escapes the text, embeds the photos, writes `index.html`. |
| `CABIN DESIGNS/`            | Source photo library. Local only, git-ignored. |

## Rebuilding

```bash
python3 src/build.py
```

The photo library must be present locally, and the base64 cache
(`/tmp/sauna_build/images.json`) must exist. If it doesn't, re-run the encoder
step that produces it before building.

## Why the build step

Two problems it solves:

1. **Encoding.** Every non-ASCII character is escaped — `Slovenčina` becomes
   `Sloven&#269;ina` in markup, `Ručne` becomes `Ručne` in JavaScript. The
   file is pure ASCII, so accented Slovak, Czech and Hungarian render correctly
   even if a browser ignores the charset entirely.
2. **Photos.** They are resized, re-compressed and inlined as base64, so the
   single file stays self-contained.

## Still to do

- Real copy for Slovak, Czech and Hungarian — the current strings are unverified.
- Descriptions for the five saunas. Fill in the `DESC` object at the top of the
  script in `src/suomii.template.html`; an empty string shows a "coming soon" line.
- Replace the placeholder contact address `info@suomii.com`.
