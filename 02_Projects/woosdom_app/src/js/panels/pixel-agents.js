// ─── panels/pixel-agents.js — Canvas renderer for Pixel Agents HQ ───────────
// Sprite sheet : assets/32x32folk.png  (384x256 — 12 cols x 8 rows, 32px/tile)
// Tileset      : assets/gentle-obj.png (1440x1024 — 45 cols x 32 rows, 32px/tile)
// Credits      : a16z-infra/ai-town (MIT License)
(function initPixelAgentsHQ() {
  'use strict';
  var canvas = document.getElementById('agentCanvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var W = 760, H = 420;

  // ── Data from canvas attributes ──────────────────────────────────────────────
  var TEAM_STATUS = {brain:'idle', cc:'idle', codex:'idle', ag:'idle'};
  var AGENT_TASKS = {};
  var AGENT_LOGS  = [];
  try {
    TEAM_STATUS = JSON.parse(canvas.dataset.teamStatus || '{}');
    AGENT_TASKS = JSON.parse(canvas.dataset.agentTasks  || '{}');
    AGENT_LOGS  = JSON.parse(canvas.dataset.agentLogs   || '[]');
  } catch(e) {}

  // ── Bug 1 fix: status normalisation ──────────────────────────────────────────
  // Ensures only known status values reach the renderer regardless of data source.
  function normalizeStatus(val) {
    var s = (val || '').toLowerCase();
    if (s === 'active')        return 'active';
    if (s === 'done')          return 'done';
    if (s === 'error')         return 'error';
    if (s === 'communicating') return 'communicating';
    if (s === 'meeting')       return 'meeting';
    return 'idle';
  }

  // ── Sprite sheet: assets/32x32folk.png (384x256, 12 cols x 8 rows, 32px/tile)
  // charIdx 0-3 → rows 0-3; charIdx 4-7 → rows 4-7
  // Per char: cols = (charIdx%4)*3 .. +2; rows: down=+0, left=+1, right=+2, up=+3
  var SS = {img:null, ok:false};
  var ssImg = new Image();
  ssImg.onload  = function() { SS.img = ssImg; SS.ok = true; };
  ssImg.onerror = function() { SS.ok = false; };
  ssImg.src = 'assets/32x32folk.png';

  // ── Tileset: assets/gentle-obj.png (1440x1024, 45 cols x 32 rows, 32px/tile)
  // Tile ID = row * 45 + col;  srcX = (id%45)*32;  srcY = floor(id/45)*32
  // ── Tile Reference (PIL verified from gentle-obj.png) ──────────────────────
  // 406,407,451,452 = dark blue-teal indoor floor (row9-10, avg rgb(24,63,76))
  // 499,544,589,634 = gradient dark blue floor   (row11-14, rgb(24-29,32-76,64-80))
  // 675,676,631,632 = golden-brown carpet/rug     (row14-15, rgb(97-165,71-120,36-37))
  // 586,587         = red-brown carpet             (row13, rgb(58-82,31-52,31-46))
  // 319,320         = dark green-gray stone         (row7, rgb(54-67,69-75,63-65))
  // 405,408         = warm brown building edge      (row9, rgb(105-111,96-101,51-52))
  // 360,363,450,453 = olive/tan border             (row8-10)
  // 271             = GREEN grass — OUTDOOR ONLY, not for rooms!
  var TS = {img:null, ok:false};
  var tsImg = new Image();
  tsImg.onload  = function() { TS.img = tsImg; TS.ok = true; };
  tsImg.onerror = function() { TS.ok = false; };
  tsImg.src = 'assets/gentle-obj.png';
  var TS_COLS = 45, TS_SZ = 32;

  // ── Room definitions ──────────────────────────────────────────────────────────
  // tiles: 4 IDs for 2x2 checkerboard floor pattern [col0row0, col1row0, col0row1, col1row1]
  // wallTile: single tile ID for the 20px header strip
  // tint: colour overlay that gives each room its identity at low opacity
  var ROOMS = {
    cc:    {name:'CC Room',    x:10,  y:10,  w:235, h:235,
            bg:'#0d1b2e', border:'#4a9eff',
            tiles:[406,407,451,452], wallTile:405,
            tint:'rgba(26,60,110,0.25)'},
    codex: {name:'Codex Room', x:255, y:10,  w:240, h:235,
            bg:'#0a2a1a', border:'#00b894',
            tiles:[499,544,589,634], wallTile:408,
            tint:'rgba(10,80,50,0.25)'},
    ag:    {name:'AG Room',    x:505, y:10,  w:245, h:235,
            bg:'#2a1006', border:'#e17055',
            tiles:[675,676,631,632], wallTile:360,
            tint:'rgba(90,40,10,0.25)'},
    brain: {name:'Brain HQ',   x:10,  y:255, w:740, h:155,
            bg:'#16082e', border:'#a29bfe',
            tiles:[586,587,319,320], wallTile:450,
            tint:'rgba(55,20,100,0.25)'},
  };

  // ── Pre-rendered room backgrounds (offscreen canvas per room) ─────────────────
  // Computed once when tileset loads; then blit every frame via drawImage (fast).
  var ROOM_BG = {};
  var bgRendered = false;

  function prerenderRooms() {
    if (bgRendered || !TS.ok || !TS.img) return;
    // Bug 5 fix: wrap in try-catch so a partial draw failure doesn't freeze bgRendered=true
    try {
      Object.keys(ROOMS).forEach(function(key) {
        var room = ROOMS[key];
        var oc = document.createElement('canvas');
        oc.width = room.w; oc.height = room.h;
        var oc2 = oc.getContext('2d');
        oc2.imageSmoothingEnabled = false;

        // Solid colour base (shows through transparent tile regions)
        oc2.fillStyle = room.bg;
        oc2.fillRect(0, 0, room.w, room.h);

        // Floor tiles — 2x2 checkerboard starting below header strip (y=20)
        var WALL_H = 20;
        for (var ty = WALL_H; ty < room.h + TS_SZ; ty += TS_SZ) {
          for (var tx = 0; tx < room.w + TS_SZ; tx += TS_SZ) {
            var col = Math.floor(tx / TS_SZ) % 2;
            var row = Math.floor((ty - WALL_H) / TS_SZ) % 2;
            var tid = room.tiles[col + row * 2];
            var sx  = (tid % TS_COLS) * TS_SZ;
            var sy  = Math.floor(tid / TS_COLS) * TS_SZ;
            oc2.drawImage(TS.img, sx, sy, TS_SZ, TS_SZ, tx, ty, TS_SZ, TS_SZ);
          }
        }

        // Wall strip tiles along top 20px
        var wtid = room.wallTile;
        var wsx = (wtid % TS_COLS) * TS_SZ, wsy = Math.floor(wtid / TS_COLS) * TS_SZ;
        for (var wx = 0; wx < room.w + TS_SZ; wx += TS_SZ) {
          oc2.drawImage(TS.img, wsx, wsy, TS_SZ, TS_SZ, wx, 0, TS_SZ, WALL_H);
        }
        // Darken wall strip for depth
        oc2.fillStyle = 'rgba(0,0,0,0.40)';
        oc2.fillRect(0, 0, room.w, WALL_H);

        // Colour identity tint over the whole room
        oc2.fillStyle = room.tint;
        oc2.fillRect(0, 0, room.w, room.h);

        ROOM_BG[key] = oc;
      });
      bgRendered = true;
    } catch(e) {
      console.warn('[PixelAgents] prerenderRooms failed, will retry:', e);
      // bgRendered stays false → retry on next frame
    }
  }

  // ── Desk positions (absolute canvas coords) ───────────────────────────────────
  var DESKS = {
    cc:    [[60,90],[127,90],[192,90],[60,175],[127,175]],
    codex: [[300,90],[380,90],[300,175],[380,175]],
    ag:    [[545,90],[620,90],[545,175],[620,175]],
    brain: [[385,330]],
  };

  // ── Agent definitions ─────────────────────────────────────────────────────────
  var AGENT_DEFS = [
    {id:'Foreman',      emoji:'👔', team:'cc',    charIdx:0, roomId:'cc',    di:0, leader:true, color:'#4a9eff'},
    {id:'Engineer',     emoji:'⌨',  team:'cc',    charIdx:1, roomId:'cc',    di:1,              color:'#74b9ff'},
    {id:'Critic',       emoji:'🔍', team:'cc',    charIdx:2, roomId:'cc',    di:2,              color:'#74b9ff'},
    {id:'GitOps',       emoji:'📤', team:'cc',    charIdx:3, roomId:'cc',    di:3,              color:'#74b9ff'},
    {id:'VaultKeeper',  emoji:'🗄', team:'cc',    charIdx:4, roomId:'cc',    di:4,              color:'#74b9ff'},
    {id:'Compute Lead', emoji:'👔', team:'codex', charIdx:5, roomId:'codex', di:0, leader:true, color:'#00b894'},
    {id:'Quant',        emoji:'🧮', team:'codex', charIdx:6, roomId:'codex', di:1,              color:'#55efc4'},
    {id:'Backtester',   emoji:'📊', team:'codex', charIdx:7, roomId:'codex', di:2,              color:'#55efc4'},
    {id:'Builder',      emoji:'🔨', team:'codex', charIdx:0, roomId:'codex', di:3,              color:'#55efc4'},
    {id:'Scout Lead',   emoji:'👔', team:'ag',    charIdx:1, roomId:'ag',    di:0, leader:true, color:'#e17055'},
    {id:'Web Scout',    emoji:'🔍', team:'ag',    charIdx:2, roomId:'ag',    di:1,              color:'#fab1a0'},
    {id:'Architect',    emoji:'🏗', team:'ag',    charIdx:3, roomId:'ag',    di:2,              color:'#fab1a0'},
    {id:'Experimenter', emoji:'🧪', team:'ag',    charIdx:4, roomId:'ag',    di:3,              color:'#fab1a0'},
    {id:'Brain',        emoji:'🧠', team:'brain', charIdx:5, roomId:'brain', di:0, leader:true, color:'#a29bfe'},
  ];

  // Map fictional team → real dashboard agent key for task text
  var TEAM_REAL = {cc:'Hands-4', codex:'Hands-3', ag:'Hands-1', brain:'Brain'};

  // Room key → engine aliases used in parsed logs
  var ROOM_ENGINES = {
    cc: ['claude_code', 'Hands-4', 'CC팀'],
    codex: ['codex', 'Codex', 'Hands-3'],
    ag: ['antigravity', 'Antigravity', 'Hands-1', 'Hands-2'],
    brain: ['Brain']
  };

  // ── A* Pathfinding Grid (full canvas, half-tile resolution) ──────────────────
  var CELL = 16;
  var GRID_W = Math.ceil(W / CELL);  // 48
  var GRID_H = Math.ceil(H / CELL);  // 27
  var WALL_H = 20;
  var GRID = [];  // GRID[gx][gy] = 0 (walkable) or 1 (blocked)

  function buildGrid() {
    var g = [];
    for (var gx = 0; gx < GRID_W; gx++) {
      g[gx] = [];
      for (var gy = 0; gy < GRID_H; gy++) {
        g[gx][gy] = 1; // default blocked (canvas background)
      }
    }
    // Mark room interiors as walkable (below wall header)
    Object.keys(ROOMS).forEach(function(k) {
      var r = ROOMS[k];
      var gx0 = Math.floor(r.x / CELL);
      var gy0 = Math.floor((r.y + WALL_H) / CELL);
      var gx1 = Math.floor((r.x + r.w) / CELL);
      var gy1 = Math.floor((r.y + r.h) / CELL);
      for (var gx = gx0; gx < gx1; gx++) {
        for (var gy = gy0; gy < gy1; gy++) {
          if (gx >= 0 && gx < GRID_W && gy >= 0 && gy < GRID_H) g[gx][gy] = 0;
        }
      }
    });
    // Mark hallway between rooms as walkable (the gap between top rooms and Brain HQ)
    // Top rooms end at y=245, Brain starts at y=255, gap y=245-255
    var hallY0 = Math.floor(245 / CELL);
    var hallY1 = Math.ceil(255 / CELL);
    for (var gx = Math.floor(10 / CELL); gx < Math.ceil(750 / CELL); gx++) {
      for (var gy = hallY0; gy <= hallY1; gy++) {
        if (gx >= 0 && gx < GRID_W && gy >= 0 && gy < GRID_H) g[gx][gy] = 0;
      }
    }
    // Also make gaps between top rooms walkable (cc→codex→ag transitions)
    // cc ends at x=245, codex starts at x=255 → gap x=245-255
    // codex ends at x=495, ag starts at x=505 → gap x=495-505
    var gaps = [[245,255],[495,505]];
    gaps.forEach(function(gap) {
      var gapX0 = Math.floor(gap[0] / CELL);
      var gapX1 = Math.ceil(gap[1] / CELL);
      for (var gx = gapX0; gx <= gapX1; gx++) {
        for (var gy = Math.floor(30 / CELL); gy < Math.ceil(245 / CELL); gy++) {
          if (gx >= 0 && gx < GRID_W && gy >= 0 && gy < GRID_H) g[gx][gy] = 0;
        }
      }
    });
    // Mark desk positions as blocked (agents walk around desks)
    Object.keys(DESKS).forEach(function(rid) {
      DESKS[rid].forEach(function(d) {
        var dgx = Math.floor(d[0] / CELL);
        var dgy = Math.floor(d[1] / CELL);
        // Block desk area (2 cells wide, 1 tall for monitor + desk)
        for (var ox = -1; ox <= 1; ox++) {
          for (var oy = -1; oy <= 0; oy++) {
            var bx = dgx + ox, by = dgy + oy;
            if (bx >= 0 && bx < GRID_W && by >= 0 && by < GRID_H) g[bx][by] = 1;
          }
        }
      });
    });
    GRID = g;
  }
  buildGrid();

  // A* pathfinding — returns array of {x,y} canvas coords, or null
  function findPath(sx, sy, ex, ey) {
    var sgx = Math.floor(sx / CELL), sgy = Math.floor(sy / CELL);
    var egx = Math.floor(ex / CELL), egy = Math.floor(ey / CELL);
    // Clamp to grid
    sgx = Math.max(0, Math.min(GRID_W - 1, sgx));
    sgy = Math.max(0, Math.min(GRID_H - 1, sgy));
    egx = Math.max(0, Math.min(GRID_W - 1, egx));
    egy = Math.max(0, Math.min(GRID_H - 1, egy));
    // If start or end is blocked, find nearest walkable cell
    if (GRID[sgx][sgy] === 1) {
      var ns = nearestWalkable(sgx, sgy);
      if (!ns) return null;
      sgx = ns[0]; sgy = ns[1];
    }
    if (GRID[egx][egy] === 1) {
      var ne = nearestWalkable(egx, egy);
      if (!ne) return null;
      egx = ne[0]; egy = ne[1];
    }
    if (sgx === egx && sgy === egy) return [{x: egx * CELL + CELL / 2, y: egy * CELL + CELL / 2}];

    // A* with Manhattan heuristic
    var open = [{gx:sgx, gy:sgy, g:0, f:0, parent:null}];
    var closed = {};
    var key = function(gx, gy) { return gx + ',' + gy; };
    closed[key(sgx, sgy)] = true;
    var dirs = [[0,-1],[0,1],[-1,0],[1,0]]; // up,down,left,right
    var maxIter = 800;

    while (open.length > 0 && maxIter-- > 0) {
      // Find lowest f in open list
      var bestIdx = 0;
      for (var i = 1; i < open.length; i++) {
        if (open[i].f < open[bestIdx].f) bestIdx = i;
      }
      var cur = open.splice(bestIdx, 1)[0];

      if (cur.gx === egx && cur.gy === egy) {
        // Reconstruct path
        var path = [];
        var node = cur;
        while (node) {
          path.unshift({x: node.gx * CELL + CELL / 2, y: node.gy * CELL + CELL / 2});
          node = node.parent;
        }
        return path;
      }

      for (var d = 0; d < 4; d++) {
        var ngx = cur.gx + dirs[d][0], ngy = cur.gy + dirs[d][1];
        if (ngx < 0 || ngx >= GRID_W || ngy < 0 || ngy >= GRID_H) continue;
        if (GRID[ngx][ngy] === 1) continue;
        var nk = key(ngx, ngy);
        if (closed[nk]) continue;
        closed[nk] = true;
        var ng = cur.g + 1;
        var nh = Math.abs(ngx - egx) + Math.abs(ngy - egy);
        open.push({gx:ngx, gy:ngy, g:ng, f:ng + nh, parent:cur});
      }
    }
    return null; // no path found
  }

  function nearestWalkable(gx, gy) {
    for (var r = 1; r < 10; r++) {
      for (var dx = -r; dx <= r; dx++) {
        for (var dy = -r; dy <= r; dy++) {
          if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue;
          var nx = gx + dx, ny = gy + dy;
          if (nx >= 0 && nx < GRID_W && ny >= 0 && ny < GRID_H && GRID[nx][ny] === 0) {
            return [nx, ny];
          }
        }
      }
    }
    return null;
  }

  // ── Sprite / animation constants ──────────────────────────────────────────────
  var DIR_ROW   = {down:0, left:1, right:2, up:3};
  var SPRITE_SZ = 28;
  var SPEED     = 0.33;  // idle wander speed
  var ANIM_RATE = 8;
  var tick      = 0;

  // ── Per-agent runtime state ───────────────────────────────────────────────────
  var STATE = {};
  AGENT_DEFS.forEach(function(def) {
    var desks = DESKS[def.roomId] || [];
    var room  = ROOMS[def.roomId];
    // Bug 3 fix: fallback to room centre instead of hard-coded Brain HQ position
    var deskFallbackX = Math.round(room.x + room.w / 2);
    var deskFallbackY = Math.round(room.y + room.h * 0.6);
    var desk  = desks[def.di] || [deskFallbackX, deskFallbackY];
    var ix = room.x + 24 + Math.random() * (room.w - 48);
    var iy = room.y + 32 + Math.random() * (room.h - 56);
    STATE[def.id] = {
      x:ix, y:iy, tx:ix, ty:iy,
      deskX:desk[0], deskY:desk[1],
      dir:'down', frame:0, fTimer:0,
      status: normalizeStatus(TEAM_STATUS[def.team]),
      wanderCd:Math.floor(Math.random() * 160),
      effectT:0, moving:false,
      path:[], pathIdx:0, arrived:false,
    };
  });
  AGENT_DEFS.forEach(function(def) {
    if (STATE[def.id].status === 'done') STATE[def.id].effectT = 110;
  });

  // ── Shared movement helper: follow A* path or fallback to direct line ──────
  function followPath(s, speed) {
    if (s.path.length > 0 && s.pathIdx < s.path.length) {
      var wp = s.path[s.pathIdx];
      var dx = wp.x - s.x, dy = wp.y - s.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      if (dist > 2) {
        s.x += (dx / dist) * speed;
        s.y += (dy / dist) * speed;
        s.moving = true;
        s.dir = (Math.abs(dx) > Math.abs(dy)) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
        s.fTimer++;
        if (s.fTimer >= ANIM_RATE) { s.fTimer = 0; s.frame = (s.frame + 1) % 3; }
      } else {
        s.pathIdx++;
        if (s.pathIdx >= s.path.length) {
          s.moving = false; s.frame = 1;
          s.arrived = true;
        }
      }
    } else {
      s.moving = false; s.frame = 1;
    }
  }

  // ── Update ────────────────────────────────────────────────────────────────────
  function update() {
    AGENT_DEFS.forEach(function(def) {
      var s    = STATE[def.id];
      var room = ROOMS[def.roomId];

      // ── Active: snap to desk + typing animation ──
      if (s.status === 'active') {
        s.x = s.deskX; s.y = s.deskY;
        s.tx = s.deskX; s.ty = s.deskY;
        s.moving = false; s.dir = 'down';
        s.path = []; s.pathIdx = 0; s.arrived = false;
        // Typing animation: fast frame cycle
        s.fTimer++;
        if (s.fTimer >= 4) { s.fTimer = 0; s.frame = (s.frame + 1) % 3; }
        if (s.effectT > 0) s.effectT--;
        return;
      }

      // ── Done: snap to desk + effect countdown ──
      if (s.status === 'done') {
        s.x = s.deskX; s.y = s.deskY;
        s.moving = false; s.dir = 'down'; s.frame = 1;
        s.path = []; s.pathIdx = 0; s.arrived = false;
        if (s.effectT > 0) s.effectT--;
        return;
      }

      // ── Error: stay in place, no movement ──
      if (s.status === 'error') {
        s.moving = false;
        if (s.effectT > 0) s.effectT--;
        return;
      }

      // ── Communicating: pathfind to Brain HQ entrance ──
      if (s.status === 'communicating') {
        if (!s.arrived) {
          if (s.path.length === 0) {
            var brainRoom = ROOMS.brain;
            var targetX = brainRoom.x + brainRoom.w / 2 + (def.di * 20 - 30);
            var targetY = brainRoom.y + 40;
            var p = findPath(s.x, s.y, targetX, targetY);
            s.path = p || [{x: targetX, y: targetY}];
            s.pathIdx = 0;
          }
          followPath(s, SPEED * 1.5);
        } else {
          s.moving = false; s.dir = 'down'; s.frame = 1;
        }
        if (s.effectT > 0) s.effectT--;
        return;
      }

      // ── Meeting: leaders pathfind to Brain HQ center ──
      if (s.status === 'meeting') {
        if (def.leader) {
          if (!s.arrived) {
            if (s.path.length === 0) {
              var br = ROOMS.brain;
              // Spread leaders across meeting area
              var leaderIdx = 0;
              AGENT_DEFS.forEach(function(d, i) { if (d.leader && d.id === def.id) leaderIdx = i; });
              var meetX = br.x + br.w / 2 + (leaderIdx * 30 - 45);
              var meetY = br.y + br.h / 2;
              var mp = findPath(s.x, s.y, meetX, meetY);
              s.path = mp || [{x: meetX, y: meetY}];
              s.pathIdx = 0;
            }
            followPath(s, SPEED * 1.2);
          } else {
            s.moving = false; s.dir = 'down'; s.frame = 1;
          }
        } else {
          // Non-leaders: snap to desk during meetings
          s.x = s.deskX; s.y = s.deskY;
          s.moving = false; s.dir = 'down'; s.frame = 1;
        }
        if (s.effectT > 0) s.effectT--;
        return;
      }

      // ── Idle: wander within room via A* pathfinding ──
      s.wanderCd--;
      if (s.wanderCd <= 0) {
        if (Math.random() < 0.35) {
          // Random pause in place
          s.path = []; s.pathIdx = 0;
          s.wanderCd = 60 + Math.floor(Math.random() * 100);
        } else {
          var m = 28;
          var wx = room.x + m + Math.random() * (room.w - m * 2);
          var wy = room.y + m + 22 + Math.random() * (room.h - m * 2 - 20);
          var wp = findPath(s.x, s.y, wx, wy);
          s.path = wp || [{x: wx, y: wy}];
          s.pathIdx = 0; s.arrived = false;
          s.wanderCd = 80 + Math.floor(Math.random() * 150);
        }
      }
      followPath(s, SPEED);
      // Boundary clamping
      var mg = 16;
      s.x = Math.max(room.x + mg, Math.min(room.x + room.w - mg, s.x));
      s.y = Math.max(room.y + mg + 22, Math.min(room.y + room.h - mg, s.y));
      if (s.effectT > 0) s.effectT--;
    });
  }

  // ── Render ────────────────────────────────────────────────────────────────────
  function render() {
    prerenderRooms(); // no-op after first successful render

    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = '#06060e';
    ctx.fillRect(0, 0, W, H);

    // Draw room backgrounds (tileset-based once loaded, solid-colour fallback)
    Object.keys(ROOMS).forEach(function(k) { drawRoom(ROOMS[k], k); });

    // Draw desks
    Object.keys(DESKS).forEach(function(rid) {
      var border = ROOMS[rid] ? ROOMS[rid].border : '#ffffff';
      DESKS[rid].forEach(function(d) { drawDesk(d[0], d[1], border); });
    });

    // Active-leader room glow
    AGENT_DEFS.filter(function(d) { return d.leader; }).forEach(function(def) {
      var s = STATE[def.id];
      if (s.status === 'active') {
        var r = ROOMS[def.roomId];
        ctx.save();
        ctx.globalAlpha = 0.12 + 0.06 * Math.sin(tick * 0.06);
        ctx.fillStyle = def.color;
        ctx.fillRect(r.x + 2, r.y + 2, r.w - 4, r.h - 4);
        ctx.restore();
      }
    });

    // Draw agents sorted by Y (painter's algorithm)
    var sorted = AGENT_DEFS.slice().sort(function(a, b) {
      return STATE[a.id].y - STATE[b.id].y;
    });
    sorted.forEach(drawAgent);
    tick++;
  }

  // ── drawRoom ─────────────────────────────────────────────────────────────────
  function drawRoom(room, key) {
    if (ROOM_BG[key]) {
      // Fast blit of pre-rendered tileset background
      ctx.drawImage(ROOM_BG[key], room.x, room.y);
    } else {
      // Fallback: solid colour + subtle grid (used before tileset loads)
      ctx.fillStyle = room.bg;
      ctx.fillRect(room.x, room.y, room.w, room.h);
      ctx.strokeStyle = 'rgba(255,255,255,0.025)';
      ctx.lineWidth = 1;
      for (var gx = room.x; gx <= room.x + room.w; gx += 16) {
        ctx.beginPath(); ctx.moveTo(gx+.5, room.y); ctx.lineTo(gx+.5, room.y+room.h); ctx.stroke();
      }
      for (var gy = room.y; gy <= room.y + room.h; gy += 16) {
        ctx.beginPath(); ctx.moveTo(room.x, gy+.5); ctx.lineTo(room.x+room.w, gy+.5); ctx.stroke();
      }
    }
    // Coloured border
    ctx.strokeStyle = room.border;
    ctx.lineWidth = 2;
    ctx.strokeRect(room.x + 1, room.y + 1, room.w - 2, room.h - 2);
    // Clickable room label (pill background + text)
    ctx.font = 'bold 10px monospace';
    var lw = ctx.measureText(room.name).width;
    ctx.fillStyle = 'rgba(0,0,0,0.80)';
    ctx.fillRect(room.x + 4, room.y + 3, lw + 10, 14);
    ctx.fillStyle = room.border;
    ctx.textAlign = 'left';
    ctx.fillText(room.name, room.x + 9, room.y + 13);
  }

  // ── drawDesk ─────────────────────────────────────────────────────────────────
  function drawDesk(dx, dy, color) {
    ctx.fillStyle = 'rgba(255,255,255,0.07)';
    ctx.fillRect(dx - 13, dy - 7, 26, 14);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(dx - 13, dy - 7, 26, 14);
    // Monitor
    ctx.fillStyle = '#020208';
    ctx.fillRect(dx - 7, dy - 20, 14, 12);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(dx - 7, dy - 20, 14, 12);
    // Screen glow
    ctx.save();
    ctx.globalAlpha = 0.22 + 0.12 * Math.sin(tick * 0.04 + dx * 0.08);
    ctx.fillStyle = color;
    ctx.fillRect(dx - 6, dy - 19, 12, 10);
    ctx.restore();
  }

  // ── drawAgent ─────────────────────────────────────────────────────────────────
  function drawAgent(def) {
    var s = STATE[def.id];
    var x = s.x, y = s.y;

    // Sprite or fallback circle
    ctx.save();
    if (SS.ok && SS.img) {
      var cIdx      = def.charIdx;
      var baseCol   = (cIdx % 4) * 3;
      var baseRow   = Math.floor(cIdx / 4) * 4;
      var spriteCol = baseCol + s.frame;
      var spriteRow = baseRow + (DIR_ROW[s.dir] || 0);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(SS.img,
        spriteCol * 32, spriteRow * 32, 32, 32,
        Math.round(x - SPRITE_SZ / 2), Math.round(y - SPRITE_SZ), SPRITE_SZ, SPRITE_SZ);
    } else {
      ctx.beginPath();
      ctx.arc(x, y - 10, 11, 0, Math.PI * 2);
      ctx.fillStyle = def.color + '22'; ctx.fill();
      ctx.strokeStyle = def.color; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.font = '13px serif'; ctx.textAlign = 'center';
      ctx.fillText(def.emoji, x, y - 4);
    }
    ctx.restore();

    // Name tag
    var label = def.id.length > 10 ? def.id.slice(0, 10) : def.id;
    ctx.save();
    ctx.font = 'bold 7px monospace'; ctx.textAlign = 'center';
    var tw = ctx.measureText(label).width;
    ctx.fillStyle = 'rgba(0,0,0,0.82)';
    ctx.fillRect(Math.round(x - tw / 2 - 2), Math.round(y + 2), tw + 4, 9);
    ctx.fillStyle = def.color;
    ctx.fillText(label, x, Math.round(y) + 10);
    ctx.restore();

    // Status / speech-bubble overlay
    ctx.save(); ctx.textAlign = 'center';
    if (s.effectT > 0 && s.status === 'done') {
      ctx.globalAlpha = s.effectT / 110;
      ctx.font = '11px serif';
      ctx.fillText('\u2705', x, y - SPRITE_SZ - 5);
    } else if (s.status === 'error') {
      // Red pulse effect
      ctx.globalAlpha = 0.5 + 0.5 * Math.sin(tick * 0.25);
      ctx.font = '11px serif';
      ctx.fillText('\u274C', x, y - SPRITE_SZ - 5);
    } else if (s.status === 'active') {
      if (def.leader) {
        // Speech bubble showing current real task for the team leader
        var rk = TEAM_REAL[def.team];
        var taskTxt = AGENT_TASKS[rk] ? AGENT_TASKS[rk].substring(0, 28) : '작업 중...';
        drawTaskBubble(x, y - SPRITE_SZ - 4, taskTxt, def.color);
      }
      // Typing particles for all active agents (3 animated dots)
      var dotPhase = Math.floor(tick / 6) % 3;
      for (var di = 0; di < 3; di++) {
        ctx.globalAlpha = (di === dotPhase) ? 1.0 : 0.3;
        ctx.fillStyle = def.color;
        ctx.fillRect(Math.round(x - 6 + di * 5), Math.round(y - SPRITE_SZ - 14), 2, 2);
      }
      ctx.globalAlpha = 1.0;
    } else if (s.status === 'communicating') {
      // Speech bubble when arrived at Brain HQ
      if (s.arrived) {
        ctx.globalAlpha = 0.7 + 0.3 * Math.sin(tick * 0.1);
        ctx.font = '10px serif';
        ctx.fillText('\uD83D\uDCE1', x, y - SPRITE_SZ - 5); // 📡
      } else {
        // Moving indicator
        ctx.globalAlpha = 0.6;
        ctx.fillStyle = def.color;
        ctx.font = '7px monospace';
        ctx.fillText('→HQ', x, y - SPRITE_SZ - 5);
      }
    } else if (s.status === 'meeting' && def.leader) {
      if (s.arrived) {
        ctx.globalAlpha = 0.7 + 0.3 * Math.sin(tick * 0.08);
        ctx.font = '10px serif';
        ctx.fillText('\uD83E\uDD1D', x, y - SPRITE_SZ - 5); // 🤝
      }
    }
    ctx.restore();
  }

  // ── drawTaskBubble ────────────────────────────────────────────────────────────
  function drawTaskBubble(x, y, text, color) {
    ctx.save();
    ctx.font = '7px monospace';
    var tw = ctx.measureText(text).width;
    var bw = tw + 8, bh = 12;
    var bx = x - bw / 2, by = y - bh;

    ctx.fillStyle = 'rgba(0,0,0,0.88)';
    ctx.fillRect(bx, by, bw, bh);
    ctx.strokeStyle = color; ctx.lineWidth = 1;
    ctx.strokeRect(bx, by, bw, bh);

    // Downward arrow
    ctx.beginPath();
    ctx.moveTo(x - 4, by + bh);
    ctx.lineTo(x + 4, by + bh);
    ctx.lineTo(x, by + bh + 5);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0,0,0,0.88)'; ctx.fill();
    ctx.strokeStyle = color; ctx.stroke();

    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(text, x, by + bh - 3);
    ctx.restore();
  }

  // ── Popup ─────────────────────────────────────────────────────────────────────
  function showPaPopup(roomKey) {
    var room   = ROOMS[roomKey];
    var agents = AGENT_DEFS.filter(function(d) { return d.roomId === roomKey; });
    var rk     = TEAM_REAL[roomKey];

    var titleEl = document.getElementById('pa-popup-title');
    if (titleEl) { titleEl.textContent = room.name; titleEl.style.color = room.border; }

    var stLabels = {active:'🔄 Active', idle:'💤 Idle', done:'✅ Done', error:'❌ Error',
                    communicating:'📡 Comm', meeting:'🤝 Meeting'};
    var stColors = {active:'#fdcb6e', idle:'#636e72', done:'#00b894', error:'#e17055',
                    communicating:'#74b9ff', meeting:'#a29bfe'};

    var html = '';
    agents.forEach(function(def) {
      var st      = (STATE[def.id] && STATE[def.id].status) || 'idle';
      var stLabel = stLabels[st] || st;
      var stColor = stColors[st] || '#aaa';
      var taskTxt = '';
      if (def.leader && AGENT_TASKS[rk]) {
        taskTxt = AGENT_TASKS[rk].substring(0, 60) + (AGENT_TASKS[rk].length > 60 ? '...' : '');
      }
      html += '<div class="pa-popup-agent">';
      html += '<span class="pa-popup-emoji">' + def.emoji + '</span>';
      html += '<div style="flex:1;min-width:0">';
      html += '<div class="pa-popup-name" style="color:' + def.color + '">' +
              def.id + (def.leader ? ' 👑' : '') + '</div>';
      if (taskTxt) {
        html += '<div class="pa-popup-task">' + taskTxt + '</div>';
      }
      html += '</div>';
      html += '<span class="pa-popup-status" style="color:' + stColor + '">' + stLabel + '</span>';
      html += '</div>';
    });
    var roomEngines = ROOM_ENGINES[roomKey] || [];
    // Bug 2 fix: show only this room's logs; removed fallback to ALL logs
    var displayLogs = AGENT_LOGS.filter(function(entry) {
      return roomEngines.some(function(eng) {
        var fromVal = entry.from || '';
        var toVal = entry.to || '';
        return fromVal.indexOf(eng) >= 0 || toVal.indexOf(eng) >= 0;
      });
    });

    // Bug 4 fix: per-agent-type emoji labels for log entries
    var LABEL_MAP = {
      'Brain':         '🧠 Brain',
      'Hands-4':       '⌨️ CC',    'CC팀':   '⌨️ CC',    'claude_code': '⌨️ CC',
      'Hands-3':       '🤖 Codex', 'codex':  '🤖 Codex', 'Codex':       '🤖 Codex',
      'Hands-1':       '🚀 AG',    'Hands-2':'🚀 AG',    'antigravity': '🚀 AG',
      'Antigravity':   '🚀 AG',
    };
    function agentLabel(name) { return LABEL_MAP[name] || ('💬 ' + name); }

    html += '<div class="pa-popup-log-header">💬 대화 로그</div>';
    if (displayLogs.length === 0) {
      html += '<div class="pa-popup-log">로그 없음</div>';
    } else {
      html += '<div class="pa-popup-log-wrap">';
      displayLogs.forEach(function(entry) {
        var fromVal = entry.from || '';
        var toVal = entry.to || '';
        var fromLabel = agentLabel(fromVal);
        var toLabel   = agentLabel(toVal);
        var timeStr   = entry.time ? '[' + entry.time + '] ' : '';
        html += '<div class="pa-log-entry">';
        html += '<span class="pa-log-arrow">' + timeStr + fromLabel + ' → ' + toLabel + '</span>';
        html += '<span class="pa-log-msg">' + (entry.msg || '') + '</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    var contentEl = document.getElementById('pa-popup-content');
    if (contentEl) contentEl.innerHTML = html;

    var overlayEl = document.getElementById('pa-popup-overlay');
    if (overlayEl) overlayEl.style.display = 'block';
  }

  function closePaPopup() {
    var el = document.getElementById('pa-popup-overlay');
    if (el) el.style.display = 'none';
  }
  window.closePaPopup = closePaPopup;

  // ── Click / hover handlers ────────────────────────────────────────────────────
  canvas.addEventListener('click', function(e) {
    var rect = canvas.getBoundingClientRect();
    var scX = W / rect.width, scY = H / rect.height;
    var cx = (e.clientX - rect.left) * scX;
    var cy = (e.clientY - rect.top)  * scY;
    var clicked = null;
    // Bug 6 fix: click area matches WALL_H (20px), was 18px
    Object.keys(ROOMS).forEach(function(k) {
      var r = ROOMS[k];
      if (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + 20) clicked = k;
    });
    if (clicked) showPaPopup(clicked);
  });

  canvas.addEventListener('mousemove', function(e) {
    var rect = canvas.getBoundingClientRect();
    var scX = W / rect.width, scY = H / rect.height;
    var cx = (e.clientX - rect.left) * scX;
    var cy = (e.clientY - rect.top)  * scY;
    var over = false;
    Object.keys(ROOMS).forEach(function(k) {
      var r = ROOMS[k];
      if (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + 18) over = true;
    });
    canvas.style.cursor = over ? 'pointer' : 'default';
  });

  // ── External refresh API (realtime update without page reload) ───────────────
  // Called by Dashboard.update() when window.state.dashboard_data changes.
  function refreshPixelAgents(teamStatus, agentTasks, logs) {
    TEAM_STATUS = teamStatus || {};
    AGENT_TASKS = agentTasks || {};
    AGENT_LOGS  = logs || [];
    AGENT_DEFS.forEach(function(def) {
      var s  = STATE[def.id];
      if (!s) return;
      var st = normalizeStatus(TEAM_STATUS[def.team]);
      if (s.status !== st) {
        // Trigger ✅ effect when transitioning to done
        if (st === 'done') s.effectT = 110;
        // Reset pathfinding state on status change
        s.path = []; s.pathIdx = 0; s.arrived = false;
        s.status = st;
      }
    });
  }

  // ── Main loop ─────────────────────────────────────────────────────────────────
  function loop() { update(); render(); requestAnimationFrame(loop); }
  loop();

  // ── Register with Dashboard for realtime updates ──────────────────────────────
  if (typeof Dashboard !== 'undefined' && Dashboard.registerPanel) {
    Dashboard.registerPanel('pixel-agents', {
      render: function(data) {
        var ps = (data && data.pixel_state) || {};
        refreshPixelAgents(ps.teamStatus, ps.agentTasks, (data && data.pixel_logs) || []);
      }
    });
  }

})();
