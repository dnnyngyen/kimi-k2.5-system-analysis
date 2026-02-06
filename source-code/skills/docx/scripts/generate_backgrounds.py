#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
Background Example - DO NOT COPY, create your own design.

Learn: HTML/CSS techniques (radial-gradient, positioning, transparency), Playwright workflow.
Do NOT copy: colors, layout, this specific aesthetic.

Design Directions (pick one, then create original):

  Universal:
    Swiss Grid / Minimalist / Double Border / Clean Whitespace
    Soft Blocks / Gradient Ribbons / Frosted Glass / Subtle Grid
    Watercolor Wash / Ink Wash / Line Art / Grain Texture

  Expressive (match scenario well = stunning; mismatch = distracting):
    Bauhaus Geometric / Memphis / Art Deco / Monochrome Bold

Technical: 794×1123px, device_scale_factor=2, center clear for text, low saturation.
"""
from playwright.sync_api import sync_playwright
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

PAGE_W = 794
PAGE_H = 1123

# Morandi Color Palette
MORANDI = {
    'green': '#7C9885',
    'blue': '#8B9DC3',
    'beige': '#B4A992',
    'rose': '#C9A9A6',
    'sage': '#9CAF88',
}

# ============================================================================
# Cover - Color block gradient, no frames
# ============================================================================
COVER_BG_HTML = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    width: {PAGE_W}px;
    height: {PAGE_H}px;
    background: linear-gradient(160deg, #f8faf9 0%, #f0f4f2 100%);
    position: relative;
    overflow: hidden;
}}

/* Top-right large blob */
.blob-1 {{
    position: absolute;
    top: -120px;
    right: -150px;
    width: 550px;
    height: 550px;
    background: radial-gradient(ellipse at center,
        {MORANDI['green']}50 0%,
        {MORANDI['green']}25 40%,
        transparent 70%
    );
    border-radius: 50%;
}}

/* Bottom-left blob */
.blob-2 {{
    position: absolute;
    bottom: -150px;
    left: -120px;
    width: 600px;
    height: 600px;
    background: radial-gradient(ellipse at center,
        {MORANDI['blue']}40 0%,
        {MORANDI['blue']}18 45%,
        transparent 70%
    );
    border-radius: 50%;
}}

/* Center-right blob */
.blob-3 {{
    position: absolute;
    top: 35%;
    right: 5%;
    width: 350px;
    height: 350px;
    background: radial-gradient(ellipse at center,
        {MORANDI['beige']}35 0%,
        transparent 60%
    );
    border-radius: 50%;
}}

/* Top accent bar */
.accent-bar {{
    position: absolute;
    top: 60px;
    left: 60px;
    width: 140px;
    height: 6px;
    background: linear-gradient(90deg, {MORANDI['green']}, {MORANDI['sage']});
    border-radius: 3px;
}}

/* Bottom-right corner accent */
.corner-accent {{
    position: absolute;
    bottom: 50px;
    right: 50px;
    width: 90px;
    height: 90px;
    border: 2.5px solid {MORANDI['green']}40;
    border-radius: 50%;
}}

.corner-accent::after {{
    content: '';
    position: absolute;
    top: 18px;
    left: 18px;
    width: 54px;
    height: 54px;
    background: {MORANDI['green']}20;
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="blob-1"></div>
    <div class="blob-2"></div>
    <div class="blob-3"></div>
    <div class="accent-bar"></div>
    <div class="corner-accent"></div>
</body>
</html>
'''

# ============================================================================
# Back Cover - Echo cover, mirrored positioning
# ============================================================================
BACKCOVER_BG_HTML = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    width: {PAGE_W}px;
    height: {PAGE_H}px;
    background: linear-gradient(200deg, #f8faf9 0%, #f0f4f2 100%);
    position: relative;
    overflow: hidden;
}}

/* Bottom-left blob - echo cover top-right */
.blob-1 {{
    position: absolute;
    bottom: -120px;
    left: -150px;
    width: 500px;
    height: 500px;
    background: radial-gradient(ellipse at center,
        {MORANDI['green']}45 0%,
        {MORANDI['green']}20 40%,
        transparent 70%
    );
    border-radius: 50%;
}}

/* Top-right blob - echo cover bottom-left */
.blob-2 {{
    position: absolute;
    top: -100px;
    right: -80px;
    width: 400px;
    height: 400px;
    background: radial-gradient(ellipse at center,
        {MORANDI['blue']}35 0%,
        transparent 65%
    );
    border-radius: 50%;
}}

/* Top accent */
.top-accent {{
    position: absolute;
    top: 60px;
    right: 60px;
    width: 120px;
    height: 5px;
    background: linear-gradient(90deg, {MORANDI['sage']}, {MORANDI['green']});
    border-radius: 2px;
}}

/* Bottom-left corner accent */
.corner-accent {{
    position: absolute;
    bottom: 50px;
    left: 50px;
    width: 70px;
    height: 70px;
    border: 2px solid {MORANDI['green']}35;
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="blob-1"></div>
    <div class="blob-2"></div>
    <div class="top-accent"></div>
    <div class="corner-accent"></div>
</body>
</html>
'''

# ============================================================================
# Body - More noticeable decoration, but doesn't interfere with reading
# ============================================================================
BODY_BG_HTML = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    width: {PAGE_W}px;
    height: {PAGE_H}px;
    background: #FDFEFE;
    position: relative;
    overflow: hidden;
}}

/* Top gradient band - more noticeable */
.top-gradient {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 120px;
    background: linear-gradient(180deg,
        {MORANDI['green']}12 0%,
        {MORANDI['green']}04 60%,
        transparent 100%
    );
}}

/* Left side bar - thicker and longer */
.side-bar {{
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(180deg,
        {MORANDI['green']}30 0%,
        {MORANDI['green']}15 30%,
        {MORANDI['green']}08 60%,
        transparent 100%
    );
}}

/* Bottom-right subtle decoration */
.corner-blob {{
    position: absolute;
    bottom: -80px;
    right: -80px;
    width: 200px;
    height: 200px;
    background: radial-gradient(ellipse at center,
        {MORANDI['blue']}08 0%,
        transparent 70%
    );
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="top-gradient"></div>
    <div class="side-bar"></div>
    <div class="corner-blob"></div>
</body>
</html>
'''


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': PAGE_W, 'height': PAGE_H},
            device_scale_factor=2
        )

        page.set_content(COVER_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'cover_bg.png'), type='png')
        print("cover_bg.png")

        page.set_content(BACKCOVER_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'backcover_bg.png'), type='png')
        print("backcover_bg.png")

        page.set_content(BODY_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'body_bg.png'), type='png')
        print("body_bg.png")

        browser.close()
    print("Done - Morandi (no glass frames)")


if __name__ == '__main__':
    main()
