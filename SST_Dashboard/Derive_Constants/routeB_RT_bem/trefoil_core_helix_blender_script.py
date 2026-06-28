import bpy
import bmesh
import math
from math import sin, cos, pi
from mathutils import Vector, Matrix

# ============================================================
# Trefoil core tube + outer 3-blade screw shell
# v3: straight segment with male plug + boolean-cut female socket
# ============================================================

# ---------------------------
# User parameters
# ---------------------------
OBJECT_NAME = "Trefoil_CorePlusBlade_v3"

# Resolution
N_SAMPLES = 900
PROFILE_SAMPLES = 180

# Trefoil centerline
GLOBAL_SCALE = 1.0
TREFOIL_SCALE = 1.10

# Centerline mode
USE_TREFOIL_CURVATURE = False   # True = trefoil, False = straight segment
SEGMENT_COUNT = 3
STRAIGHT_LENGTH = None          # auto-computed from trefoil length / SEGMENT_COUNT
CENTER_LOCK = False

# ---------------------------
# Core + blade geometry
# ---------------------------
CORE_RADIUS = 0.36
BLADE_RADIUS = 0.36
LOBE_STRENGTH = 0.92
BLADE_SHARPNESS = 0.22
PROFILE_ECCENTRICITY = 1.00

# Twist around path
TREFOIL_TWIST_TURNS = 10.0
TWIST_TURNS = TREFOIL_TWIST_TURNS if USE_TREFOIL_CURVATURE else (TREFOIL_TWIST_TURNS / SEGMENT_COUNT)

# Center-lock options
LOCK_TO_GAP = True
CENTER_LOCK_BLEND = 1.0

# Mesh / cleanup
SMOOTH_SHADE = True
MERGE_BY_DISTANCE = 1e-5
DELETE_EXISTING_SAME_NAME = True

# Transform to match triple gear
APPLY_FINAL_TRANSFORM = True
FINAL_MIRROR_Y = True
FINAL_UNIFORM_SCALE = 9.52

# ------------------------------------------------------------
# Connector settings
# ------------------------------------------------------------
ENABLE_CONNECTORS = True

# Connector lengths (object units before final scale)
MALE_CONNECTOR_LENGTH = 1.80
FEMALE_SOCKET_LENGTH = 1.95

# D-key size
CONNECTOR_RADIUS_SCALE = 0.82
D_FLAT_FRACTION = 0.74

# TPU fit clearance
CONNECTOR_CLEARANCE = 0.05

# Female wall thickness guidance
FEMALE_WALL_EXTRA = 0.14

# Reinforced collar near body ends
END_COLLAR_LENGTH = 1.20
END_COLLAR_EXTRA = 0.10

# Male barb / snap
ENABLE_SNAP = True
SNAP_BUMP_HEIGHT = 0.1
SNAP_BUMP_WIDTH = 0.18
SNAP_BUMP_POS = 0.80

# Boolean cleanup
APPLY_VOXEL_REMESH = False
VOXEL_SIZE = 0.08

# Export
EXPORT_STL = True
EXPORT_PATH = r"C:\workspace\projects\SwirlStringTheory\3d-prints\Triple_Gear\files\trefoil_core_plus_blade_connector_v4.1_10_turns.stl"


# ============================================================
# Utility
# ============================================================

def cleanup_existing(name: str):
    if not DELETE_EXISTING_SAME_NAME:
        return
    obj = bpy.data.objects.get(name)
    if obj is not None:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def trefoil_point(t: float) -> Vector:
    x = sin(t) + 2.0 * sin(2.0 * t)
    y = cos(t) - 2.0 * cos(2.0 * t)
    z = -sin(3.0 * t)
    return TREFOIL_SCALE * GLOBAL_SCALE * Vector((x, y, z))


def sample_closed_curve(n: int):
    return [trefoil_point(2.0 * pi * i / n) for i in range(n)]


def compute_curve_length(points, closed: bool):
    L = 0.0
    for i in range(1, len(points)):
        L += (points[i] - points[i - 1]).length
    if closed and len(points) > 1:
        L += (points[0] - points[-1]).length
    return L


