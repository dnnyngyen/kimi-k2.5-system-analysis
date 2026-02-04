# /mnt/okcomputer/ Analysis
## Working Directory and Output Storage

---

## Executive Summary

`/mnt/okcomputer/` serves as the primary working directory for the Kimi agents including Docs, Sheets, Website, and Slides. It contains deployment artifacts, output files, and upload storage. This directory is the current working directory for the agent process.

---

## 1. Directory Structure

```
/mnt/okcomputer/
├── .todo.jsonl            # Task tracking
├── deploy/                # Deployment artifacts
├── output/                # Generated outputs
│   └── analysis/          # Analysis documents
└── upload/                # User uploads
```

---

## 2. File Purposes

### 2.1 .todo.jsonl

**Purpose**: Task tracking for the agent session

**Format**: JSON Lines (one JSON object per line)

**Contents**: Task status, priority, and content

### 2.2 deploy/

**Purpose**: Deployment artifacts

**Contents**: Files ready for deployment

### 2.3 output/

**Purpose**: Generated outputs

**Contents**: Generated files

### 2.4 upload/

**Purpose**: User uploads

**Contents**: Files uploaded by users

---

## 3. Process Context

```bash
$ pwd
/mnt/okcomputer

$ ls -la
-rw-r--r-- 1 root root 1389 Feb  2 09:08 .todo.jsonl
drwxr-xr-x 0 root root    0 Feb  2 08:27 deploy
drwxr-xr-x 0 root root    0 Feb  2 08:27 output
drwxr-xr-x 0 root root    0 Feb  2 08:27 upload
```

---

## 4. Inter-Module Relationships

```
/mnt/okcomputer/
    ├── .todo.jsonl ──► Task tracking
    ├── deploy/ ──► Deployment
    ├── output/ ──► Generated files
    │   └── analysis/ ──► Documentation
    └── upload/ ──► User uploads
```
