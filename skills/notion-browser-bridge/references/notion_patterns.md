# Notion Page Patterns

## Common Element Structures

### 1. Tables (Project Tracking)
Notion tables appear in snapshots as:
```
- table [ref=e67]:
  - rowgroup [ref=e68]:
    - row "Header Row" [disabled] [ref=e69]:
      - cell "Column 1" [ref=e70]
      - cell "Column 2" [ref=e73]
    - row "Data Row" [disabled] [ref=e79]:
      - cell "Data 1" [ref=e80]
      - cell "Data 2" [ref=e83]
```

**Pattern recognition:**
- Look for `table` elements
- Nested `rowgroup` contains rows
- Each row has cells with content
- Header rows often marked differently (first row)

**Example from MA Kooperation:**
- Columns: Arbeit, Kosten, Bonus
- Rows: Project entries with deadlines and costs

### 2. Numbered Lists
```
- generic [ref=e114]:
  - generic [ref=e116]: "1."
  - generic [ref=e119]: "Forschungkonzept MA-Thesis: Im Prozess"
```

**Pattern recognition:**
- Number + period as separate element
- Text content follows
- Often used for status tracking

### 3. Linked Pages
```
- link "Forschungskonzept_MA-Thesis.Duygu" [disabled] [ref=e126] [cursor=pointer]:
  - /url: /Forschungskonzept_MA-Thesis-Duygu-3165477ed8848060a16ad1a8a33e4a59?pvs=25
  - generic [ref=e129]:
    - img [ref=e132] (page icon)
    - generic [ref=e137]: Forschungskonzept_MA-Thesis.Duygu
```

**Pattern recognition:**
- `link` element with `[cursor=pointer]`
- Contains `/url:` with relative path
- Often has page icon image
- Text is the page title

### 4. Page Headers
```
- heading "MA Kooperation" [level=1] [ref=e50]
```

**Pattern recognition:**
- `heading` element with `level=1` for main title
- May have multiple heading levels for sections

## Interaction Patterns

### Clicking Links
```javascript
browser({
  action: "act",
  profile: "brave-remote",
  targetId: "TARGET_ID",
  request: {
    kind: "click",
    ref: "e126" // Link ref from snapshot
  }
})
```

**Wait for navigation:** After clicking, wait a moment before taking new snapshot.

### Reading Table Data
1. Find table element in snapshot
2. Extract rowgroup → rows → cells
3. Parse cell content (text may be in nested `generic` elements)
4. Map to structured data

### Handling Disabled Elements
Many Notion elements are marked `[disabled]` in snapshots. This is normal—they're still readable but not directly interactive via the snapshot refs. For typing/editing, you may need to find editable text areas.

## Notion-Specific Considerations

### 1. Page IDs
Notion URLs use 32-character hexadecimal IDs:
- `https://www.notion.so/MA-Kooperation-3165477ed88480cbbee8e7d1a91b50fe`
- Page ID: `3165477ed88480cbbee8e7d1a91b50fe`
- Subpage IDs follow same pattern

### 2. Query Parameters
Common parameters:
- `?pvs=25` - View settings
- `?pvs=4` - Different view
- Links may be relative (`/Forschungskonzept_MA-Thesis-Duygu-3165477ed8848060a16ad1a8a33e4a59`)

### 3. Authentication State
- Browser must be logged into Notion
- Session cookies persist in browser profile
- Private/incognito windows lose session on close

## Real-World Example: MA Kooperation Page

### Page Structure Observed:
1. **Header:** "MA Kooperation" (h1)
2. **Table:** 3 columns, 4 rows (header + 3 projects)
3. **Numbered List:** 3 items with status
4. **Linked Pages:** 2 subpage links

### Data Extraction Results:
```javascript
{
  projects: [
    {
      arbeit: "-Konzept MA Thesis (Kickoff) -Abgabe Anfang März 26",
      kosten: "100Fr. Auszahlung Anfang März",
      bonus: ""
    },
    {
      arbeit: "-Modul BA03 -Abgabe 2.7.2026",
      kosten: "Kick-off 300Fr Auszahlung Anfang März",
      bonus: "Abgabe 5+ = 300Fr & -5 200Fr."
    },
    {
      arbeit: "-MA-Thesis -Abgabe Anfang Dezember 26",
      kosten: "50Fr. Pro Seite ~ 100 Seiten Pro Monat 500Fr ab Ende März Aprox. 10 Monate",
      bonus: "Abgabe +5.5 = 500fr."
    }
  ],
  status: [
    "Forschungskonzept MA-Thesis: Im Prozess",
    "MA03 Qualitative Forschung: Pending",
    "MA-Thesis: Pending"
  ],
  subpages: [
    "Forschungskonzept_MA-Thesis.Duygu",
    "MA03 LNW Vorgabe 2026"
  ]
}
```

## Troubleshooting Specific to Notion

### Issue: Elements not interactive
**Cause:** Notion uses complex React components that may not expose standard interactive elements.
**Workaround:** Use `refs: "aria"` for better accessibility tree, or simulate clicks via coordinate targeting.

### Issue: Content loads dynamically
**Cause:** Notion loads content asynchronously.
**Workaround:** Add delays or wait for specific elements to appear before snapshot.

### Issue: Different page layouts
**Cause:** Notion pages are highly customizable.
**Solution:** Adapt parsing logic based on observed structure—no single pattern fits all pages.
