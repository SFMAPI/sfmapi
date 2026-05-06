// Type-only mirror of `app/schemas/api/scene.py`. These types ship in
// the SDK so TypeScript clients can consume sealed snapshots, mesh
// manifests, dense outputs, pose priors, etc. without runtime
// validators.
//
// Quaternion convention: Hamilton (w, x, y, z), scalar-first — same
// as the server's wire format.

// ----- core geometry -------------------------------------------------------

export interface Rotation {
  /** Hamilton quaternion, scalar-first. */
  w: number;
  x: number;
  y: number;
  z: number;
}

export interface Rigid3 {
  rotation: Rotation;
  translation: [number, number, number];
}

export interface Sim3 {
  rotation: Rotation;
  translation: [number, number, number];
  scale: number;
}

export interface GpsCoord {
  lat: number;
  lng: number;
  alt?: number | null;
  horiz_accuracy_m?: number | null;
  vert_accuracy_m?: number | null;
}

export interface ImuMeasurement {
  timestamp_ns: number;
  gyro: [number, number, number];
  accel: [number, number, number];
}

export interface PosePrior {
  cam_from_world: Rigid3;
  /** 36-float row-major 6x6 covariance over (rx, ry, rz, tx, ty, tz). */
  covariance?: number[] | null;
  gps?: GpsCoord | null;
  timestamp_ns?: number | null;
  imu?: ImuMeasurement | null;
}

// ----- camera --------------------------------------------------------------

/** Wire constant for equirectangular-panorama cameras. */
export const SPHERICAL_CAMERA_MODEL = "SPHERICAL" as const;

export interface Camera {
  camera_id: number;
  /** COLMAP camera-model name (`SIMPLE_RADIAL`, `PINHOLE`, ...) or
   * the `"SPHERICAL"` constant for equirectangular panoramas. */
  model: string;
  width: number;
  height: number;
  /** Empty for `model === "SPHERICAL"`; model-specific otherwise. */
  params: number[];
  has_prior_focal_length?: boolean;
}

export function isSphericalCamera(c: Pick<Camera, "model">): boolean {
  return c.model === SPHERICAL_CAMERA_MODEL;
}

// ----- image keypoints, tracks, image pose --------------------------------

export interface Point2D {
  xy: [number, number];
  /** `null` when the keypoint is not (yet) part of a 3D track. */
  point3d_id?: number | null;
}

export interface ImagePose {
  image_id: number;
  name: string;
  camera_id: number;
  cam_from_world: Rigid3;
  points2D?: Point2D[];
}

export interface TrackElement {
  image_id: number;
  point2d_idx: number;
}

export interface Track {
  point3d_id: number;
  elements?: TrackElement[];
}

// ----- rig + frame --------------------------------------------------------

export interface Rig {
  rig_id: number;
  ref_sensor_id: number;
  /** Sensor-id (string) → cam_from_rig transform. */
  sensor_from_rig: Record<string, Rigid3>;
}

export interface Frame {
  frame_id: number;
  rig_id: number;
  rig_from_world: Rigid3;
  /** Sensor-id (string) → image_id binding. */
  data_ids?: Record<string, number>;
}

// ----- two-view geometry + correspondences --------------------------------

export type TwoViewGeometryType =
  | "undefined"
  | "degenerate"
  | "calibrated"
  | "uncalibrated"
  | "planar"
  | "panoramic"
  | "planar_or_panoramic"
  | "watermark"
  | "multiple";

export interface TwoViewGeometry {
  image_id1: number;
  image_id2: number;
  type: TwoViewGeometryType;
  num_inliers: number;
  /** 9-float row-major 3x3; only the matrix matching `type` is set. */
  F?: number[] | null;
  E?: number[] | null;
  H?: number[] | null;
  inlier_matches?: Array<[number, number]>;
}

export interface CorrespondencePair {
  image_id1: number;
  image_id2: number;
  num_matches: number;
  /** Raw (pre-verification) matches as `(kp_idx_1, kp_idx_2)` pairs. */
  matches?: Array<[number, number]>;
}

// ----- pose graph ---------------------------------------------------------

export interface PoseGraphEdge {
  image_id1: number;
  image_id2: number;
  cam2_from_cam1: Rigid3;
  weight?: number;
}

export interface PoseGraph {
  nodes?: ImagePose[];
  edges?: PoseGraphEdge[];
}

// ----- snapshot file wrappers --------------------------------------------

export interface CamerasFile {
  cameras: Camera[];
}

export interface ImagesFile {
  images: ImagePose[];
}

export interface RigsFile {
  rigs: Rig[];
}

export interface FramesFile {
  frames: Frame[];
}

export interface TwoViewGeometriesFile {
  pairs: TwoViewGeometry[];
}

export interface CorrespondenceGraphFile {
  pairs: CorrespondencePair[];
}

export interface PoseGraphFile {
  pose_graph: PoseGraph;
}

// ----- localization -------------------------------------------------------

export interface LocalizationResult {
  success: boolean;
  cam_from_world?: Rigid3 | null;
  num_inliers?: number;
  /** Flat list of `(query_keypoint_idx, point3d_id)` inliers. */
  inlier_matches?: Array<[number, number]>;
  diagnostics?: Record<string, unknown>;
}

// ----- dense MVS ---------------------------------------------------------

export interface DepthMapInfo {
  image_id: number;
  image_name: string;
  width: number;
  height: number;
  depth_min: number;
  depth_max: number;
  has_normal_map?: boolean;
}

export interface DenseSummary {
  num_images: number;
  num_depth_maps: number;
  num_normal_maps: number;
  fused_points: number;
  bbox_min?: [number, number, number] | null;
  bbox_max?: [number, number, number] | null;
}

export interface DenseManifestFile {
  summary: DenseSummary;
  depth_maps?: DepthMapInfo[];
}

// ----- mesh --------------------------------------------------------------

export type MeshMethod = "poisson" | "delaunay";

export interface MeshSummary {
  method: MeshMethod;
  num_vertices: number;
  num_faces: number;
  has_vertex_colors?: boolean;
  has_vertex_normals?: boolean;
  bbox_min?: [number, number, number] | null;
  bbox_max?: [number, number, number] | null;
}

export interface MeshFile {
  summary: MeshSummary;
  /** Populated by the API at read-time; absolute under `/v1/...`. */
  mesh_url?: string | null;
}
