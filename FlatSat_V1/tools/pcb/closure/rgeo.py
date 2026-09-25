#!/usr/bin/env python3
"""Raster geometry + Dijkstra router for L11 attachment stubs and extension pre-routing.
Run with KiCad's bundled python3 (needs pcbnew + numpy).

Everything is exact-shape based: obstacles are KiCad's own TransformShapeToPolygon output
(pads of any shape, tracks as capsules, vias as rings) inflated by the required clearance,
rasterised by scanline into a numpy grid.  No inscribed-circle approximations.
"""
import math
import heapq
import numpy as np
import pcbnew

MM = pcbnew.FromMM
TOMM = pcbnew.ToMM
CU = None  # set by init()


def copper_layers(board):
    n = board.GetCopperLayerCount()
    ids = [pcbnew.F_Cu] + [board.GetLayerID('In%d.Cu' % i) for i in range(1, n - 1)] + [pcbnew.B_Cu]
    return ids


# ---------------------------------------------------------------- rasterising

def fill_poly(grid, pts, x0, y0, step, value=True):
    """even-odd scanline fill of one closed polygon (list of (x,y) mm) into a bool grid."""
    if len(pts) < 3:
        return
    xs = np.array([p[0] for p in pts], dtype=float)
    ys = np.array([p[1] for p in pts], dtype=float)
    H, W = grid.shape
    j0 = int(math.floor((ys.min() - y0) / step - 0.5))
    j1 = int(math.ceil((ys.max() - y0) / step + 0.5))
    j0 = max(j0, 0)
    j1 = min(j1, H - 1)
    if j1 < j0:
        return
    x2 = np.roll(xs, -1)
    y2 = np.roll(ys, -1)
    dy = y2 - ys
    for j in range(j0, j1 + 1):
        y = y0 + (j + 0.5) * step
        cond = (ys > y) != (y2 > y)
        if not cond.any():
            continue
        xi = xs[cond] + (y - ys[cond]) * (x2[cond] - xs[cond]) / dy[cond]
        xi = np.sort(xi)
        for k in range(0, len(xi) - 1, 2):
            a = int(math.ceil((xi[k] - x0) / step - 0.5))
            b = int(math.floor((xi[k + 1] - x0) / step - 0.5))
            if a < 0:
                a = 0
            if b > W - 1:
                b = W - 1
            if b >= a:
                grid[j, a:b + 1] = value


def polyset_pts(ps):
    """yield outline point lists (mm) of a SHAPE_POLY_SET (outer contours only -> conservative)."""
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        yield [(TOMM(o.CPoint(k).x), TOMM(o.CPoint(k).y)) for k in range(o.PointCount())]


def fill_circle(grid, cx, cy, r, x0, y0, step, value=True):
    H, W = grid.shape
    j0 = max(0, int((cy - r - y0) / step))
    j1 = min(H - 1, int((cy + r - y0) / step) + 1)
    i0 = max(0, int((cx - r - x0) / step))
    i1 = min(W - 1, int((cx + r - x0) / step) + 1)
    if j1 < j0 or i1 < i0:
        return
    yy = y0 + (np.arange(j0, j1 + 1) + 0.5) * step
    xx = x0 + (np.arange(i0, i1 + 1) + 0.5) * step
    d2 = (xx[None, :] - cx) ** 2 + (yy[:, None] - cy) ** 2
    sub = grid[j0:j1 + 1, i0:i1 + 1]
    sub[d2 <= r * r] = value


# ---------------------------------------------------------------- board facts