def compute_auto_straight_length():
    trefoil_points = sample_closed_curve(N_SAMPLES)
    trefoil_length = compute_curve_length(trefoil_points, closed=True)
    segment_length = trefoil_length / SEGMENT_COUNT
    return trefoil_length, segment_length


def centerline_point(u: float, straight_length: float) -> Vector:
    if USE_TREFOIL_CURVATURE:
        t = 2.0 * pi * u
        return trefoil_point(t)
    return Vector((0.0, 0.0, straight_length * u))


def sample_centerline(n: int, straight_length: float):
    if USE_TREFOIL_CURVATURE:
        return [centerline_point(i / n, straight_length) for i in range(n)]
    if n < 2:
        return [centerline_point(0.0, straight_length)]
    return [centerline_point(i / (n - 1), straight_length) for i in range(n)]


def compute_tangents(points):
    n = len(points)
    tangents = []

    if USE_TREFOIL_CURVATURE:
        for i in range(n):
            p_prev = points[(i - 1) % n]
            p_next = points[(i + 1) % n]
            d = p_next - p_prev
            if d.length < 1e-12:
                d = Vector((1.0, 0.0, 0.0))
            tangents.append(d.normalized())
    else:
        for i in range(n):
            if i == 0:
                d = points[1] - points[0]
            elif i == n - 1:
                d = points[-1] - points[-2]
            else:
                d = points[i + 1] - points[i - 1]

            if d.length < 1e-12:
                d = Vector((0.0, 0.0, 1.0))
            tangents.append(d.normalized())

    return tangents


def choose_initial_normal(tangent: Vector) -> Vector:
    candidates = [Vector((0, 0, 1)), Vector((0, 1, 0)), Vector((1, 0, 0))]
    best = None
    best_len = -1.0
    for c in candidates:
        v = c - c.dot(tangent) * tangent
        l = v.length
        if l > best_len:
            best = v
            best_len = l
    if best is None or best.length < 1e-12:
        best = Vector((1, 0, 0))
    return best.normalized()


def rotation_between(a: Vector, b: Vector) -> Matrix:
    a = a.normalized()
    b = b.normalized()
    dot_ab = max(-1.0, min(1.0, a.dot(b)))

    if dot_ab > 0.999999:
        return Matrix.Identity(3)

    if dot_ab < -0.999999:
        axis = a.cross(Vector((1, 0, 0)))
        if axis.length < 1e-8:
            axis = a.cross(Vector((0, 1, 0)))
        axis.normalize()
        return Matrix.Rotation(pi, 3, axis)

    axis = a.cross(b)
    if axis.length < 1e-12:
        return Matrix.Identity(3)
    axis.normalize()
    angle = math.acos(dot_ab)
    return Matrix.Rotation(angle, 3, axis)


def compute_parallel_transport_frames(points, tangents):
    n = len(points)
    frames = []

    T0 = tangents[0]
    N0 = choose_initial_normal(T0)
    B0 = T0.cross(N0)
    if B0.length < 1e-12:
        B0 = Vector((0, 1, 0))
    B0.normalize()
    N0 = B0.cross(T0).normalized()

    frames.append((N0, B0, T0))
    N_prev, B_prev, T_prev = N0, B0, T0

    for i in range(1, n):
        T = tangents[i]
        R = rotation_between(T_prev, T)

        N = (R @ N_prev).normalized()
        B = (R @ B_prev).normalized()

        B = T.cross(N)
        if B.length < 1e-12:
            B = B_prev.copy()
        B.normalize()
        N = B.cross(T).normalized()

        frames.append((N, B, T))
        N_prev, B_prev, T_prev = N, B, T

    if USE_TREFOIL_CURVATURE:
        N_start, B_start, T_start = frames[0]
        N_end, B_end, T_end = frames[-1]

        cross_ne = N_end.cross(N_start)
        sign = 1.0 if cross_ne.dot(T_start) >= 0 else -1.0
        dot_ne = max(-1.0, min(1.0, N_end.dot(N_start)))
        closure_angle = sign * math.acos(dot_ne)

        corrected = []
        for i, (N, B, T) in enumerate(frames):
            frac = i / n
            Rcorr = Matrix.Rotation(frac * closure_angle, 3, T)
            Nc = (Rcorr @ N).normalized()
            Bc = (Rcorr @ B).normalized()
            Bc = T.cross(Nc)
            if Bc.length < 1e-12:
                Bc = B
            Bc.normalize()
            Nc = Bc.cross(T).normalized()
            corrected.append((Nc, Bc, T))
        return corrected

    return frames


