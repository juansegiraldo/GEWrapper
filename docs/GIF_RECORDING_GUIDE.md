# GIF Recording Guide

This guide shows how to record short, focused GIFs for the docs.

## What to record
- hero.gif — 10–15s app overview (upload → configure → run → results)
- upload.gif — Upload and profiling (5–8s)
- configure.gif — Configure expectations and add one SQL validation (8–12s)
- validate.gif — Start validation and show progress (6–10s)
- results.gif — Results overview and export (8–12s)

## Windows (PowerShell) – free tools
1) Install ShareX: `https://getsharex.com/`
2) Run ShareX → Capture → Screen recording (GIF)
3) Set region and FPS 8–12, start/stop with hotkey
4) Save to `docs/assets/`

## Recording tips
- Keep under 10–15 seconds each
- 720px width is a good balance for size/clarity
- Lower FPS (8–12) keeps files small
- Avoid moving background windows; zoom if needed

## Optimize GIF size
- Use Ezgif (`https://ezgif.com/`) to resize/optimize
- Reduce colors to 64–128 if necessary
- Trim the start/end frames

## File placement and references
- Put files in `docs/assets/`
- Refer in docs using relative paths, for example:
```markdown
![Upload and profiling](assets/upload.gif)
```

Done! Commit GIFs along with doc edits.
