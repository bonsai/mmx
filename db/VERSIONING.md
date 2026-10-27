# MMX Improvement History - Naming Convention & Version Rules

## Version Naming: SemVer + Stage Suffix

```
v<MAJOR>.<MINOR>.<PATCH>[-<STAGE>[.<BUILD>]]

Examples:
  v1.0.0           - Initial release candidate
  v1.1.0-alpha.1   - Alpha build with colors
  v1.1.0           - Stable colored version
  v1.2.0-beta.1    - Beta with lighting fix
  v1.2.0           - Stable lighting fix
  v1.2.1           - Patch (camera distance tweak)
  v2.0.0           - Major: new geometry / pipeline rewrite
```

## Stage Definitions

| Stage | Meaning | Stability |
|-------|---------|-----------|
| `-alpha` | Internal testing, incomplete features | Unstable |
| `-beta` | Feature complete, needs review | Mostly stable |
| `-rc` | Release candidate, final QA | Stable |
| (none) | Production release | Stable |

## Version Bump Rules

| Change Type | Bump | Example |
|-------------|------|---------|
| Major geometry rewrite / pipeline overhaul | MAJOR | v1.x.x → v2.0.0 |
| New feature (camera system, materials, post-processing) | MINOR | v1.1.0 → v1.2.0 |
| Bug fix (lighting values, camera params, render settings) | PATCH | v1.2.0 → v1.2.1 |
| Experimental / WIP | + STAGE | v1.2.0-alpha.1 |

## Feedback-Driven Versioning

Each version **must** address feedback from previous version:

```
v1.0.0 (initial)
  ↓ VLM: "too dark, colors invisible" (sev 3)
v1.1.0 (colors added) 
  ↓ VLM: "still dark, lighting insufficient" (sev 3)
  ↓ USER: "camera too close, cluttered" (sev 2)
  ↓ USER: "geometry collapsing?" (sev 3)
v1.2.0 (lighting fixed, 5sec render)
  ↓ USER: "pull back camera, simplify composition"
  ↓ USER: "verify mesh integrity"
v1.3.0 (camera pulled back, mesh verified) ← NEXT
```

## Current History

| Version | Parent | Stage | Key Changes | Feedback Addressed |
|---------|--------|-------|-------------|---------------------|
| **v1.0.0** | — | stable | 10 STLs → assembly → decimate 5% (3171 verts). No materials. 15s render. | — |
| **v1.1.0** | v1.0.0 | stable | Applied 10 JAXA MMX materials from JSON. Same dark lighting. | — |
| **v1.2.0** | v1.1.0 | stable | **VLM-driven lighting fix**: sun 5→15, fill 0.5→3, rim 0→2, world 0.15→0.5. 5s render. | v1.1.0 VLM feedback (2 items) ✓ |
| **v1.3.0** | v1.2.0 | **planned** | Camera pull-back (orbit 25→45), mesh integrity check, wider lens | v1.2.0 USER feedback (2 items) |

## Feedback Tracking Schema

```sql
-- Each feedback item links to version where raised and version where fixed
feedback {
  version_id (where raised)
  source: user | vlm | llm
  category: lighting | color | camera | composition | geometry | performance
  severity: 1=minor, 2=major, 3=critical
  addressed: bool
  addressed_in_version: "v1.2.0"  -- NULL if not fixed
}
```

## Next Actions for v1.3.0

1. **Camera** (user/camera sev-2): Increase orbit distance 25→45, reduce orbits 2→1, lens 35→28mm
2. **Geometry** (user/geometry sev-3): Run mesh integrity check, verify decimate doesn't collapse parts
3. **Re-render** 5-10 sec test with new camera params
4. **VLM review** on v1.3.0 output

## Database

Location: `mmx_history.db` (SQLite)
Tables: `versions`, `lighting_configs`, `camera_configs`, `material_configs`, `feedback`, `review_sessions`

Query examples:
```sql
-- All feedback for a version
SELECT * FROM feedback WHERE version_id = (SELECT id FROM versions WHERE version = 'v1.2.0');

-- Open critical issues
SELECT f.*, v.version FROM feedback f JOIN versions v ON f.version_id = v.id 
WHERE f.severity = 3 AND f.addressed = 0;

-- Lighting evolution
SELECT v.version, l.sun_energy, l.fill_energy, l.rim_energy, l.world_strength
FROM versions v JOIN lighting_configs l ON v.id = l.version_id;
```