def inward_alignment_phase(P: Vector, N: Vector, B: Vector, T: Vector, center=Vector((0.0, 0.0, 0.0))):
    radial = center - P
    radial_plane = radial - radial.dot(T) * T

    if radial_plane.length < 1e-10:
        return 0.0

    radial_plane.normalize()
    x = radial_plane.dot(N)
    y = radial_plane.dot(B)
    return math.atan2(y, x)


# ============================================================
# Profiles
# ============================================================

def blade_envelope(theta: float) -> float:
    raw = (
        1.0
        + LOBE_STRENGTH * math.cos(3.0 * theta)
        + BLADE_SHARPNESS * math.cos(6.0 * theta)
    )
    return max(0.0, raw)


def profile_radius(theta: float) -> float:
    return CORE_RADIUS + BLADE_RADIUS * blade_envelope(theta)


def profile_xy(theta: float):
    r = profile_radius(theta)
    x = r * math.cos(theta)
    y = r * math.sin(theta) * PROFILE_ECCENTRICITY
    return x, y


def min_profile_radius():
    vals = []
    samples = 720
    for i in range(samples):
        th = 2.0 * pi * i / samples
        vals.append(profile_radius(th))
    return min(vals)


# ============================================================
# Connector helpers
# ============================================================

def d_key_xy(theta: float, radius: float, flat_fraction: float):
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    flat_x = -radius * flat_fraction
    if x < flat_x:
        x = flat_x
    return x, y


def male_connector_profile_xy(theta: float, z_local: float):
    base_r = min_profile_radius() * CONNECTOR_RADIUS_SCALE
    x, y = d_key_xy(theta, base_r, D_FLAT_FRACTION)

    if ENABLE_SNAP:
        barb_peak = SNAP_BUMP_POS * MALE_CONNECTOR_LENGTH
        barb_start = barb_peak - SNAP_BUMP_WIDTH * 0.75
        barb_end   = barb_peak + SNAP_BUMP_WIDTH * 0.25

        bump = 0.0
        if barb_start <= z_local <= barb_peak:
            bump = SNAP_BUMP_HEIGHT * (z_local - barb_start) / max(1e-9, (barb_peak - barb_start))
        elif barb_peak < z_local <= barb_end:
            bump = SNAP_BUMP_HEIGHT * (1.0 - (z_local - barb_peak) / max(1e-9, (barb_end - barb_peak)))

        rr = math.hypot(x, y)
        if rr > 1e-12 and bump > 0.0:
            scale = (rr + bump) / rr
            x *= scale
            y *= scale

    return x, y


def bridge_ring_pair(bm, ring_a, ring_b, reverse=False):
    n = len(ring_a)
    for j in range(n):
        j2 = (j + 1) % n
        try:
            if reverse:
                bm.faces.new((ring_a[j], ring_b[j], ring_b[j2], ring_a[j2]))
            else:
                bm.faces.new((ring_a[j], ring_a[j2], ring_b[j2], ring_b[j]))
        except ValueError:
            pass


def add_cap_face_fan(bm, ring, reverse=False):
    center = Vector((0.0, 0.0, 0.0))
    for v in ring:
        center += v.co
    center /= len(ring)
    c = bm.verts.new(center)

    n = len(ring)
    for j in range(n):
        j2 = (j + 1) % n
        try:
            if reverse:
                bm.faces.new((c, ring[j], ring[j2]))
            else:
                bm.faces.new((c, ring[j2], ring[j]))
        except ValueError:
            pass


# ============================================================
# Boolean cutter for female socket
# ============================================================

