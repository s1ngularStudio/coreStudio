# Lab

A running, public showcase of the exercises and art pieces built in this repo — separate
from the Framer site (`s1ngular.com.br`, the studio's main public face) and from
`03-transmissions/web-assets/` (raw media hotlinked into Framer via CDN). This is a real
coded site, deployed straight from GitHub.

## Site structure

- `/` — landing page (Twitch embed, live or Twitch's own offline card automatically)
- `/work` — every piece, newest first
- `/work/<slug>` — one piece's detail page
- `/about`, `/contact`, `/lab`, `/search` — the rest of the nav (thin for now)

## Adding a new piece

Drop a new Markdown file into `src/content/pieces/`, e.g. `my-new-thing.md`:

```markdown
---
title: My New Thing
date: 2026-09-10
tags: [py5, generative]
builtWith: [py5, python-chess]     # optional, shown as "Built with" on the detail page
summary: One or two sentences, shown on the Work list.
link: https://example.com          # optional, an external "View it" link
media: /work/my-new-thing/hero.mp4 # optional, the thumbnail/hero -- see below
gallery:                           # optional, extra images/videos, detail page only
  - /work/my-new-thing/shot-2.png
  - /work/my-new-thing/clip.mp4
---

The full write-up goes here — shown on the piece's own detail page (not the Work list). No
length limit; write as much as you want.
```

The detail page (`src/pages/work/[id].astro`) renders everything automatically: title,
tags, media, the write-up, gallery, "Built with", and a link to the next piece. Nothing
else needs to change for a new entry.

**Adding media/gallery images:** put the actual image/video files under
`public/work/<slug>/`, then point `media` (and any `gallery` entries) at those public paths
(e.g. `/work/my-new-thing/hero.mp4`). The detail page picks `<img>` or `<video>`
automatically from each file's extension. `media` is also what shows as the thumbnail
everywhere the piece is listed (Work grid, landing page); `gallery` images only appear on
the piece's own detail page.

## Local development

```bash
npm install   # first time only
npm run dev   # http://localhost:4321
npm run build # production build, output in dist/
```

## Visual system

Colors and fonts in `src/styles/global.css` come from the **S1NGULAR Studio Visual Spec**
(the Claude Design canvas) — keep them in sync with that spec rather than inventing new
tokens here.

## Deploying (Netlify or Vercel)

This is a subproject inside a larger monorepo, so the one setting that matters when
connecting the repo:

- **Base directory / Root directory:** `03-transmissions/lab`
- Everything else (build command `npm run build`, output directory `dist`) is auto-detected
  for Astro on both platforms — no extra config needed.

Once connected, every push to the repo's default branch redeploys automatically.

**Deploying specifically to Netlify:** `netlify.toml` already sets the base directory and
functions folder, so connecting the repo just works without touching the dashboard's build
settings.

## Content management (Decap CMS)

`/admin` on the deployed site is a real content-editing UI — add/edit pieces through forms
instead of writing Markdown by hand. It commits straight to this GitHub repo (a real git
commit, triggering a real redeploy), so nothing about "where the content lives" changes —
this is a friendlier way to write to the same `src/content/pieces/` files, not a separate
database.

**One-time setup, on Netlify (three things only you can do):**

1. **Create a GitHub OAuth App** — on GitHub: Settings → Developer settings → OAuth Apps →
   New OAuth App. Fill in:
   - **Application name:** anything, e.g. "S1NGULAR Lab CMS"
   - **Homepage URL:** your deployed site's URL (e.g. `https://your-site.netlify.app`)
   - **Authorization callback URL:** the SAME URL + `/.netlify/functions/auth`
     (e.g. `https://your-site.netlify.app/.netlify/functions/auth`)

   GitHub gives you a **Client ID** immediately, and lets you generate a **Client Secret**
   once — copy both.

2. **Set two environment variables on the Netlify site** (Site settings → Environment
   variables): `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`, the two values from step 1.
   Never commit these to the repo.

3. **Update `public/admin/config.yml`'s `base_url`** to your real deployed URL (it currently
   says `https://YOUR-DEPLOYED-SITE.netlify.app` as a placeholder) and push that change.

## Pending

- [ ] Commit and push everything built 2026-09-05 (the whole Lab project, the CMS setup,
  `03-transmissions/under-construction/`) — none of it is on GitHub yet as of this writing.
- [ ] Install the GitHub Mobile app on the iPad specifically (not just the iPhone) — GitHub's
  2FA push notification only reaches whichever device actually has the app installed and
  signed in, so it currently has nowhere to go when working from the iPad. Until then, use
  "Send a code via email" on GitHub's confirm-access screen as the workaround.
- [ ] Netlify account registration + connecting the repo (both the Lab project and the
  separate `under-construction` site).
- [ ] Register the GitHub OAuth App and set the two env vars (see steps above) once a real
  deployed URL exists.

After that, visiting `/admin` on the live site lets you log in with GitHub and start
editing. If you ever move hosting off Netlify, the one piece that needs redoing is
`netlify/functions/auth.js` (a ~70-line file) in whatever function format the new host
uses — everything else (the CMS config, the content itself, the rest of the site) is
unaffected.
