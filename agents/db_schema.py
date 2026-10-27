"""
MMX Improvement History Database Schema
Tracks: versions, renders, VLM/LLM/User feedback, camera params, lighting configs
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum

DB_PATH = Path(__file__).parent.parent / "mmx_history.db"

class FeedbackSource(Enum):
    USER = "user"
    VLM = "vlm"
    LLM = "llm"

class FeedbackCategory(Enum):
    LIGHTING = "lighting"
    COLOR = "color"
    CAMERA = "camera"
    COMPOSITION = "composition"
    GEOMETRY = "geometry"
    PERFORMANCE = "performance"
    OTHER = "other"

class VersionStatus(Enum):
    DRAFT = "draft"
    RENDERED = "rendered"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"

@dataclass
class Version:
    id: Optional[int] = None
    version: str = ""
    parent_version: Optional[str] = None
    description: str = ""
    status: str = VersionStatus.DRAFT.value
    created_at: str = ""
    updated_at: str = ""
    blender_file: str = ""
    render_output: str = ""
    video_file: str = ""
    glb_file: str = ""
    frame_count: int = 0
    fps: int = 30
    duration_sec: float = 0.0
    resolution_x: int = 1280
    resolution_y: int = 720
    engine: str = "EEVEE"
    samples: int = 16
    commit_hash: str = ""

@dataclass
class LightingConfig:
    id: Optional[int] = None
    version_id: int = 0
    sun_energy: float = 5.0
    sun_color: str = "[1.0, 0.95, 0.9]"
    sun_angle: float = 0.53
    fill_energy: float = 0.5
    fill_color: str = "[0.3, 0.4, 0.6]"
    rim_energy: float = 0.0
    rim_color: str = "[0.2, 0.3, 0.5]"
    world_strength: float = 0.15
    world_star_density: float = 0.95
    exposure: float = 1.0

@dataclass
class CameraConfig:
    id: Optional[int] = None
    version_id: int = 0
    lens_mm: float = 35.0
    clip_start: float = 0.1
    clip_end: float = 1000.0
    orbit_distance: float = 25.0
    orbit_height: float = 8.0
    orbits_per_animation: float = 2.0
    vertical_oscillation: float = 5.0
    follow_offset_y: float = -15.0
    follow_offset_z: float = 0.0

@dataclass
class MaterialConfig:
    id: Optional[int] = None
    version_id: int = 0
    part_name: str = ""
    base_color: str = ""
    metallic: float = 0.0
    roughness: float = 0.5
    emission_color: str = "[0, 0, 0]"
    emission_strength: float = 0.0

@dataclass
class Feedback:
    id: Optional[int] = None
    version_id: int = 0
    source: str = FeedbackSource.USER.value
    category: str = FeedbackCategory.OTHER.value
    severity: int = 1
    title: str = ""
    description: str = ""
    suggestion: str = ""
    addressed: bool = False
    addressed_in_version: Optional[str] = None
    created_at: str = ""

@dataclass
class ReviewSession:
    id: Optional[int] = None
    version_id: int = 0
    vlm_model: str = ""
    frames_reviewed: str = ""
    summary: str = ""
    overall_score: float = 0.0
    created_at: str = ""

class HistoryDB:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    parent_version TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    blender_file TEXT,
                    render_output TEXT,
                    video_file TEXT,
                    glb_file TEXT,
                    frame_count INTEGER DEFAULT 0,
                    fps INTEGER DEFAULT 30,
                    duration_sec REAL DEFAULT 0.0,
                    resolution_x INTEGER DEFAULT 1280,
                    resolution_y INTEGER DEFAULT 720,
                    engine TEXT DEFAULT 'EEVEE',
                    samples INTEGER DEFAULT 16,
                    commit_hash TEXT
                );
                
                CREATE TABLE IF NOT EXISTS lighting_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    sun_energy REAL DEFAULT 5.0,
                    sun_color TEXT,
                    sun_angle REAL DEFAULT 0.53,
                    fill_energy REAL DEFAULT 0.5,
                    fill_color TEXT,
                    rim_energy REAL DEFAULT 0.0,
                    rim_color TEXT,
                    world_strength REAL DEFAULT 0.15,
                    world_star_density REAL DEFAULT 0.95,
                    exposure REAL DEFAULT 1.0,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                );
                
                CREATE TABLE IF NOT EXISTS camera_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    lens_mm REAL DEFAULT 35.0,
                    clip_start REAL DEFAULT 0.1,
                    clip_end REAL DEFAULT 1000.0,
                    orbit_distance REAL DEFAULT 25.0,
                    orbit_height REAL DEFAULT 8.0,
                    orbits_per_animation REAL DEFAULT 2.0,
                    vertical_oscillation REAL DEFAULT 5.0,
                    follow_offset_y REAL DEFAULT -15.0,
                    follow_offset_z REAL DEFAULT 0.0,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                );
                
                CREATE TABLE IF NOT EXISTS material_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    part_name TEXT NOT NULL,
                    base_color TEXT,
                    metallic REAL DEFAULT 0.0,
                    roughness REAL DEFAULT 0.5,
                    emission_color TEXT,
                    emission_strength REAL DEFAULT 0.0,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                );
                
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity INTEGER DEFAULT 1,
                    title TEXT NOT NULL,
                    description TEXT,
                    suggestion TEXT,
                    addressed BOOLEAN DEFAULT 0,
                    addressed_in_version TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                );
                
                CREATE TABLE IF NOT EXISTS review_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    vlm_model TEXT,
                    frames_reviewed TEXT,
                    summary TEXT,
                    overall_score REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_feedback_version ON feedback(version_id);
                CREATE INDEX IF NOT EXISTS idx_feedback_source ON feedback(source);
                CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category);
            """)
    
    def create_version(self, v: Version) -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO versions (version, parent_version, description, status, created_at, updated_at,
                    blender_file, render_output, video_file, glb_file, frame_count, fps, duration_sec,
                    resolution_x, resolution_y, engine, samples, commit_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (v.version, v.parent_version, v.description, v.status, now, now,
                v.blender_file, v.render_output, v.video_file, v.glb_file, v.frame_count, v.fps, v.duration_sec,
                v.resolution_x, v.resolution_y, v.engine, v.samples, v.commit_hash))
            return cur.lastrowid
    
    def add_lighting(self, l: LightingConfig):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO lighting_configs (version_id, sun_energy, sun_color, sun_angle, fill_energy, fill_color,
                    rim_energy, rim_color, world_strength, world_star_density, exposure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (l.version_id, l.sun_energy, l.sun_color, l.sun_angle, l.fill_energy, l.fill_color,
                l.rim_energy, l.rim_color, l.world_strength, l.world_star_density, l.exposure))
    
    def add_camera(self, c: CameraConfig):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO camera_configs (version_id, lens_mm, clip_start, clip_end, orbit_distance, orbit_height,
                    orbits_per_animation, vertical_oscillation, follow_offset_y, follow_offset_z)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (c.version_id, c.lens_mm, c.clip_start, c.clip_end, c.orbit_distance, c.orbit_height,
                c.orbits_per_animation, c.vertical_oscillation, c.follow_offset_y, c.follow_offset_z))
    
    def add_material(self, m: MaterialConfig):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO material_configs (version_id, part_name, base_color, metallic, roughness,
                    emission_color, emission_strength)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (m.version_id, m.part_name, m.base_color, m.metallic, m.roughness,
                m.emission_color, m.emission_strength))
    
    def add_feedback(self, f: Feedback) -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO feedback (version_id, source, category, severity, title, description, suggestion,
                    addressed, addressed_in_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f.version_id, f.source, f.category, f.severity, f.title, f.description, f.suggestion,
                f.addressed, f.addressed_in_version, now))
            return cur.lastrowid
    
    def add_review_session(self, r: ReviewSession) -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO review_sessions (version_id, vlm_model, frames_reviewed, summary, overall_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (r.version_id, r.vlm_model, r.frames_reviewed, r.summary, r.overall_score, now))
            return cur.lastrowid
    
    def get_version(self, version: str) -> Optional[Version]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM versions WHERE version = ?", (version,)).fetchone()
            return Version(**dict(row)) if row else None
    
    def get_feedback_for_version(self, version_id: int) -> List[Feedback]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM feedback WHERE version_id = ? ORDER BY severity DESC", (version_id,)).fetchall()
            return [Feedback(**dict(row)) for row in rows]
    
    def get_history(self) -> List[Version]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM versions ORDER BY created_at DESC").fetchall()
            return [Version(**dict(row)) for row in rows]
    
    def link_feedback_to_version(self, feedback_id: int, fixed_version: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE feedback SET addressed = 1, addressed_in_version = ? WHERE id = ?", (fixed_version, feedback_id))

# Demo: Populate with current history
if __name__ == "__main__":
    db = HistoryDB()
    
    # v1.0.0 - Initial assembly (no colors, dark)
    v1 = Version(
        version="v1.0.0",
        description="Initial MMX assembly from 10 STLs. Combined, decimated to 5% (3171 verts). No materials. Dark render.",
        status=VersionStatus.RENDERED.value,
        blender_file="models/mmx_lowpoly.blend",
        render_output="renders/",
        video_file="MMX_space_flight_15sec.mp4",
        frame_count=450,
        fps=30,
        duration_sec=15.0,
        commit_hash="d9c55d9"
    )
    v1_id = db.create_version(v1)
    
    db.add_lighting(LightingConfig(version_id=v1_id, sun_energy=5.0, fill_energy=0.5, world_strength=0.15))
    db.add_camera(CameraConfig(version_id=v1_id, orbit_distance=30, orbits_per_animation=2.5))
    
    # v1.1.0 - Colors applied (still dark)
    v11 = Version(
        version="v1.1.0",
        parent_version="v1.0.0",
        description="Applied JAXA MMX colors from JSON config (10 materials). Still dark rendering.",
        status=VersionStatus.RENDERED.value,
        blender_file="models/mmx_colored_lowpoly.blend",
        frame_count=450,
        duration_sec=15.0,
        commit_hash="1ffc9af"
    )
    v11_id = db.create_version(v11)
    
    db.add_lighting(LightingConfig(version_id=v11_id, sun_energy=5.0, fill_energy=0.5, world_strength=0.15))
    db.add_camera(CameraConfig(version_id=v11_id, orbit_distance=30, orbits_per_animation=2.5))
    
    # VLM Feedback on v1.1.0
    db.add_feedback(Feedback(
        version_id=v11_id, source=FeedbackSource.VLM.value, category=FeedbackCategory.LIGHTING.value,
        severity=3, title="Under-exposed render",
        description="Spacecraft barely visible. Colors not distinguishable. Starfield too faint.",
        suggestion="Increase sun energy to 10-15, add fill/rim lights, boost world background strength"
    ))
    db.add_feedback(Feedback(
        version_id=v11_id, source=FeedbackSource.VLM.value, category=FeedbackCategory.COLOR.value,
        severity=2, title="Color scheme not visible",
        description="White thermal blankets, red propulsion, blue solar panels, gray structure all appear gray/black",
        suggestion="Verify material emission, increase lighting, check color values"
    ))
    
    # v1.2.0 - Lighting fixed per VLM
    v12 = Version(
        version="v1.2.0",
        parent_version="v1.1.0",
        description="Lighting overhaul per VLM feedback: sun 15.0, fill 3.0, rim 2.0, world 0.5. 5-second render.",
        status=VersionStatus.RENDERED.value,
        blender_file="models/mmx_animation_5sec.blend",
        render_output="renders5/",
        video_file="MMX_space_flight_5sec.mp4",
        frame_count=150,
        fps=30,
        duration_sec=5.0,
        commit_hash="pending"
    )
    v12_id = db.create_version(v12)
    
    db.add_lighting(LightingConfig(
        version_id=v12_id, sun_energy=15.0, fill_energy=3.0, rim_energy=2.0, world_strength=0.5,
        sun_color="[1.0, 0.95, 0.9]", fill_color="[0.3, 0.4, 0.6]", rim_color="[0.2, 0.3, 0.5]"
    ))
    db.add_camera(CameraConfig(version_id=v12_id, orbit_distance=25, orbits_per_animation=2.0))
    
    # Link VLM feedback as addressed
    db.link_feedback_to_version(1, "v1.2.0")
    db.link_feedback_to_version(2, "v1.2.0")
    
    # User feedback on v1.2.0
    db.add_feedback(Feedback(
        version_id=v12_id, source=FeedbackSource.USER.value, category=FeedbackCategory.CAMERA.value,
        severity=2, title="Camera too close / cluttered",
        description="引いてほしい画角、ごちゃごちゃしてる - camera distance too close, composition cluttered",
        suggestion="Increase orbit distance to 40-50, reduce orbits to 1, wider lens (24-28mm)"
    ))
    db.add_feedback(Feedback(
        version_id=v12_id, source=FeedbackSource.USER.value, category=FeedbackCategory.GEOMETRY.value,
        severity=3, title="Possible mesh collapse?",
        description="崩壊してる？？ - geometry may be breaking up during decimation/animation",
        suggestion="Check vertex positions, verify decimate ratio, inspect mesh integrity"
    ))
    
    print("Database initialized at", DB_PATH)
    print("\nVersions:")
    for v in db.get_history():
        print(f"  {v.version} ({v.status}) - {v.description[:60]}...")
    
    print("\nFeedback:")
    for v in db.get_history():
        fb = db.get_feedback_for_version(v.id if hasattr(v, 'id') else 0)
        for f in fb:
            print(f"  [{v.version}] {f.source}/{f.category} sev={f.severity}: {f.title}")