def create_female_socket_cutter(name="FemaleSocketCutter"):
    """
    Creates a D-profile cutter aligned with +Z, starting at z=0 and going to FEMALE_SOCKET_LENGTH.
    This cutter will be subtracted from the main body.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    cutter_r = min_profile_radius() * CONNECTOR_RADIUS_SCALE + CONNECTOR_CLEARANCE

    steps_z = 18
    rings = []

    for k in range(steps_z):
        u = k / (steps_z - 1)
        z = u * FEMALE_SOCKET_LENGTH
        ring = []
        for j in range(PROFILE_SAMPLES):
            theta = 2.0 * pi * j / PROFILE_SAMPLES
            x, y = d_key_xy(theta, cutter_r, D_FLAT_FRACTION)
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        bridge_ring_pair(bm, rings[i], rings[i + 1], reverse=False)

    add_cap_face_fan(bm, rings[0], reverse=True)
    add_cap_face_fan(bm, rings[-1], reverse=False)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def boolean_subtract_socket(body_obj, cutter_obj):
    mod = body_obj.modifiers.new(name="FemaleSocketBoolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter_obj

    bpy.context.view_layer.objects.active = body_obj
    body_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.data.objects.remove(cutter_obj, do_unlink=True)


def optional_voxel_remesh(obj):
    if not APPLY_VOXEL_REMESH:
        return
    mod = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = VOXEL_SIZE
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)


# ============================================================
# Mesh generation
# ============================================================

def build_straight_segment_with_connectors(points, frames):
    """
    Build ONLY a clean solid body + protruding male plug.
    Female socket is cut later using a Boolean Difference.
    """
    bm = bmesh.new()
    body_rings = []
    male_rings = []

    n = len(points)
    denom = max(1, n - 1)
    body_len = points[-1].z if len(points) > 1 else 0.0

    # --------------------------------------------------
    # Main body outer surface
    # --------------------------------------------------
    for i, (P, frame) in enumerate(zip(points, frames)):
        N, B, T = frame

        u = i / denom
        base_twist = 2.0 * pi * TWIST_TURNS * u

        lock_phase = 0.0
        if CENTER_LOCK:
            inward_phase = inward_alignment_phase(P, N, B, T)
            phase_offset = (pi / 3.0) if LOCK_TO_GAP else 0.0
            target_twist = inward_phase + phase_offset
            lock_phase = CENTER_LOCK_BLEND * target_twist

        extra_twist = base_twist + lock_phase
        Rtwist = Matrix.Rotation(extra_twist, 3, T)

        Nt = (Rtwist @ N).normalized()
        Bt = (Rtwist @ B).normalized()

        collar_boost = 0.0
        z_body = P.z
        if z_body < END_COLLAR_LENGTH:
            collar_boost = END_COLLAR_EXTRA * (1.0 - z_body / END_COLLAR_LENGTH)
        elif z_body > body_len - END_COLLAR_LENGTH:
            collar_boost = END_COLLAR_EXTRA * (1.0 - (body_len - z_body) / END_COLLAR_LENGTH)

        ring = []
        for j in range(PROFILE_SAMPLES):
            theta = 2.0 * pi * j / PROFILE_SAMPLES
            u2, v2 = profile_xy(theta)

            if collar_boost > 0.0:
                rr = math.hypot(u2, v2)
                if rr > 1e-12:
                    scale = (rr + collar_boost) / rr
                    u2 *= scale
                    v2 *= scale

            pos = P + u2 * Nt + v2 * Bt
            ring.append(bm.verts.new(pos))

        body_rings.append(ring)

    for i in range(len(body_rings) - 1):
        bridge_ring_pair(bm, body_rings[i], body_rings[i + 1], reverse=False)

    # --------------------------------------------------
    # Male plug
    # --------------------------------------------------
    male_steps = 18
    for k in range(1, male_steps + 1):
        u = k / male_steps
        z = body_len + u * MALE_CONNECTOR_LENGTH

        ring = []
        for j in range(PROFILE_SAMPLES):
            theta = 2.0 * pi * j / PROFILE_SAMPLES
            x, y = male_connector_profile_xy(theta, z_local=u * MALE_CONNECTOR_LENGTH)
            ring.append(bm.verts.new((x, y, z)))
        male_rings.append(ring)

    last_body_ring = body_rings[-1]
    if male_rings:
        bridge_ring_pair(bm, last_body_ring, male_rings[0], reverse=False)

    for i in range(len(male_rings) - 1):
        bridge_ring_pair(bm, male_rings[i], male_rings[i + 1], reverse=False)

    # cap back end of male plug
    if body_rings:
        add_cap_face_fan(bm, body_rings[0], reverse=True)
    if male_rings:
        add_cap_face_fan(bm, male_rings[-1], reverse=False)

    if MERGE_BY_DISTANCE > 0.0:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_BY_DISTANCE)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    return bm


def build_regular_swept_mesh(points, frames):
    bm = bmesh.new()
    rings = []
    n = len(points)

    denom = n if USE_TREFOIL_CURVATURE else max(1, n - 1)

    for i, (P, frame) in enumerate(zip(points, frames)):
        N, B, T = frame

        u = i / denom
        base_twist = 2.0 * pi * TWIST_TURNS * u

        lock_phase = 0.0
        if CENTER_LOCK:
            inward_phase = inward_alignment_phase(P, N, B, T)
            phase_offset = (pi / 3.0) if LOCK_TO_GAP else 0.0
            target_twist = inward_phase + phase_offset
            lock_phase = CENTER_LOCK_BLEND * target_twist

        extra_twist = base_twist + lock_phase
        Rtwist = Matrix.Rotation(extra_twist, 3, T)

        Nt = (Rtwist @ N).normalized()
        Bt = (Rtwist @ B).normalized()

        ring = []
        for j in range(PROFILE_SAMPLES):
            theta = 2.0 * pi * j / PROFILE_SAMPLES
            u2, v2 = profile_xy(theta)
            pos = P + u2 * Nt + v2 * Bt
            ring.append(bm.verts.new(pos))
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    ring_count = len(rings)
    for i in range(ring_count):
        i2 = (i + 1) % ring_count
        bridge_ring_pair(bm, rings[i], rings[i2], reverse=False)

    if MERGE_BY_DISTANCE > 0.0:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_BY_DISTANCE)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    return bm


def build_swept_mesh(points, frames):
    if (not USE_TREFOIL_CURVATURE) and ENABLE_CONNECTORS:
        return build_straight_segment_with_connectors(points, frames)
    return build_regular_swept_mesh(points, frames)


def create_object_from_bmesh(name: str, bm: bmesh.types.BMesh):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if SMOOTH_SHADE:
        for poly in obj.data.polygons:
            poly.use_smooth = True

        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(60.0)

    return obj


def apply_final_transform(obj):
    sy = -1.0 if FINAL_MIRROR_Y else 1.0

    Sx = Matrix.Scale(FINAL_UNIFORM_SCALE, 4, Vector((1, 0, 0)))
    Sy = Matrix.Scale(FINAL_UNIFORM_SCALE * sy, 4, Vector((0, 1, 0)))
    Sz = Matrix.Scale(FINAL_UNIFORM_SCALE, 4, Vector((0, 0, 1)))

    obj.matrix_world = Sx @ Sy @ Sz @ obj.matrix_world

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def export_stl(obj, path: str):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    except Exception:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True)


# ============================================================
# Main
# ============================================================

def main():
    cleanup_existing(OBJECT_NAME)

    trefoil_length, auto_segment_length = compute_auto_straight_length()
    straight_length = auto_segment_length if STRAIGHT_LENGTH is None else STRAIGHT_LENGTH

    print(f"Trefoil total length: {trefoil_length:.6f}")
    print(f"Straight segment length (1/{SEGMENT_COUNT}): {straight_length:.6f}")
    if not USE_TREFOIL_CURVATURE:
        print(f"Straight segment twist turns: {TWIST_TURNS:.6f}")

    points = sample_centerline(N_SAMPLES, straight_length)
    tangents = compute_tangents(points)
    frames = compute_parallel_transport_frames(points, tangents)

    bm = build_swept_mesh(points, frames)
    obj = create_object_from_bmesh(OBJECT_NAME, bm)

    # boolean-cut female socket only for straight connector version
    if (not USE_TREFOIL_CURVATURE) and ENABLE_CONNECTORS:
        cutter = create_female_socket_cutter()
        boolean_subtract_socket(obj, cutter)
        optional_voxel_remesh(obj)

    if APPLY_FINAL_TRANSFORM:
        apply_final_transform(obj)

    if EXPORT_STL:
        export_stl(obj, EXPORT_PATH)
        print(f"STL exported to: {EXPORT_PATH}")

    print("Done:", OBJECT_NAME)


main()