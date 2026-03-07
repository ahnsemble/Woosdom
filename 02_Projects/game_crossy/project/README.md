# Project Crossy Phase 0 - Documentation

## Project Structure
```
res://
├── scenes/
│   ├── main.tscn            # Entry point
│   ├── player/
│   │   └── player.tscn      # Player character
│   ├── chunks/              # Terrain slices
│   │   ├── chunk_grass.tscn
│   │   ├── chunk_road.tscn
│   │   ├── chunk_river.tscn
│   │   └── chunk_train.tscn
│   ├── obstacles/           # Spawntable objects
│   │   ├── car.tscn
│   │   ├── log.tscn
│   │   └── train.tscn
│   └── ui/
│       └── hud.tscn
├── scripts/
│   ├── Global.gd            # Autoload
│   ├── managers/            # Logic controllers
│   │   ├── GameManager.gd   # Autoload
│   │   ├── ChunkManager.gd
│   │   └── ObjectPool.gd
│   ├── player/
│   │   ├── PlayerController.gd
│   │   └── CameraFollow.gd
│   ├── chunks/
│   │   ├── ChunkBase.gd
│   │   ├── LaneMover.gd
│   │   └── TrainSpawner.gd
│   └── ui/
│       └── HUD.gd
└── assets/                  # (Empty for Phase 0)
```

## Scene Trees

### Main Scene
```
Main (Node3D)
├── WorldEnvironment
├── DirectionalLight3D
├── ChunkHolder (Node3D)
├── ChunkManager (Node) -> Script: ChunkManager.gd
├── Player (Area3D) -> Scene: player.tscn
├── Camera3D -> Script: CameraFollow.gd
└── HUD (CanvasLayer) -> Scene: hud.tscn
```

### Player Scene
```
Player (Area3D) -> Script: PlayerController.gd
├── CollisionShape3D
├── Visual (Node3D)
│   └── MeshInstance3D (Yellow Cube)
├── RayFront (RayCast3D)
├── RayBack (RayCast3D)
├── RayLeft (RayCast3D)
└── RayRight (RayCast3D)
```

### Chunk Scenes
**Road:**
```
ChunkRoad (Node3D) -> Script: ChunkBase.gd
├── Floor (MeshInstance3D)
└── LaneMover (Node3D) -> Script: LaneMover.gd
    └── (Spawns Car instances)
```

**River:**
```
ChunkRiver (Node3D) -> Script: ChunkBase.gd
├── WaterVisual (MeshInstance3D)
├── WaterArea (Area3D) -> Collision Layer: Water
└── LaneMover (Node3D) -> Script: LaneMover.gd
    └── (Spawns Log instances)
```

**Train:**
```
ChunkTrain (Node3D) -> Script: ChunkBase.gd
├── TrackVisual (MeshInstance3D)
└── TrainSpawner (Node3D) -> Script: TrainSpawner.gd
    ├── WarningLight (Node3D) -> Visible on warning
    └── (Spawns Train instance)
```
