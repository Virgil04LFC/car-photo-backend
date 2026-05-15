# Background Spec — Car Photo App

This document defines the technical and visual requirements for all custom background images
used by the car photo background replacement pipeline.

Give this document to every designer commissioned to create backgrounds (Fiverr, etc.).
**All backgrounds must conform to this spec exactly.** Non-conforming deliveries will be rejected.

---

## Why the spec exists

The backend places the car cutout automatically using `verticalAlignment=bottom` and a
pre-configured `paddingBottom` value. This only works predictably if every background has
its floor line at the same position. Backgrounds that deviate from the floor-line rule will
produce cars that float or clip into the ground.

---

## Required Specifications

### Dimensions
| Property | Value |
|---|---|
| Aspect ratio | **16:9 exactly** |
| Minimum width | **2400 px** |
| Preferred width | **3840 px** (4K) |
| Height at 2400px | 1350 px |
| Height at 3840px | 2160 px |
| Colour space | sRGB |
| Format | JPEG (quality 92+) or PNG |
| EXIF rotation | Must be 0 (no rotation tag) |

### Floor Line — The Critical Rule
```
The floor-wall boundary must sit at exactly 35% from the bottom of the image.
```

In pixels:
- At 2400×1350: floor line = row **878** from top (472 px from bottom)
- At 3840×2160: floor line = row **1404** from top (756 px from bottom)

The **bottom 35%** of the image is the **placement zone** — the area where the car will sit.
The **top 65%** is the **scene zone** — walls, sky, architecture, background features.

> **Deliverable check:** Open the finished image, draw a horizontal guide at 35% from the
> bottom. The floor surface must be clearly visible below this line. The wall, ceiling, or
> background must be clearly visible above it.

### Floor Zone (bottom 35%) — Rules
- Must show only the **floor surface** (concrete, asphalt, tiles, etc.)
- **No furniture, props, vehicles, signs, or objects** in this zone
- Floor texture should be realistic and consistent
- Slight perspective foreshortening is fine (floor converges toward horizon)
- Floor lighting should be consistent with the scene lighting above

### Perspective
- Single-point perspective with vanishing point within the **middle horizontal third**
- Horizon line between **25–40% from the top** of the image
- Symmetrical left/right (no strong off-axis angles)

### Lighting
- Overhead or slightly front-left direction preferred
- Consistent with where an AI shadow under the car would fall (toward the viewer)
- Avoid strong single-source side lighting that would conflict with the car shadow

### What to avoid
- Logos, text, branding, watermarks
- Reflections of other vehicles on the floor
- Objects that would overlap with where the car will be placed
- Strong vignetting at the bottom edge
- JPEG artefacts, visible compression blocks

---

## Metadata to supply with each background

When delivering a background, the designer must also confirm:

| Field | Description | Example |
|---|---|---|
| `id` | Kebab-case identifier | `city-rooftop` |
| `name` | Display name for the app picker | `City Rooftop` |
| `description` | One-line buyer-facing description | `Downtown rooftop at dusk — suits sports cars and EVs` |
| `scene_type` | `interior` or `exterior` | `exterior` |
| `floor_y_from_bottom` | Measured floor-line position (should be ~0.35) | `0.35` |
| `preview_color` | Dominant hex colour for app tile swatch | `#2A3A52` |

---

## Floor Line Reference Diagram

```
┌──────────────────────────────────────────────────────┐  ← top of image (0%)
│                                                      │
│                  SCENE ZONE (65%)                    │
│        walls · sky · architecture · features         │
│                                                      │
│                                                      │
├──────────────────────────────────────────────────────┤  ← floor line (35% from bottom)
│                                                      │
│               PLACEMENT ZONE (35%)                   │
│              floor surface only                      │
│                                                      │
└──────────────────────────────────────────────────────┘  ← bottom of image (0%)
```

The car cutout will be composited so its wheel contact points land just above the bottom
of the placement zone, with the car body extending upward into the scene zone.

---

## Existing Backgrounds (pre-spec, measured values)

These were created before this spec existed. Floor lines were measured using PIL analysis.

| ID | Floor line (measured) | Placement paddingBottom |
|---|---|---|
| `industrial-garage` | 70% from bottom (large warehouse floor) | 0.10 |
| `white-studio` | 35% from bottom (seamless cyc) | 0.08 |

New commissioned backgrounds should all target 35% from bottom and use `paddingBottom: 0.10`.

---

## Fiverr Brief Template

> **What I need:** A high-quality photorealistic background image for automotive photography.
> A car cutout will be composited onto this background automatically, so the image must follow
> exact technical rules (attached spec). The floor line must be at exactly 35% from the bottom.
> Deliver as JPEG, 3840×2160px, sRGB. See BACKGROUND_SPEC.md for full requirements.

---

*Last updated: 2026-05-15*