class Board:
    def __init__(self, path, snap):
        self.b = pcbnew.LoadBoard(path)
        self.snap = snap
        self.cu = copper_layers(self.b)
        self.fcu = pcbnew.F_Cu
        self.bcu = pcbnew.B_Cu
        self.her_fp = set(snap['footprints'].keys())
        self.her_tr = set(snap['tracks'].keys())
        self.rev2 = [tuple(p) for p in snap['rev2_outline']]
        self._index()

    def _index(self):
        b = self.b
        self.pads = []      # (pad, ref, net, layers set, bbox(x0,y0,x1,y1), is_heritage)
        for fp in b.GetFootprints():
            ish = fp.m_Uuid.AsString() in self.her_fp
            ref = fp.GetReference()
            for pd in fp.Pads():
                bb = pd.GetBoundingBox()
                lay = set(l for l in self.cu if pd.IsOnLayer(l))
                self.pads.append((pd, ref, pd.GetNetname(), lay, (TOMM(bb.GetLeft()), TOMM(bb.GetTop()), TOMM(bb.GetRight()), TOMM(bb.GetBottom())), ish))
        # graphic items that sit on a copper layer (the FC has a poem in F.Cu text): real copper,
        # shorts against them are real DRC errors, so they are obstacles like anything else
        self.gfx = []
        for d in list(b.GetDrawings()) + [g for f in b.GetFootprints() for g in f.GraphicalItems()]:
            l = d.GetLayer()
            if l not in self.cu:
                continue
            bb = d.GetBoundingBox()
            self.gfx.append((d, l, (TOMM(bb.GetLeft()), TOMM(bb.GetTop()), TOMM(bb.GetRight()), TOMM(bb.GetBottom()))))
        self.refresh_tracks()
        # board outline (grown) with holes
        self.outline_ps = pcbnew.SHAPE_POLY_SET()
        b.GetBoardPolygonOutlines(self.outline_ps, False)
        # heritage zone fills, per layer, for the soft penalty
        self.zone_fills = []   # (net, layer, [pts...])
        for z in b.Zones():
            if z.GetIsRuleArea():
                continue
            for l in z.GetLayerSet().Seq():
                if l not in self.cu:
                    continue
                fp = z.GetFilledPolysList(l)
                for i in range(fp.OutlineCount()):
                    o = fp.Outline(i)
                    pts = [(TOMM(o.CPoint(k).x), TOMM(o.CPoint(k).y)) for k in range(o.PointCount())]
                    if pts:
                        self.zone_fills.append((z.GetNetname(), l, pts))

    def refresh_tracks(self):
        self.tracks = []    # (item, net, layer or None for via, bbox, is_heritage)
        for t in self.b.GetTracks():
            bb = t.GetBoundingBox()
            isv = t.GetClass() == 'PCB_VIA'
            self.tracks.append((t, t.GetNetname(), None if isv else t.GetLayer(), (TOMM(bb.GetLeft()), TOMM(bb.GetTop()), TOMM(bb.GetRight()), TOMM(bb.GetBottom())), t.m_Uuid.AsString() in self.her_tr, isv))


# ---------------------------------------------------------------- window grid

