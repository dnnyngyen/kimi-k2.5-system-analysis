#!/usr/bin/env node
/**
 * Shared Playwright/Chromium detection utilities.
 * Used by html_to_pdf.js (runtime) and setup.sh (environment check).
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const Module = require('module');
const { execSync, spawnSync } = require('child_process');

function loadPlaywright() {
  try {
    return require('playwright');
  } catch (error) {
    const searchRoots = new Set();

    if (process.env.PLAYWRIGHT_PATH) {
      searchRoots.add(process.env.PLAYWRIGHT_PATH);
    }

    if (process.env.NODE_PATH) {
      process.env.NODE_PATH.split(path.delimiter)
        .filter(Boolean)
        .forEach(entry => searchRoots.add(entry));
    }

    try {
      const npmRoot = execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] })
        .toString()
        .trim();
      if (npmRoot) {
        searchRoots.add(npmRoot);
      }
    } catch (_) {
      // ignore npm errors
    }

    for (const base of searchRoots) {
      if (!base) continue;
      const pkgPath = path.join(base, 'playwright', 'package.json');
      if (!fs.existsSync(pkgPath)) continue;

      try {
        const requireFromBase = Module.createRequire(pkgPath);
        return requireFromBase('playwright');
      } catch (_) {
        // try next path
      }
    }

    throw new Error('Playwright module not found. Install it or set PLAYWRIGHT_PATH.');
  }
}

function getDefaultChromiumPath(chromiumInstance) {
  if (!chromiumInstance) return null;
  try {
    return chromiumInstance.executablePath();
  } catch (_) {
    return null;
  }
}

function extractRevisionFromPath(input) {
  if (!input) return null;
  const match = String(input).match(/(?:chromium|chrome|chromium_headless_shell)-(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

function resolveChromium(options = {}) {
  const {
    chromium = loadPlaywright().chromium,
    allowInstall = false,
  } = options;

  const expectedPath = getDefaultChromiumPath(chromium);
  const expectedRevision = extractRevisionFromPath(expectedPath);

  if (expectedPath && fs.existsSync(expectedPath)) {
    return {
      status: 'ok',
      executablePath: expectedPath,
      revision: extractRevisionFromPath(expectedPath),
      expectedRevision,
      isFallback: false,
      source: 'default'
    };
  }

  const fallback = findExistingChromium(expectedRevision);
  if (fallback) {
    return {
      status: 'fallback',
      executablePath: fallback.path,
      revision: fallback.revision || null,
      expectedRevision,
      isFallback: true,
      source: fallback.source
    };
  }

  if (!allowInstall) {
    return {
      status: 'missing',
      executablePath: expectedPath || '',
      revision: null,
      expectedRevision,
      isFallback: false,
      source: 'missing'
    };
  }

  const installResult = spawnSync('npx', ['playwright', 'install', 'chromium'], {
    stdio: 'inherit',
    shell: true
  });

  if (installResult.status === 0) {
    const installedPath = getDefaultChromiumPath(chromium);
    if (installedPath && fs.existsSync(installedPath)) {
      return {
        status: 'installed',
        executablePath: installedPath,
        revision: extractRevisionFromPath(installedPath),
        expectedRevision: extractRevisionFromPath(installedPath),
        isFallback: false,
        source: 'install'
      };
    }
  }

  const err = new Error('Failed to install Chromium via Playwright');
  err.code = 'INSTALL_FAILED';
  throw err;
}

function findExistingChromium(expectedRevision) {
  const seen = new Set();
  const candidates = [];

  const addCandidate = (candidatePath, revision = null, source = 'cache') => {
    if (!candidatePath || seen.has(candidatePath)) return;
    try {
      fs.accessSync(candidatePath, fs.constants.X_OK);
    } catch (_) {
      return;
    }
    candidates.push({ path: candidatePath, revision, source });
    seen.add(candidatePath);
  };

  ['PLAYWRIGHT_CHROMIUM_PATH', 'CHROMIUM_PATH', 'BROWSER_PATH'].forEach(envName => {
    if (process.env[envName]) {
      addCandidate(process.env[envName], null, 'env');
    }
  });

  getBrowserCacheDirectories().forEach(dir => {
    collectCacheExecutables(dir).forEach(entry => addCandidate(entry.path, entry.revision, 'cache'));
  });

  collectSystemBrowsers().forEach(cmdPath => addCandidate(cmdPath, null, 'system'));

  if (candidates.length === 0) {
    return null;
  }

  const score = (candidate) => {
    if (expectedRevision != null && candidate.revision != null) {
      return Math.abs(candidate.revision - expectedRevision);
    }
    if (candidate.revision != null) {
      return 100000 - candidate.revision;
    }
    return Number.MAX_SAFE_INTEGER;
  };

  candidates.sort((a, b) => {
    const diff = score(a) - score(b);
    if (diff !== 0) return diff;
    const revA = a.revision || 0;
    const revB = b.revision || 0;
    return revB - revA;
  });

  return candidates[0];
}

function getBrowserCacheDirectories() {
  const dirs = new Set();

  if (process.env.PLAYWRIGHT_BROWSERS_PATH) {
    process.env.PLAYWRIGHT_BROWSERS_PATH
      .split(path.delimiter)
      .filter(Boolean)
      .forEach(entry => dirs.add(entry));
  }

  const seenHomes = new Set();
  const addHomeDir = homeDir => {
    if (!homeDir) return;
    const normalized = path.resolve(homeDir);
    if (seenHomes.has(normalized)) return;
    seenHomes.add(normalized);

    if (process.platform === 'darwin') {
      dirs.add(path.join(normalized, 'Library', 'Caches', 'ms-playwright'));
    } else if (process.platform === 'win32') {
      dirs.add(path.join(normalized, 'AppData', 'Local', 'ms-playwright'));
    } else {
      dirs.add(path.join(normalized, '.cache', 'ms-playwright'));
    }
  };

  addHomeDir(os.homedir());
  if (process.env.HOME) addHomeDir(process.env.HOME);

  if (process.platform !== 'win32') {
    addHomeDir('/root');
    if (process.env.SUDO_USER) {
      addHomeDir(path.join('/home', process.env.SUDO_USER));
    }
    if (process.env.USER && process.env.USER !== process.env.SUDO_USER) {
      addHomeDir(path.join('/home', process.env.USER));
    }
    // 显式添加常见沙箱/容器用户的缓存目录
    ['kimi', 'ubuntu', 'sandbox', 'user', 'app'].forEach(user => {
      dirs.add(`/home/${user}/.cache/ms-playwright`);
    });
  }

  const multiUserBases = [];
  if (process.platform === 'darwin') {
    multiUserBases.push('/Users');
  } else if (process.platform !== 'win32') {
    multiUserBases.push('/home');
  }
  multiUserBases.forEach(baseDir => {
    try {
      const entries = fs.readdirSync(baseDir, { withFileTypes: true });
      entries.forEach(entry => {
        if (!entry.isDirectory()) return;
        addHomeDir(path.join(baseDir, entry.name));
      });
    } catch (_) {
      // ignore if /home or /Users not accessible
    }
  });

  if (process.env.PDF_EXTRA_BROWSER_PATHS) {
    process.env.PDF_EXTRA_BROWSER_PATHS
      .split(path.delimiter)
      .filter(Boolean)
      .forEach(entry => dirs.add(entry));
  }

  return Array.from(dirs);
}

function collectCacheExecutables(cacheDir) {
  const executables = [];
  if (!cacheDir) return executables;

  let entries = [];
  try {
    entries = fs.readdirSync(cacheDir);
  } catch (_) {
    return executables;
  }

  entries.forEach(entry => {
    const fullPath = path.join(cacheDir, entry);
    let stats;
    try {
      stats = fs.statSync(fullPath);
    } catch (_) {
      return;
    }
    if (!stats.isDirectory()) return;

    if (!/(chromium|chrome)/i.test(entry)) return;

    const revision = extractRevisionFromPath(entry);
    getExecutableCandidates(fullPath).forEach(candidate => {
      executables.push({ path: candidate, revision });
    });
  });

  return executables;
}

function getExecutableCandidates(baseDir) {
  const candidates = [];
  const pushIfExists = relativeParts => {
    const target = path.join(baseDir, ...relativeParts);
    if (fs.existsSync(target)) {
      candidates.push(target);
    }
  };

  if (process.platform === 'darwin') {
    pushIfExists(['chrome-mac', 'Chromium.app', 'Contents', 'MacOS', 'Chromium']);
    pushIfExists(['Chromium.app', 'Contents', 'MacOS', 'Chromium']);
  } else if (process.platform === 'linux') {
    pushIfExists(['chrome-linux', 'chrome']);
    pushIfExists(['chrome-linux', 'headless_shell']);
    pushIfExists(['chrome-linux', 'chromium']);
    pushIfExists(['chrome-linux64', 'chrome']);
    pushIfExists(['chrome-linux64', 'chromium']);
    pushIfExists(['chrome-linux64', 'headless_shell']);
    pushIfExists(['chrome-linux64', 'chrome-headless-shell']);
  } else if (process.platform === 'win32') {
    pushIfExists(['chrome-win', 'chrome.exe']);
    pushIfExists(['chrome-win', 'msedge.exe']);
  }

  return candidates;
}

function collectSystemBrowsers() {
  const results = [];

  // 直接检查常见系统路径（不依赖 command -v）
  if (process.platform === 'linux') {
    const directPaths = [
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/usr/lib/chromium/chromium',
      '/snap/bin/chromium',
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable'
    ];
    directPaths.forEach(p => {
      try {
        fs.accessSync(p, fs.constants.X_OK);
        results.push(p);
      } catch (_) {}
    });
  }

  // 然后用 command -v 检查
  const commands = [
    'chromium-browser',
    'chromium',
    'google-chrome',
    'google-chrome-stable',
    'chrome',
    'microsoft-edge',
    'msedge'
  ];

  commands.forEach(cmd => {
    const resolved = resolveSystemCommand(cmd);
    if (resolved) {
      results.push(resolved);
    }
  });
  return results;
}

function resolveSystemCommand(cmd) {
  try {
    if (process.platform === 'win32') {
      const output = execSync(`where ${cmd}`, { stdio: ['ignore', 'pipe', 'ignore'] })
        .toString()
        .split(/\r?\n/)
        .map(line => line.trim())
        .find(Boolean);
      return output || null;
    }
    return execSync(`command -v ${cmd}`, { stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim();
  } catch (_) {
    return null;
  }
}

module.exports = {
  loadPlaywright,
  resolveChromium,
  extractRevisionFromPath
};

if (require.main === module) {
  const args = process.argv.slice(2);
  const allowInstall = args.includes('--allow-install');
  const jsonOutput = args.includes('--json');

  try {
    const info = resolveChromium({ allowInstall });
    if (jsonOutput) {
      console.log(JSON.stringify(info, null, 2));
    } else {
      console.log(`${info.status}:${info.executablePath || ''}`);
    }
    process.exit(info.status === 'missing' ? 2 : 0);
  } catch (error) {
    if (jsonOutput) {
      console.error(JSON.stringify({ status: 'error', message: error.message || String(error) }));
    } else {
      console.log(`error:${error.message || error}`);
    }
    process.exit(3);
  }
}
