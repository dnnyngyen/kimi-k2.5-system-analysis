# Chrome Data Analysis
## `/app/data/chrome_data/` — Chromium Profile Persistence

---

## Executive Summary

The `chrome_data/` directory serves as the persistent user data directory for Chromium instances launched by `browser_guard.py`. This profile stores cookies, browsing history, extension state, and cached data across browser sessions, enabling stateful browser automation.

---

## 1. Directory Structure

```
chrome_data/
├── Default/                        # Default Chrome profile
│   ├── Cache/                      # HTTP response cache
│   ├── Code Cache/                 # V8 bytecode cache
│   ├── Cookies                     # SQLite cookies database
│   ├── Cookies-journal             # SQLite journal file
│   ├── DawnWebGPUCache/            # WebGPU shader cache
│   ├── Extension Scripts/          # Extension JavaScript
│   ├── Extension State/            # Extension storage
│   ├── Favicons                    # Favicon database
│   ├── GPUCache/                   # GPU shader cache
│   ├── History                     # Browsing history
│   ├── History-journal             # History journal
│   ├── Local Storage/              # DOM localStorage
│   ├── Login Data                  # Saved passwords
│   ├── Network Action Predictor    # Prefetch data
│   ├── Preferences                 # Chrome preferences JSON
│   ├── Safe Browsing Cookies       # Security cookies
│   ├── Secure Preferences          # Encrypted preferences
│   ├── Session Storage/            # DOM sessionStorage
│   ├── SharedDictionary/           # Compression dictionaries
│   ├── Shortcuts                   # URL shortcuts
│   ├── Site Characteristics Database/  # Site behavior data
│   ├── Top Sites                   # New tab page tiles
│   ├── Trust Tokens                # Privacy tokens
│   ├── Web Data                    # Autofill data
│   ├── WebStorage/                 # Storage quotas
│   └── shared_proto_db/            # Protocol buffer DB
├── first_party_sets.db             # First-party sets
├── GraphiteDawnCache/              # Graphite cache
├── Local State                     # Chrome state JSON
└── Variations                      # Field trial data
```

---

## 2. Data Categories

### 2.1 Authentication Data

| File | Format | Sensitivity | Content |
|------|--------|-------------|---------|
| `Cookies` | SQLite | **HIGH** | Session tokens, login state |
| `Login Data` | SQLite (encrypted) | **HIGH** | Saved passwords |
| `Safe Browsing Cookies` | SQLite | Medium | Security-related cookies |

**Encryption**: `Login Data` uses Chrome's encryption (OS keyring on Linux).

### 2.2 Browsing History

| File | Format | Sensitivity | Content |
|------|--------|-------------|---------|
| `History` | SQLite | Medium | URL history, visit counts |
| `Favicons` | SQLite | Low | Favicon images |
| `Shortcuts` | SQLite | Low | Typed URL shortcuts |
| `Top Sites` | SQLite | Low | New tab page tiles |

### 2.3 Storage Data

| Directory | API | Sensitivity | Content |
|-----------|-----|-------------|---------|
| `Local Storage/` | localStorage | Medium | Persistent key-value storage |
| `Session Storage/` | sessionStorage | Low | Session-scoped storage |
| `WebStorage/` | Quota Management | Low | Storage quota tracking |
| `IndexedDB/` | IndexedDB | Medium | Structured client-side storage |

### 2.4 Extension Data

| Directory/File | Purpose |
|----------------|---------|
| `Extension Scripts/` | Extension JavaScript code |
| `Extension State/` | Extension settings and data |
| `../pdf-viewer/` | PDF.js extension (external) |

### 2.5 Cache Data

| Directory | Purpose |
|-----------|---------|
| `Cache/` | HTTP response cache |
| `Code Cache/` | V8 compiled bytecode |
| `GPUCache/` | GPU shader programs |
| `DawnWebGPUCache/` | WebGPU shader cache |
| `GraphiteDawnCache/` | Graphite rendering cache |

### 2.6 Configuration Data

| File | Format | Content |
|------|--------|---------|
| `Preferences` | JSON | User settings, extensions, themes |
| `Secure Preferences` | Encrypted JSON | Sensitive settings |
| `Local State` | JSON | Chrome state, profile info |
| `Variations` | Binary | Field trial configurations |

---

## 3. Operational Role

### 3.1 Persistence Across Sessions

```python
# In browser_guard.py
launch_options = {
    "user_data_dir": "/app/data/chrome_data",
    # ...
}
```

**Benefits**:
- Cookies survive browser restarts
- Login sessions maintained
- Extension settings preserved
- Cache improves subsequent loads
- History available for navigation

### 3.2 Launch Sequence

```
1. browser_guard.py starts
2. Checks X11 display
3. Launches Chromium with --user-data-dir=/app/data/chrome_data
4. Chrome reads existing profile
5. Session state restored
```

---

## 4. Security Analysis

### 4.1 Sensitive Data Exposure

| Data Type | Risk Level | Mitigation |
|-----------|------------|------------|
| Session cookies | **HIGH** | Profile isolation per user |
| Saved passwords | **HIGH** | OS-level encryption |
| Browsing history | Medium | Regular cleanup |
| Autofill data | Medium | User consent |
| Extension data | Low | Extension permissions |

### 4.2 Multi-Tenant Considerations

**Risk**: In multi-user environments, shared profile exposes data.

**Recommendation**: Create isolated profiles per session:
```python
import tempfile
import shutil

# Create temp profile
profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")

# Use isolated profile
launch_options["user_data_dir"] = profile_dir

# Cleanup after session
shutil.rmtree(profile_dir)
```

### 4.3 Encryption Status

| File | Encrypted | Key Storage |
|------|-----------|-------------|
| `Cookies` | No | — |
| `Login Data` | Yes | OS keyring (gnome-keyring, kwallet) |
| `Secure Preferences` | Yes | Same as Login Data |
| `History` | No | — |

---

## 5. Inter-Module Relationships

```
chrome_data/
    ├── browser_guard.py (reads/writes)
    │   └── Playwright/CDP
    ├── pdf-viewer/ (extension state)
    │   └── PDF.js settings
    └── logs/ (correlated with History)
```

---

## 6. Maintenance

### 6.1 Cleanup Operations

```bash
# Clear cache
rm -rf /app/data/chrome_data/Default/Cache/*

# Clear cookies (logout all sessions)
rm /app/data/chrome_data/Default/Cookies

# Clear history
rm /app/data/chrome_data/Default/History

# Full reset
rm -rf /app/data/chrome_data/*
```

### 6.2 Size Monitoring

| Directory | Typical Size | Growth Rate |
|-----------|--------------|-------------|
| `Cache/` | 50-500 MB | Linear with usage |
| `Code Cache/` | 10-100 MB | Stable after warmup |
| `History` | 1-10 MB | Slow growth |
| `Cookies` | 100 KB - 1 MB | Slow growth |

---

## 7. Troubleshooting

### 7.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Chrome won't start | Corrupted profile | Delete and recreate |
| Extension not loading | Extension state corrupt | Clear Extension State |
| Login lost | Cookies cleared | Expected behavior |
| Slow startup | Large cache | Clear Cache/ |

---

*Document Version: 1.0*
*Analysis Date: 2026-02-02*