class Grid:
    def __init__(self, bd, x0, y0, x1, y1, step):
        self.bd = bd
        self.step = step
        self.x0, self.y0 = x0, y0
        self.W = int(math.ceil((x1 - x0) / step))
        self.H = int(math.ceil((y1 - y0) / step))
        self.x1, self.y1 = x0 + self.W * step, y0 + self.H * step
        xs = x0 + (np.arange(self.W) + 0.5) * step
        ys = y0 + (np.arange(self.H) + 0.5) * step
        self.xx = xs
        self.yy = ys
        self.inside_rev2, self.dist_b = self._rev2_fields()
        self.board_ok = self._board_mask()

    def cell(self, x, y):
        return (int((y - self.y0) / self.step), int((x - self.x0) / self.step))

    def pos(self, j, i):
        return (float(self.x0 + (i + 0.5) * self.step), float(self.y0 + (j + 0.5) * self.step))

    def _rev2_fields(self):
        poly = self.bd.rev2
        X, Y = np.meshgrid(self.xx, self.yy)
        inside = np.zeros((self.H, self.W), dtype=bool)
        dmin = np.full((self.H, self.W), 1e9)
        n = len(poly)
        for i in range(n):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % n]
            cond = (ay > Y) != (by > Y)
            with np.errstate(divide='ignore', invalid='ignore'):
                xin = ax + (Y - ay) * (bx - ax) / (by - ay)
            inside ^= cond & (X < xin)
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            if L2 == 0:
                d = np.hypot(X - ax, Y - ay)
            else:
                t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0.0, 1.0)
                d = np.hypot(X - (ax + t * dx), Y - (ay + t * dy))
            np.minimum(dmin, d, out=dmin)
        return inside, dmin

    def _board_mask(self):
        """True where a track centre may sit w.r.t. the board outline (before edge clearance)."""
        m = np.zeros((self.H, self.W), dtype=bool)
        ps = self.bd.outline_ps
        for i in range(ps.OutlineCount()):
            o = ps.Outline(i)
            fill_poly(m, [(TOMM(o.CPoint(k).x), TOMM(o.CPoint(k).y)) for k in range(o.PointCount())], self.x0, self.y0, self.step, True)
            for h in range(ps.HoleCount(i)):
                hh = ps.Hole(i, h)
                fill_poly(m, [(TOMM(hh.CPoint(k).x), TOMM(hh.CPoint(k).y)) for k in range(hh.PointCount())], self.x0, self.y0, self.step, False)
        return m

    # ---- obstacle raster -------------------------------------------------
    def obstacles(self, layer, net, half_w, clear, same_clear=0.06, edge=0.2,
                  skip_uuids=(), extra_free_pads=(), zero_uuids=(), net_clear=None):
        """bool grid: True = blocked for a track centre of `net` with half width `half_w` on `layer`."""
        blk = np.zeros((self.H, self.W), dtype=bool)
        x0, y0, s = self.x0, self.y0, self.step
        X0, Y0, X1, Y1 = self.x0, self.y0, self.x1, self.y1
        pad_extra = 0.0

        def hit(bb, m):
            return not (bb[2] + m < X0 or bb[0] - m > X1 or bb[3] + m < Y0 or bb[1] - m > Y1)

        for pd, ref, pnet, lay, bb, ish in self.bd.pads:
            if layer not in lay:
                continue
            if pd in extra_free_pads:
                continue
            same = (pnet == net and pnet != '')
            if same and same_clear is None:
                continue
            c = same_clear if same else (clear if net_clear is None else max(clear, net_clear(pnet)))
            if not hit(bb, c + half_w + 0.2):
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            pd.TransformShapeToPolygon(ps, layer, MM(c + half_w), MM(0.005), pcbnew.ERROR_OUTSIDE)
            for pts in polyset_pts(ps):
                fill_poly(blk, pts, x0, y0, s)
        for t, tnet, tl, bb, ish, isv in self.bd.tracks:
            uu = t.m_Uuid.AsString()
            if uu in skip_uuids:
                continue
            if not isv and tl != layer:
                continue
            if isv and not t.IsOnLayer(layer):
                continue
            if uu in zero_uuids:
                continue
            same = (tnet == net and tnet != '')
            if same and same_clear is None:
                continue
            c = same_clear if same else (clear if net_clear is None else max(clear, net_clear(tnet)))
            if not hit(bb, c + half_w + 0.2):
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            try:
                t.TransformShapeToPolygon(ps, layer, MM(c + half_w), MM(0.005), pcbnew.ERROR_OUTSIDE)
            except Exception:
                continue
            for pts in polyset_pts(ps):
                fill_poly(blk, pts, x0, y0, s)
        for d, dl, bb in self.bd.gfx:
            if dl != layer or not hit(bb, clear + half_w + 0.2):
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            try:
                d.TransformShapeToPolygon(ps, layer, MM(clear + half_w), MM(0.01), pcbnew.ERROR_OUTSIDE)
            except Exception:
                ps.NewOutline()
                for x, y in ((bb[0] - clear - half_w, bb[1] - clear - half_w), (bb[2] + clear + half_w, bb[1] - clear - half_w),
                             (bb[2] + clear + half_w, bb[3] + clear + half_w), (bb[0] - clear - half_w, bb[3] + clear + half_w)):
                    ps.Append(pcbnew.VECTOR2I_MM(x, y))
            for pts in polyset_pts(ps):
                fill_poly(blk, pts, x0, y0, s)
        # board edge
        edge_ok = self._deflated_board(edge + half_w)
        blk |= ~edge_ok
        return blk

    _defl_cache = None

    def _deflated_board(self, d):
        if self._defl_cache is None:
            self._defl_cache = {}
        k = round(d, 3)
        if k in self._defl_cache:
            return self._defl_cache[k]
        ps = pcbnew.SHAPE_POLY_SET(self.bd.outline_ps)
        ps.Inflate(-MM(d), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.01))
        m = np.zeros((self.H, self.W), dtype=bool)
        for i in range(ps.OutlineCount()):
            o = ps.Outline(i)
            fill_poly(m, [(TOMM(o.CPoint(kk).x), TOMM(o.CPoint(kk).y)) for kk in range(o.PointCount())], self.x0, self.y0, self.step, True)
            for h in range(ps.HoleCount(i)):
                hh = ps.Hole(i, h)
                fill_poly(m, [(TOMM(hh.CPoint(kk).x), TOMM(hh.CPoint(kk).y)) for kk in range(hh.PointCount())], self.x0, self.y0, self.step, False)
        self._defl_cache[k] = m
        return m

    def hole_mask(self, net, drill_r, extra=0.25):
        """blocked for a new drill of radius drill_r (hole-to-hole 0.5 mm rule, +margin)."""
        blk = np.zeros((self.H, self.W), dtype=bool)
        for pd, ref, pnet, lay, bb, ish in self.bd.pads:
            dr = TOMM(pd.GetDrillSizeX()) / 2.0
            if dr <= 0:
                continue
            p = pd.GetPosition()
            fill_circle(blk, TOMM(p.x), TOMM(p.y), dr + drill_r + 0.5 + extra, self.x0, self.y0, self.step)
        for t, tnet, tl, bb, ish, isv in self.bd.tracks:
            if not isv:
                continue
            dr = TOMM(t.GetDrill()) / 2.0
            p = t.GetPosition()
            fill_circle(blk, TOMM(p.x), TOMM(p.y), dr + drill_r + 0.5 + extra, self.x0, self.y0, self.step)
        return blk

    def zone_penalty(self, layer, net, skip_nets=('GND',)):
        pen = np.zeros((self.H, self.W), dtype=bool)
        for znet, zl, pts in self.bd.zone_fills:
            if zl != layer or znet == net or znet in skip_nets:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if max(xs) < self.x0 or min(xs) > self.x1 or max(ys) < self.y0 or min(ys) > self.y1:
                continue
            fill_poly(pen, pts, self.x0, self.y0, self.step)
        return pen


