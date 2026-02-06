#!/usr/bin/env node
/**
 * HTML to PDF Conversion Script - Using Playwright + Paged.js
 *
 * Usage:
 *   node html_to_pdf.js input.html
 *   node html_to_pdf.js input.html --output custom.pdf
 */

const fs = require('fs');
const path = require('path');
const { loadPlaywright, resolveChromium } = require('./browser_helper');

const { chromium } = loadPlaywright();

// ============================================================================
// Utility: delay function (replaces deprecated page.waitForTimeout)
// ============================================================================
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// Browser availability handled by shared helper (browser_helper.js)
// ============================================================================

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Usage: node html_to_pdf.js <input.html> [options]

Options:
  --output, -o <file>   Output PDF file path (default: same name as input.pdf)
  --css <file>          Custom CSS file path
  --help, -h            Show help information

Examples:
  node html_to_pdf.js document.html
  node html_to_pdf.js document.html --output output.pdf
    `);
    process.exit(0);
  }

  const inputFile = args[0];
  let outputFile = null;
  let customCSS = null;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--output' || args[i] === '-o') {
      outputFile = args[++i];
    } else if (args[i] === '--css') {
      customCSS = args[++i];
    }
  }

  // If no output file specified, use input file name
  if (!outputFile) {
    const parsedPath = path.parse(inputFile);
    outputFile = path.join(parsedPath.dir || '.', parsedPath.name + '.pdf');
  }

  return { inputFile, outputFile, customCSS };
}

// Format file size
function formatSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

// Main function
async function convertHTMLToPDF(inputFile, outputFile, customCSS) {
  // Check if input file exists
  if (!fs.existsSync(inputFile)) {
    console.error(`Error: File not found ${inputFile}`);
    process.exit(1);
  }

  // Ensure browser is available before proceeding
  const allowInstall = process.env.PDF_SKIP_BROWSER_INSTALL === '1' ? false : true;
  const browserInfo = resolveChromium({ chromium, allowInstall });

  if (browserInfo.status === 'missing') {
    console.error('\n❌ Chromium browser not found.');
    console.error('   Please run: npx playwright install chromium');
    console.error('   Or set PLAYWRIGHT_CHROMIUM_PATH to an existing executable.');
    console.error('');
    process.exit(2);
  }

  if (browserInfo.status === 'fallback') {
    console.log('');
    console.log('⚠️  Using existing Chromium executable (version may not match Playwright):');
    console.log(`   ${browserInfo.executablePath}`);
    console.log('   Set PLAYWRIGHT_CHROMIUM_PATH to override this path.');
    console.log('');
  } else if (browserInfo.status === 'installed') {
    console.log('');
    console.log('✓ Chromium installed successfully.');
    console.log('');
  }

  console.log(`Converting ${path.basename(inputFile)}...`);

  // Read HTML file
  const inputPath = path.resolve(inputFile);
  const outputPath = path.resolve(outputFile);
  let htmlContent = fs.readFileSync(inputPath, 'utf-8');

  // Inject custom CSS if provided
  if (customCSS) {
    if (!fs.existsSync(customCSS)) {
      console.error(`Error: CSS file not found ${customCSS}`);
      process.exit(1);
    }
    const cssContent = fs.readFileSync(customCSS, 'utf-8');
    const cssTag = `<style>${cssContent}</style>`;

    // Insert CSS before </head>
    if (htmlContent.includes('</head>')) {
      htmlContent = htmlContent.replace('</head>', `${cssTag}\n</head>`);
    } else {
      htmlContent = cssTag + '\n' + htmlContent;
    }
  }

  // Launch browser with error handling for missing system dependencies
  let browser;
  try {
    const launchOptions = { headless: true };
    if (browserInfo && browserInfo.isFallback && browserInfo.executablePath) {
      launchOptions.executablePath = browserInfo.executablePath;
    }
    browser = await chromium.launch(launchOptions);
  } catch (launchError) {
    const errorMsg = launchError.message || '';

    // Check for common Ubuntu/Linux dependency issues
    if (errorMsg.includes('shared libraries') || errorMsg.includes('.so')) {
      console.error('\n❌ Chromium launch failed: Missing system libraries');
      console.error('');
      console.error('On Ubuntu/Debian, install dependencies with:');
      console.error('  npx playwright install-deps chromium');
      console.error('');
      console.error('Or install common libraries manually:');
      console.error('  sudo apt-get install -y libgbm1 libasound2 libatk-bridge2.0-0 \\');
      console.error('    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \\');
      console.error('    libxrandr2 libatspi2.0-0 libcups2');
      console.error('');
      process.exit(1);
    }

    if (errorMsg.includes('ENOENT') || errorMsg.includes('executable')) {
      console.error('\n❌ Chromium executable not found');
      console.error('');
      console.error('Install chromium with:');
      console.error('  npx playwright install chromium');
      console.error('');
      process.exit(1);
    }

    // Generic error
    console.error('\n❌ Failed to launch browser:', errorMsg);
    process.exit(1);
  }

  let pageCount = 0;
  let contentStats = null;
  let pageStats = [];

  try {
    const page = await browser.newPage();

    // Load HTML content
    const fileUrl = 'file://' + inputPath;
    await page.goto(fileUrl, {
      waitUntil: 'networkidle'
    });

    // Detect CSS Counter usage (will break with Paged.js)
    const counterWarnings = await page.evaluate(() => {
      const warnings = [];
      const styles = document.querySelectorAll('style');

      styles.forEach((style, idx) => {
        const css = style.textContent || '';

        // Check for counter-reset (excluding @page which is safe)
        const counterResetMatches = css.match(/[^@]counter-reset\s*:\s*([^;]+)/gi);
        if (counterResetMatches) {
          counterResetMatches.forEach(m => {
            // Extract selector context
            const beforeMatch = css.substring(0, css.indexOf(m));
            const lastBrace = beforeMatch.lastIndexOf('{');
            const selectorStart = beforeMatch.lastIndexOf('}', lastBrace) + 1;
            const selector = beforeMatch.substring(selectorStart, lastBrace).trim().split('\n').pop().trim();
            if (selector && !selector.startsWith('@page')) {
              warnings.push({ type: 'counter-reset', selector, styleIndex: idx });
            }
          });
        }

        // Check for counter-increment
        const counterIncMatches = css.match(/counter-increment\s*:\s*([^;]+)/gi);
        if (counterIncMatches) {
          counterIncMatches.forEach(m => {
            const beforeMatch = css.substring(0, css.indexOf(m));
            const lastBrace = beforeMatch.lastIndexOf('{');
            const selectorStart = beforeMatch.lastIndexOf('}', lastBrace) + 1;
            const selector = beforeMatch.substring(selectorStart, lastBrace).trim().split('\n').pop().trim();
            if (selector) {
              warnings.push({ type: 'counter-increment', selector, styleIndex: idx });
            }
          });
        }

        // Check for content: counter()
        if (/content\s*:\s*[^;]*counter\s*\(/i.test(css)) {
          const matches = css.match(/content\s*:\s*[^;]*counter\s*\([^)]+\)/gi);
          if (matches) {
            matches.forEach(m => {
              const beforeMatch = css.substring(0, css.indexOf(m));
              const lastBrace = beforeMatch.lastIndexOf('{');
              const selectorStart = beforeMatch.lastIndexOf('}', lastBrace) + 1;
              const selector = beforeMatch.substring(selectorStart, lastBrace).trim().split('\n').pop().trim();
              // Exclude @page counters (page numbers are safe)
              if (selector && !selector.includes('@page') && !selector.includes('footnote') &&
                  !selector.includes('@top') && !selector.includes('@bottom')) {
                warnings.push({ type: 'content:counter()', selector, styleIndex: idx });
              }
            });
          }
        }
      });

      return warnings;
    });

    if (counterWarnings.length > 0) {
      console.log('\n⚠️  CSS Counter detected (will break with Paged.js):');
      const seen = new Set();
      counterWarnings.forEach(w => {
        const key = `${w.selector}:${w.type}`;
        if (!seen.has(key)) {
          seen.add(key);
          console.log(`  ${w.selector} → ${w.type}`);
        }
      });
      console.log('  Fix: Use data-* attributes with explicit numbers instead.\n');
    }

    // Wait for Mermaid diagrams to render (if any)
    const hasMermaid = await page.evaluate(() => {
      return document.querySelectorAll('.mermaid').length > 0;
    });
    if (hasMermaid) {
      console.log('Waiting for Mermaid diagrams to render...');
      await page.waitForFunction(() => {
        const mermaids = document.querySelectorAll('.mermaid');
        for (const m of mermaids) {
          if (!m.querySelector('svg') && !m.getAttribute('data-processed')) {
            return false;
          }
        }
        return true;
      }, { timeout: 30000 });
      // Allow extra time for Mermaid SVG rendering to stabilize
      await delay(2000);
    }

    // Wait and ensure KaTeX rendering is complete
    const katexStatus = await page.evaluate(() => {
      const hasKatexLib = typeof renderMathInElement === 'function' || typeof katex !== 'undefined';
      const hasRenderedKatex = document.querySelectorAll('.katex').length > 0;
      const bodyText = document.body.innerText;
      const hasUnrenderedMath = /\$[^$]+\$/.test(bodyText) || /\$\$[^$]+\$\$/.test(bodyText);
      return { hasKatexLib, hasRenderedKatex, hasUnrenderedMath };
    });

    if (katexStatus.hasKatexLib && !katexStatus.hasRenderedKatex && katexStatus.hasUnrenderedMath) {
      console.log('Detected unrendered math formulas, triggering KaTeX rendering...');
      await page.evaluate(() => {
        if (typeof renderMathInElement === 'function') {
          renderMathInElement(document.body, {
            delimiters: [
              {left: "$$", right: "$$", display: true},
              {left: "$", right: "$", display: false}
            ],
            throwOnError: false
          });
        }
      });
      // Allow time for KaTeX rendering to complete
      await delay(1000);
    } else if (katexStatus.hasRenderedKatex) {
      // Brief pause to ensure KaTeX fonts are loaded
      await delay(500);
    }

    // Detect and fix overly tall elements
    const fixedElements = await page.evaluate(() => {
      const PAGE_HEIGHT_PX = 1000;
      const selectors = [
        '[style*="page-break-inside: avoid"]',
        '[style*="break-inside: avoid"]',
        '.avoid-break', 'table', 'figure', '.theorem', '.algorithm'
      ];
      let fixed = 0;
      selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
          if (el.getBoundingClientRect().height > PAGE_HEIGHT_PX) {
            el.style.pageBreakInside = 'auto';
            el.style.breakInside = 'auto';
            fixed++;
          }
        });
      });
      return fixed;
    });
    if (fixedElements > 0) {
      console.log(`Warning: Detected ${fixedElements} overly tall elements, removed page-break-inside: avoid`);
    }

    // Fix CSS counter issue before Paged.js processes the DOM
    // Paged.js splits elements across pages, which breaks CSS counter-reset
    // Solution: "burn in" counter values as data attributes before Paged.js runs
    const counterFixCount = await page.evaluate(() => {
      let fixedCount = 0;

      // Find all <ol> elements that might use custom counters
      const olLists = document.querySelectorAll('ol');

      olLists.forEach(ol => {
        const computedStyle = window.getComputedStyle(ol);
        const liItems = ol.querySelectorAll(':scope > li');

        if (liItems.length === 0) return;

        // Check if this ol uses custom numbering (list-style: none indicates custom ::before)
        const listStyleType = computedStyle.listStyleType;
        const hasCustomNumbering = listStyleType === 'none';

        // Also check if any li has ::before with counter content
        const firstLi = liItems[0];
        const beforeStyle = window.getComputedStyle(firstLi, '::before');
        const beforeContent = beforeStyle.content;

        // If using counter() in ::before or list-style: none
        if (hasCustomNumbering || (beforeContent && beforeContent !== 'none' && beforeContent !== '""')) {
          // Mark this ol as counter-fixed
          ol.setAttribute('data-counter-fixed', 'true');

          // Add data-counter attribute to each li
          liItems.forEach((li, index) => {
            li.setAttribute('data-counter', index + 1);
            fixedCount++;
          });
        }
      });

      // Inject CSS to use data-counter attribute instead of CSS counter
      if (fixedCount > 0) {
        const style = document.createElement('style');
        style.setAttribute('data-counter-fix', 'true');
        style.textContent = `
          /* Override CSS counter with data-counter attribute */
          ol[data-counter-fixed] {
            counter-reset: none !important;
          }
          ol[data-counter-fixed] > li::before {
            content: "[" attr(data-counter) "] " !important;
            counter-increment: none !important;
          }
        `;
        document.head.appendChild(style);
      }

      return fixedCount;
    });

    if (counterFixCount > 0) {
      console.log(`Fixed ${counterFixCount} list items with CSS counter preservation`);
    }

    // Inject Paged.js library (prefer local, fallback to CDN)
    const pagedJsLocal = path.join(__dirname, 'paged.polyfill.js');
    if (fs.existsSync(pagedJsLocal)) {
      const pagedJsContent = fs.readFileSync(pagedJsLocal, 'utf-8');
      await page.addScriptTag({ content: pagedJsContent });
    } else {
      console.log('Warning: Local paged.polyfill.js not found, using CDN...');
      await page.addScriptTag({
        url: 'https://unpkg.com/pagedjs@0.4.3/dist/paged.polyfill.js'
      });
    }

    // Wait for Paged.js to complete pagination (wait until page count stabilizes)
    console.log('Waiting for Paged.js pagination...');
    let lastPageCount = 0;
    let stableCount = 0;
    const maxWaitTime = 120000; // 2 minutes max
    const startTime = Date.now();

    // First, wait for at least one page to appear
    await page.waitForFunction(() => {
      return document.querySelectorAll('.pagedjs_page').length > 0;
    }, { timeout: 120000 });

    // Then wait for page count to stabilize (no change for 3 consecutive checks)
    while (stableCount < 3) {
      if (Date.now() - startTime > maxWaitTime) {
        console.log('Warning: Pagination timeout, proceeding with current state');
        break;
      }

      // Poll interval for pagination stability check
      await delay(1000);
      const currentPageCount = await page.evaluate(() =>
        document.querySelectorAll('.pagedjs_page').length
      );

      if (currentPageCount === lastPageCount) {
        stableCount++;
      } else {
        stableCount = 0;
        lastPageCount = currentPageCount;
        console.log(`  Pagination in progress: ${currentPageCount} pages...`);
      }
    }

    console.log(`Pagination complete: ${lastPageCount} pages`);
    // Final stabilization pause before PDF export
    await delay(1000);

    // Detect overflow elements
    const overflows = await page.evaluate(() => {
      const results = [];
      const selectors = 'pre, table, figure, img, svg, .mermaid, blockquote, .equation';
      document.querySelectorAll(selectors).forEach(el => {
        const scrollW = el.scrollWidth;
        const clientW = el.clientWidth;
        if (scrollW > clientW + 2) {  // +2 tolerance
          results.push({
            tag: el.tagName.toLowerCase(),
            class: el.className || '',
            overflow: scrollW - clientW,
            preview: (el.textContent || '').slice(0, 60).replace(/\s+/g, ' ')
          });
        }
      });
      return results;
    });

    if (overflows.length > 0) {
      console.log('\n⚠️  Overflow detected:');
      overflows.forEach(o => {
        console.log(`  <${o.tag}${o.class ? ' class="' + o.class + '"' : ''}> overflow ${o.overflow}px`);
        if (o.preview) console.log(`    "${o.preview.slice(0, 40)}..."`);
      });
    }

    // Get page count and per-page statistics
    const analysisResult = await page.evaluate(() => {
      const pages = document.querySelectorAll('.pagedjs_page');
      const pageCount = pages.length;

      // Count words per page
      const pageStats = [];
      let totalChinese = 0;
      let totalEnglish = 0;

      pages.forEach((p, i) => {
        const text = p.innerText || '';
        const chinese = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
        const english = (text.match(/[a-zA-Z]+/g) || []).length;
        const wordCount = chinese + english;
        totalChinese += chinese;
        totalEnglish += english;

        // Detect TOC pages (contain many page number patterns)
        const tocPattern = (text.match(/\.{3,}\s*\d+|…+\s*\d+/g) || []).length;
        const isToc = tocPattern >= 5;

        pageStats.push({
          page: i + 1,
          wordCount,
          isToc,
          isFirst: i === 0
        });
      });

      // Count figures and tables
      const figures = document.querySelectorAll('figure, .figure, img').length;
      const tables = document.querySelectorAll('table').length;

      return {
        pageCount,
        pageStats,
        totalWords: totalChinese + totalEnglish,
        figures,
        tables
      };
    });

    pageCount = analysisResult.pageCount;
    pageStats = analysisResult.pageStats;
    contentStats = {
      wordCount: analysisResult.totalWords,
      figures: analysisResult.figures,
      tables: analysisResult.tables
    };

    // Export PDF
    // WORKAROUND: scale=1.5 fixes a page filling issue where content renders
    // at ~67% size without this correction. Root cause is unclear but appears
    // related to Paged.js internal scaling. Discovered through extensive testing.
    // TODO: Investigate Paged.js source to find root cause and proper fix.
    // Current workaround is safe for all tested cases (covers, KaTeX, tables, etc.)
    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      tagged: true,
      scale: 1.5  // See WORKAROUND comment above
    });

    console.log('\nConversion successful');

    // Output PDF information
    const stats = fs.statSync(outputPath);
    console.log('\n========================');
    console.log('PDF Information');
    console.log('========================');
    console.log(`File: ${path.basename(outputPath)}`);
    console.log(`Pages: ${pageCount}`);
    console.log(`Size: ${formatSize(stats.size)}`);
    console.log(`Words: ~${contentStats.wordCount.toLocaleString()}`);
    console.log(`Figures/Tables: ${contentStats.figures} figures / ${contentStats.tables} tables`);
    console.log(`Path: ${outputPath}`);

    // Anomaly detection
    const contentPages = pageStats.filter(p => !p.isToc && !p.isFirst);
    if (contentPages.length > 0) {
      const avgWords = contentPages.reduce((sum, p) => sum + p.wordCount, 0) / contentPages.length;
      const anomalies = [];

      pageStats.forEach(p => {
        if (p.isFirst || p.isToc) return;

        // Blank/near-blank pages
        if (p.wordCount < 50) {
          anomalies.push({ page: p.page, type: 'Blank page', detail: `only ${p.wordCount} words` });
        }
        // Low content (below 25% of average)
        else if (avgWords > 0 && p.wordCount < avgWords * 0.25) {
          const pct = Math.round(p.wordCount / avgWords * 100);
          anomalies.push({ page: p.page, type: 'Low content', detail: `${p.wordCount} words (avg ${Math.round(avgWords)}, only ${pct}%)` });
        }
      });

      if (anomalies.length > 0) {
        console.log('\n========================');
        console.log('Anomaly Detection');
        console.log('========================');
        anomalies.forEach(a => {
          console.log(`  P${a.page}: [${a.type}] ${a.detail}`);
        });
      }
    }

  } catch (error) {
    console.error('\nConversion failed');
    console.error(error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

// Main entry point
(async () => {
  try {
    const { inputFile, outputFile, customCSS } = parseArgs();
    await convertHTMLToPDF(inputFile, outputFile, customCSS);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
