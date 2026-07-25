# Web Assets

Public-facing media hosted via GitHub CDN for **s1ngular.com.br** landing page.

---

## Structure

```
web-assets/
  ├─ carousel/        Art pieces for offline carousel/slideshow
  ├─ hero/            Hero images (desktop/mobile)
  └─ icons/           Logos, icons, SVGs
```

---

## Usage in Framer

### Step 1: Upload Assets
1. Add optimized files to the appropriate folder
2. Commit and push to GitHub

### Step 2: Get Raw URLs
Navigate to the file on GitHub → Click **"Raw"** button → Copy URL

**Format:**
```
https://raw.githubusercontent.com/USERNAME/REPO/main/03-transmissions/web-assets/carousel/FILE.png
```

### Step 3: Use in Framer
- **Image component**: Paste raw URL as image source
- **Video component**: Paste MP4 raw URL
- **Custom code**: Reference in `<img src="">` or `<video src="">`

---

## Optimization Guidelines

### Images (PNG/JPG)
- **Target size**: < 500KB per image
- **Tools**: ImageOptim, Squoosh.app, TinyPNG
- **Desktop hero**: 1920×1080 max
- **Mobile hero**: 1080×1920 max
- **Carousel pieces**: 1920×1080 or 16:9 aspect ratio

### Video (MP4)
- **Target size**: < 10MB (GitHub limit: 50MB)
- **Codec**: H.264
- **Resolution**: 1920×1080 max
- **Tool**: HandBrake or ffmpeg

**ffmpeg command:**
```bash
ffmpeg -i input.mp4 -vcodec h264 -crf 28 -preset slow output.mp4
```

### SVG Icons
- Optimize with SVGO or SVGOMG
- Remove unnecessary metadata
- Keep viewBox for proper scaling

---

## Naming Conventions

Use descriptive, theory-aligned names:

✅ **Good:**
- `carousel-presemantic-area-v3.png`
- `hero-cielab-deconstruction-desktop.png`
- `demo-reel-substrate-explorations.mp4`

❌ **Avoid:**
- `IMG_1234.png`
- `final-final-v2-ACTUAL.png`
- `untitled.mp4`

---

## Examples

### Carousel Image
```html
<!-- In Framer Embed component -->
<img 
  src="https://raw.githubusercontent.com/USERNAME/REPO/main/03-transmissions/web-assets/carousel/piece-01.png"
  alt="Presemantic Area Exploration"
  style="width: 100%; border-radius: 12px;"
/>
```

### Demo Reel Video
```html
<!-- In Framer Embed component -->
<video 
  src="https://raw.githubusercontent.com/USERNAME/REPO/main/03-transmissions/web-assets/carousel/demo-reel.mp4"
  autoplay
  loop
  muted
  style="width: 100%; border-radius: 12px;"
>
</video>
```

---

## Theory Alignment

This folder lives in **03-transmissions/** because these assets are public-facing outputs — literal transmissions of the studio's work to the world. They bridge the digital substrate (code, theory) with physical perception.

See `00-substrate/self-substrate-currents.md` for conceptual foundation.

---

## Git LFS (Optional)

If you need to host files > 50MB, enable Git Large File Storage:

```bash
# Install LFS
brew install git-lfs
git lfs install

# Track large files
git lfs track "03-transmissions/web-assets/**/*.mp4"

# Commit .gitattributes
git add .gitattributes
git commit -m "Track large video files with LFS"
```

**Note:** GitHub free tier includes 1GB LFS storage + 1GB/month bandwidth.

---

## Quick Reference

| Asset Type | Location | Max Size | Format |
|------------|----------|----------|--------|
| Carousel images | `carousel/` | 500KB | PNG/JPG |
| Hero images | `hero/` | 500KB | PNG/JPG |
| Demo reel | `carousel/` | 10MB | MP4 |
| Icons/logos | `icons/` | 50KB | SVG/PNG |

---

For integration details, see `_workStuff/_framer_landingPage/docs/STREAM_INTEGRATION.md`