# ---------------------------------------------------------------- Dijkstra

NB = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
      (-1, -1, 1.41421356), (-1, 1, 1.41421356), (1, -1, 1.41421356), (1, 1, 1.41421356)]


def dijkstra(free, start_cells, goal_mask, step, cost_mult=None, maxdist=None):
    """free: bool grid (True = passable).  returns (path cells, dist) or None."""
    H, W = free.shape
    INF = 1e18
    dist = np.full(H * W, INF)
    prev = np.full(H * W, -1, dtype=np.int64)
    pq = []
    for (j, i) in start_cells:
        if 0 <= j < H and 0 <= i < W and free[j, i]:
            idx = j * W + i
            dist[idx] = 0.0
            heapq.heappush(pq, (0.0, idx))
    gm = goal_mask.ravel()
    fr = free.ravel()
    cm = cost_mult.ravel() if cost_mult is not None else None
    best = None
    while pq:
        d, idx = heapq.heappop(pq)
        if d > dist[idx] + 1e-12:
            continue
        if gm[idx]:
            best = idx
            break
        if maxdist is not None and d > maxdist:
            break
        j, i = divmod(idx, W)
        for dj, di, w in NB:
            nj, ni = j + dj, i + di
            if nj < 0 or nj >= H or ni < 0 or ni >= W:
                continue
            nidx = nj * W + ni
            if not fr[nidx]:
                continue
            c = w * step * (cm[nidx] if cm is not None else 1.0)
            nd = d + c
            if nd < dist[nidx] - 1e-12:
                dist[nidx] = nd
                prev[nidx] = idx
                heapq.heappush(pq, (nd, nidx))
    if best is None:
        return None
    path = []
    idx = best
    while idx != -1:
        path.append(divmod(idx, W))
        idx = prev[idx]
    path.reverse()
    return path, dist[best]


def simplify(path, grid, free, tol_deg=(0, 45, 90, 135, 180, 225, 270, 315)):
    """collinear-merge grid cells, then greedily merge segments whose straight line stays free."""
    if len(path) < 2:
        return [grid.pos(*p) for p in path]
    pts = [path[0]]
    for k in range(1, len(path) - 1):
        a, b, c = path[k - 1], path[k], path[k + 1]
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            pts.append(b)
    pts.append(path[-1])

    def clear_line(p, q):
        n = max(2, int(max(abs(q[0] - p[0]), abs(q[1] - p[1])) * 2) + 2)
        for t in range(n + 1):
            jj = p[0] + (q[0] - p[0]) * t / n
            ii = p[1] + (q[1] - p[1]) * t / n
            for dj in (0, ):
                j = int(round(jj))
                i = int(round(ii))
                if j < 0 or j >= free.shape[0] or i < 0 or i >= free.shape[1] or not free[j, i]:
                    return False
        return True

    out = [pts[0]]
    k = 0
    while k < len(pts) - 1:
        best = k + 1
        for m in range(len(pts) - 1, k, -1):
            if clear_line(pts[k], pts[m]):
                best = m
                break
        out.append(pts[best])
        k = best
    return [grid.pos(*p) for p in out]
