#!/usr/bin/env python3
# ============================================================
# NOTICE: This file was extracted from the Kimi K2.5 agent
# environment. Provided in response to plain-English questions.
# Maintainer does not claim copyright. Included for research
# under CC0 1.0. See LICENSE for details.
# ============================================================
"""
generate_chart.py - Only for complex charts (heatmaps, 3D, radar, etc.)

WARNING: For simple charts (pie, bar, line) use native Word charts!
    Reference scripts/templates/AllInOneTemplate.cs AddPieChart() / AddBarChart()

Use this script only for:
- Heatmaps, 3D charts, radar charts, etc. that Word doesn't natively support
- Complex data visualization (multiple axes, subplots, statistical charts, etc.)

Color scheme: Morandi low-saturation palette
"""
import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Morandi Color Palette - low saturation, elegant
MORANDI = {
    'green': '#7C9885',
    'beige': '#B4A992',
    'blue': '#8B9DC3',
    'brown': '#C4A484',
    'rose': '#C9A9A6',
    'sage': '#9CAF88',
}

# Chart color sequence
CHART_COLORS = [
    MORANDI['green'],
    MORANDI['blue'],
    MORANDI['beige'],
    MORANDI['brown'],
    MORANDI['rose'],
    MORANDI['sage'],
]

# Font configuration - cross-platform
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=CHART_COLORS)

def create_bar_chart():
    """Create bar chart - Quarterly business growth comparison"""

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)

    # Data
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    data_2023 = [85, 92, 88, 95]
    data_2024 = [102, 115, 108, 125]

    x = np.arange(len(quarters))
    width = 0.35

    # Draw bar chart - Morandi colors
    bars1 = ax.bar(x - width/2, data_2023, width, label='2023',
                   color=MORANDI['beige'], edgecolor='none')
    bars2 = ax.bar(x + width/2, data_2024, width, label='2024',
                   color=MORANDI['green'], edgecolor='none')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color='#666666')

    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color='#666666')

    # Style settings
    ax.set_ylabel('Volume (K)', fontsize=11, color='#333333')
    ax.set_xticks(x)
    ax.set_xticklabels(quarters, fontsize=11, color='#333333')
    ax.legend(frameon=False, fontsize=10)

    # Remove borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')

    # Grid lines
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#cccccc')
    ax.set_axisbelow(True)

    # Y-axis range
    ax.set_ylim(0, 145)

    plt.tight_layout()

    # Save
    chart_path = os.path.join(OUTPUT_DIR, 'chart_bar.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Generated: {chart_path}")
    return chart_path


def create_line_chart():
    """Create line chart - Monthly trend"""

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    revenue = [120, 135, 142, 158, 175, 168, 182, 195, 210, 225, 248, 265]
    users = [45, 52, 58, 65, 72, 78, 85, 92, 98, 105, 115, 128]

    # Draw lines - Morandi colors
    ax.plot(months, revenue, marker='o', markersize=5, linewidth=2,
            color=MORANDI['green'], label='Revenue (K)')
    ax.plot(months, users, marker='s', markersize=4, linewidth=2,
            color=MORANDI['blue'], label='Users (K)')

    # Fill area
    ax.fill_between(months, revenue, alpha=0.15, color=MORANDI['green'])

    # Style
    ax.set_ylabel('Value', fontsize=11, color='#333333')
    ax.legend(frameon=False, fontsize=10, loc='upper left')

    # Remove borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')

    # Grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#cccccc')
    ax.set_axisbelow(True)

    # X-axis label rotation
    plt.xticks(rotation=45, ha='right', fontsize=9)

    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, 'chart_line.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Generated: {chart_path}")
    return chart_path


def create_area_chart():
    """Create stacked area chart - Cumulative trend"""

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    months = ['Q1', 'Q2', 'Q3', 'Q4']
    product_a = [30, 45, 55, 70]
    product_b = [20, 35, 45, 55]
    product_c = [15, 25, 30, 40]

    # Stacked area chart - Morandi colors
    ax.stackplot(months, product_a, product_b, product_c,
                 labels=['Product A', 'Product B', 'Product C'],
                 colors=[MORANDI['green'], MORANDI['blue'], MORANDI['beige']],
                 alpha=0.85)

    ax.set_ylabel('Sales (K)', fontsize=11, color='#333333')
    ax.legend(loc='upper left', frameon=False, fontsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')

    ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#cccccc')
    ax.set_axisbelow(True)

    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, 'chart_area.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Generated: {chart_path}")
    return chart_path


def create_horizontal_bar():
    """Create horizontal bar chart - Comparison"""

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    categories = ['Market Expansion', 'Product R&D', 'Customer Service', 'Operations', 'Branding']
    current = [75, 88, 82, 70, 65]
    target = [90, 95, 90, 85, 80]

    y = np.arange(len(categories))
    height = 0.35

    bars1 = ax.barh(y - height/2, current, height, label='Current',
                    color=MORANDI['green'], edgecolor='none')
    bars2 = ax.barh(y + height/2, target, height, label='Target',
                    color=MORANDI['beige'], edgecolor='none')

    ax.set_xlabel('Completion (%)', fontsize=11, color='#333333')
    ax.set_yticks(y)
    ax.set_yticklabels(categories, fontsize=10)
    ax.legend(frameon=False, fontsize=10, loc='lower right')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')

    ax.xaxis.grid(True, linestyle='--', alpha=0.3, color='#cccccc')
    ax.set_axisbelow(True)
    ax.set_xlim(0, 100)

    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, 'chart_hbar.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Generated: {chart_path}")
    return chart_path


def create_pie_chart():
    """Create pie chart - Market share"""

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    labels = ['Product A', 'Product B', 'Product C', 'Others']
    sizes = [35, 28, 22, 15]
    colors = [MORANDI['green'], MORANDI['blue'], MORANDI['beige'], MORANDI['rose']]
    explode = (0.02, 0, 0, 0)

    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
                                       colors=colors, autopct='%1.0f%%',
                                       startangle=90, pctdistance=0.6,
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    # Style
    for text in texts:
        text.set_fontsize(11)
        text.set_color('#333333')
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_color('white')
        autotext.set_weight('bold')

    ax.axis('equal')

    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, 'chart_pie.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Generated: {chart_path}")
    return chart_path


if __name__ == '__main__':
    create_bar_chart()
    create_line_chart()
    create_area_chart()
    create_horizontal_bar()
    create_pie_chart()
    print("\nAll charts generated with Morandi color scheme")
