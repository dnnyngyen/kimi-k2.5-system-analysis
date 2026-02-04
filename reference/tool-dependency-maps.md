# Tool Relationship Map

## Dependency Graph

```
User Request
    │
    ├─► Intent Classification (System Layer)
    │
    ├─► Base Chat Path ───────────────────────────────────────────────┐
    │   ├─► web_search ──┐                                            │
    │   ├─► web_open_url │                                            │
    │   ├─► ipython ─────┼─► External Data/Computation                │
    │   ├─► memory_space─┤                                            │
    │   └─► datasources ─┘                                            │
    │                                                                 │
    └─► OK Computer Path ─────────────────────────────────────────────┤
        │                                                             │
        ├─► Skill Detection ──┐                                       │
        │   ├─► docx ─────────┼─► read_file(SKILL.md)                 │
        │   ├─► xlsx ─────────┤                                       │
        │   ├─► pdf ──────────┤                                       │
        │   └─► webapp ───────┘                                       │
        │                                                             │
        ├─► Tool Selection                                            │
        │   ├─► mshtools-read_file ◄─── Required first for skills     │
        │   ├─► mshtools-todo_read ──── Session state check           │
        │   └─► mshtools-todo_write ─── Task planning                 │
        │                                                             │
        ├─► Data Acquisition                                          │
        │   ├─► mshtools-web_search                                   │
        │   ├─► mshtools-get_data_source                              │
        │   ├─► mshtools-search_image_by_text                         │
        │   └─► mshtools-search_image_by_image                        │
        │                                                             │
        ├─► Browser Automation (if needed)                            │
        │   ├─► mshtools-browser_visit ◄─── Entry point               │
        │   ├─► mshtools-browser_click                                │
        │   ├─► mshtools-browser_find                                 │
        │   ├─► mshtools-browser_input                                │
        │   ├─► mshtools-browser_scroll_*                             │
        │   ├─► mshtools-browser_screenshot                           │
        │   └─► mshtools-browser_state                                │
        │                                                             │
        ├─► Content Generation                                        │
        │   ├─► mshtools-ipython ◄─────── Primary computation         │
        │   ├─► mshtools-write_file                                    │
        │   ├─► mshtools-edit_file                                     │
        │   └─► mshtools-shell ◄─────── Build orchestration           │
        │                                                             │
        ├─► Media Generation                                          │
        │   ├─► mshtools-generate_image                                │
        │   ├─► mshtools-generate_speech                               │
        │   └─► mshtools-generate_sound_effects                        │
        │                                                             │
        ├─► Asset Extraction (Web Replication)                        │
        │   ├─► mshtools-screenshot_web_full_page                      │
        │   ├─► mshtools-find_asset_bbox                               │
        │   └─► mshtools-crop_and_replicate_assets_in_image            │
        │                                                             │
        └─► Delivery                                                  │
            ├─► mshtools-deploy_website                                │
            ├─► mshtools-slides_generator                              │
            └─► KIMI_REF tags (automatic)                              │
```

## Skill-Specific Tool Chains

### DOCX Skill Tool Chain
```
read_file(SKILL.md) ─► read_file(Example.cs)
    │
    ▼
shell: ./docx init ──► Setup environment
    │
    ▼
ipython: Generate Program.cs ──► Meta-programming
    │
    ▼
shell: ./docx build ──► Compilation pipeline:
    ├─► dotnet build
    ├─► dotnet run
    ├─► python fix_element_order.py
    ├─► ./validator/Validator
    ├─► python validate_docx.py
    └─► pandoc verification
    │
    ▼
read_file(output.docx) ──► Verification
    │
    ▼
KIMI_REF output.docx
```

### XLSX Skill Tool Chain
```
read_file(SKILL.md)
    │
    ▼
Per-Sheet Loop:
    ├─► ipython: openpyxl creation
    ├─► ipython: wb.save()
    ├─► shell: KimiXlsx recheck ──┐
    ├─► shell: reference-check ───┤ Validation gates
    └─► Error? ──► Fix & retry ◄──┘
    │
    ▼
[If PivotTable needed]:
    ├─► shell: KimiXlsx pivot (MUST be last)
    │
    ▼
shell: KimiXlsx validate ──► Exit code 0 required
    │
    ▼
KIMI_REF output.xlsx
```

### PDF Skill Tool Chain (HTML Route)
```
read_file(SKILL.md) ─► read_file(routes/html.md)
    │
    ▼
ipython: Generate HTML + CSS
    ├─► matplotlib charts (if needed)
    └─► KaTeX math (if needed)
    │
    ▼
write_file: /tmp/input.html
    │
    ▼
shell: pdf.sh html input.html ──► Playwright + Paged.js
    ├─► Mermaid rendering (if present)
    ├─► Pagination stability detection
    └─► PDF export (scale: 1.5)
    │
    ▼
KIMI_REF output.pdf
```

### PDF Skill Tool Chain (LaTeX Route)
```
read_file(SKILL.md) ─► read_file(routes/latex.md)
    │
    ▼
ipython: Generate .tex source
    ├─► Document structure
    ├─► Math formulas
    └─► Bibliography (.bib)
    │
    ▼
write_file: /tmp/main.tex
    │
    ▼
shell: compile_latex.py main.tex --runs 2
    ├─► tectonic run 1 (generate aux)
    └─► tectonic run 2 (resolve references)
    │
    ▼
KIMI_REF output.pdf
```

### WebApp Skill Tool Chain
```
read_file(SKILL.md)
    │
    ▼
shell: init-webapp.sh "Title"
    ├─► Copy 73-file template
    └─► npm install (26,082 files)
    │
    ▼
ipython: Component architecture planning
    │
    ▼
write_file: src/components/*.tsx
    ├─► React components
    ├─► TypeScript types
    └─► shadcn/ui usage
    │
    ▼
shell: npm run build ──► Vite bundler:
    ├─► Tree-shaking
    ├─► Code splitting
    ├─► Asset optimization
    └─► dist/ generation
    │
    ▼
mshtools-deploy_website(dist)
    │
    ▼
Public URL returned
```

## Tool Synergy Patterns

### Pattern 1: Data Pipeline
```
get_data_source ──► ipython (pandas analysis) ──► write_file (CSV)
     │                                          │
     └─► Source citation                        └─► KIMI_REF
```

### Pattern 2: Web Research
```
web_search ──► browser_visit ──► browser_scroll ──► browser_screenshot
    │                                                  │
    └─► Initial discovery                              └─► Visual verification
```

### Pattern 3: Asset Extraction
```
screenshot_web_full_page ──► find_asset_bbox ──► crop_and_replicate
        │                          │                    │
        └─► Full page capture      └─► Detection        └─► Extraction
```

### Pattern 4: Media Production
```
generate_image ──► ipython (Pillow processing) ──► write_file
    │                                               │
    └─► Base image                                  └─► Final asset
```

### Pattern 5: Document Assembly
```
read_file (multiple) ──► ipython (analysis) ──► Skill-specific generation
        │                                         │
        └─► Source material                       └─► shell/ipython pipeline
                                                        │
                                                        ▼
                                                   KIMI_REF
```


