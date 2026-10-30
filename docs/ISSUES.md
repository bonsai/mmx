# MMX Spacecraft STL Issue Report
Generated: Blender analysis (bpy)

## Summary
| Metric | Value |
|---|---|
| Total parts | 10 |
| Total facets | 82,305 |
| Total vertices | 4,789 |
| Non-manifold edges | 9,587 |
| Degenerate faces | 99 |
| Loose parts | Multiple per mesh |

## Per-Part Issues

### PAF_Stand (1_PAF)
- Non-manifold edges: 68
- Otherwise clean

### Propulsion_Lower (2_PropM)
- Non-manifold edges: 1,739
- Degenerate faces: 6
- Loose parts: 29

### Propulsion_Upper (3_PropM)
- Non-manifold edges: 1,581
- Degenerate faces: 4
- Loose parts: 49

### Return_Lower (4_ReturnM)
- Non-manifold edges: 279
- Degenerate faces: 16
- Loose parts: 66

### Return_Upper (5_RetunM)
- Non-manifold edges: 1,889 (highest)
- Degenerate faces: 15
- Loose parts: 70

### Exploration (6_ExplorationM)
- Non-manifold edges: 350
- Degenerate faces: 24
- Loose parts: 128

### LandingLeg_Normal (7_LandingLeg)
- Non-manifold edges: 267
- Loose parts: 166

### LandingLeg_P-SMP (8_LandingLeg)
- Non-manifold edges: 89
- Loose parts: 180

### SolarPaddle (9_SolarPaddle)
- Non-manifold edges: 1,546
- Degenerate faces: 24
- Loose parts: 197

### Miscellaneous (10_Misc)
- Non-manifold edges: 1,779
- Degenerate faces: 10
- Loose parts: 325 (highest fragmentation)

## Root Causes
1. Binary STL parsing creates disconnected face islands (loose parts)
2. Missing vertices at shared edges cause non-manifold geometry
3. Degenerate/zero-area triangles in binary STL encoding
4. No vertex merging (duplicate vertices) after parsing
