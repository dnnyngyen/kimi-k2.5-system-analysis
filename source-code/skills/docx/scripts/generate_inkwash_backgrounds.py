#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
Ink-Wash (水墨侘寂) Background Generator.

Design: Chinese ink wash painting style - subtle gray gradients,
like ink spreading on rice paper. Zen-inspired minimalism.

Colors: Gray scale from charcoal (#1A202C) to misty white (#F7FAFC)
"""
from playwright.sync_api import sync_playwright
import os
import sys

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))

PAGE_W = 794
PAGE_H = 1123

# 水墨色阶 - Ink Wash Gray Scale
INK = {
    'charcoal': '#1A202C',    # 浓墨
    'graphite': '#2D3748',    # 重墨
    'slate': '#4A5568',       # 中墨
    'stone': '#718096',       # 淡墨
    'mist': '#A0AEC0',        # 轻墨
    'cloud': '#CBD5E0',       # 烟墨
    'paper': '#EDF2F7',       # 宣纸
    'snow': '#F7FAFC',        # 雪白
}

# ============================================================================
# Cover - Ink wash gradient, zen-inspired
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
    background: linear-gradient(165deg, {INK['snow']} 0%, {INK['paper']} 100%);
    position: relative;
    overflow: hidden;
}}

/* Top-right ink splash */
.ink-splash-1 {{
    position: absolute;
    top: -100px;
    right: -100px;
    width: 480px;
    height: 480px;
    background: radial-gradient(ellipse at center,
        {INK['stone']}35 0%,
        {INK['mist']}18 45%,
        transparent 70%
    );
    border-radius: 45% 55% 40% 60%;
    transform: rotate(-15deg);
}}

/* Bottom-left ink diffusion */
.ink-splash-2 {{
    position: absolute;
    bottom: -130px;
    left: -100px;
    width: 520px;
    height: 520px;
    background: radial-gradient(ellipse at center,
        {INK['slate']}28 0%,
        {INK['stone']}12 50%,
        transparent 72%
    );
    border-radius: 55% 45% 60% 40%;
    transform: rotate(10deg);
}}

/* Center accent - like brush stroke */
.brush-stroke {{
    position: absolute;
    top: 55%;
    right: 8%;
    width: 200px;
    height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        {INK['mist']}60 20%,
        {INK['stone']}40 50%,
        {INK['mist']}30 80%,
        transparent 100%
    );
    transform: rotate(-5deg);
}}

/* Top-left corner seal mark hint */
.seal-hint {{
    position: absolute;
    top: 50px;
    left: 55px;
    width: 8px;
    height: 60px;
    background: linear-gradient(180deg, {INK['slate']}40, {INK['stone']}20);
    border-radius: 2px;
}}

/* Bottom-right zen circle */
.zen-circle {{
    position: absolute;
    bottom: 45px;
    right: 45px;
    width: 80px;
    height: 80px;
    border: 2px solid {INK['mist']}50;
    border-radius: 50%;
}}

.zen-circle::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 12px;
    height: 12px;
    background: {INK['stone']}30;
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="ink-splash-1"></div>
    <div class="ink-splash-2"></div>
    <div class="brush-stroke"></div>
    <div class="seal-hint"></div>
    <div class="zen-circle"></div>
</body>
</html>
'''

# ============================================================================
# Back Cover - Mirrored zen composition
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
    background: linear-gradient(195deg, {INK['snow']} 0%, {INK['paper']} 100%);
    position: relative;
    overflow: hidden;
}}

/* Bottom-left ink splash - mirror of cover */
.ink-splash-1 {{
    position: absolute;
    bottom: -100px;
    left: -100px;
    width: 450px;
    height: 450px;
    background: radial-gradient(ellipse at center,
        {INK['stone']}30 0%,
        {INK['mist']}15 45%,
        transparent 70%
    );
    border-radius: 55% 45% 50% 50%;
    transform: rotate(15deg);
}}

/* Top-right subtle mist */
.ink-splash-2 {{
    position: absolute;
    top: -80px;
    right: -60px;
    width: 350px;
    height: 350px;
    background: radial-gradient(ellipse at center,
        {INK['mist']}22 0%,
        transparent 65%
    );
    border-radius: 45% 55% 40% 60%;
}}

/* Top accent stroke */
.brush-stroke {{
    position: absolute;
    top: 55px;
    right: 50px;
    width: 100px;
    height: 4px;
    background: linear-gradient(90deg,
        {INK['stone']}35,
        {INK['mist']}20
    );
    border-radius: 2px;
}}

/* Bottom-left seal hint */
.seal-hint {{
    position: absolute;
    bottom: 45px;
    left: 45px;
    width: 60px;
    height: 60px;
    border: 1.5px solid {INK['mist']}40;
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="ink-splash-1"></div>
    <div class="ink-splash-2"></div>
    <div class="brush-stroke"></div>
    <div class="seal-hint"></div>
</body>
</html>
'''

# ============================================================================
# Body - Minimal ink wash, doesn't interfere with reading
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
    background: {INK['snow']};
    position: relative;
    overflow: hidden;
}}

/* Top gradient - like ink diffusing at paper edge */
.top-wash {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100px;
    background: linear-gradient(180deg,
        {INK['mist']}10 0%,
        {INK['cloud']}05 50%,
        transparent 100%
    );
}}

/* Left edge - subtle ink border */
.left-edge {{
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg,
        {INK['stone']}25 0%,
        {INK['mist']}12 40%,
        {INK['cloud']}06 70%,
        transparent 100%
    );
}}

/* Bottom-right corner - very subtle cloud */
.corner-mist {{
    position: absolute;
    bottom: -60px;
    right: -60px;
    width: 150px;
    height: 150px;
    background: radial-gradient(ellipse at center,
        {INK['mist']}06 0%,
        transparent 70%
    );
    border-radius: 50%;
}}
</style>
</head>
<body>
    <div class="top-wash"></div>
    <div class="left-edge"></div>
    <div class="corner-mist"></div>
</body>
</html>
'''


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': PAGE_W, 'height': PAGE_H},
            device_scale_factor=2
        )

        page.set_content(COVER_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'cover_bg.png'), type='png')
        print(f"cover_bg.png -> {OUTPUT_DIR}")

        page.set_content(BACKCOVER_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'backcover_bg.png'), type='png')
        print(f"backcover_bg.png -> {OUTPUT_DIR}")

        page.set_content(BODY_BG_HTML)
        page.screenshot(path=os.path.join(OUTPUT_DIR, 'body_bg.png'), type='png')
        print(f"body_bg.png -> {OUTPUT_DIR}")

        browser.close()
    print("Done - Ink Wash (水墨侘寂)")


if __name__ == '__main__':
    main()
