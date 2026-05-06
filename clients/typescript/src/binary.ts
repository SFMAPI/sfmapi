// Wire-format binary readers — keep in sync with
// `app/schemas/points_binary.py` and `app/schemas/depth_map_binary.py`.

const MAGIC_POINTS = [0x53, 0x46, 0x4d, 0x50, 0x33, 0x44, 0x00, 0x00]; // "SFMP3D\0\0"
const MAGIC_DEPTH = [0x53, 0x46, 0x4d, 0x44, 0x50, 0x54, 0x48, 0x00]; // "SFMDPTH\0"
const MAGIC_NORMAL = [0x53, 0x46, 0x4d, 0x4e, 0x52, 0x4d, 0x00, 0x00]; // "SFMNRM\0\0"

const POINTS_HEADER_SIZE = 44;
const POINTS_RECORD_SIZE = 26;
const MAP_HEADER_SIZE = 32;

function _eqMagic(view: DataView, expected: number[]): boolean {
  for (let i = 0; i < expected.length; i++) {
    if (view.getUint8(i) !== expected[i]) return false;
  }
  return true;
}

// ---- application/x-sfm-points-v1 ----------------------------------------

export interface Point3DRecord {
  point3d_id: bigint;
  xyz: [number, number, number];
  rgb: [number, number, number];
  track_len: number;
}

export interface PointsBinary {
  count: number;
  bbox_min: [number, number, number];
  bbox_max: [number, number, number];
  records: Point3DRecord[];
}

export function parsePointsBinary(buffer: ArrayBuffer): PointsBinary {
  if (buffer.byteLength < POINTS_HEADER_SIZE) {
    throw new Error(`points-binary: buffer too small for header`);
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_POINTS)) {
    throw new Error("points-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) {
    throw new Error(`points-binary: unknown version ${version}`);
  }
  const count = Number(view.getBigUint64(12, true));
  const bboxMin: [number, number, number] = [
    view.getFloat32(20, true),
    view.getFloat32(24, true),
    view.getFloat32(28, true),
  ];
  const bboxMax: [number, number, number] = [
    view.getFloat32(32, true),
    view.getFloat32(36, true),
    view.getFloat32(40, true),
  ];
  const expected = POINTS_HEADER_SIZE + count * POINTS_RECORD_SIZE;
  if (buffer.byteLength < expected) {
    throw new Error(
      `points-binary: body short — got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const records: Point3DRecord[] = new Array(count);
  for (let i = 0; i < count; i++) {
    const off = POINTS_HEADER_SIZE + i * POINTS_RECORD_SIZE;
    records[i] = {
      xyz: [
        view.getFloat32(off, true),
        view.getFloat32(off + 4, true),
        view.getFloat32(off + 8, true),
      ],
      rgb: [
        view.getUint8(off + 12),
        view.getUint8(off + 13),
        view.getUint8(off + 14),
      ],
      track_len: view.getUint16(off + 16, true),
      point3d_id: view.getBigUint64(off + 18, true),
    };
  }
  return { count, bbox_min: bboxMin, bbox_max: bboxMax, records };
}

// ---- application/x-sfm-depth-v1 -----------------------------------------

export interface DepthMap {
  width: number;
  height: number;
  depth_min: number;
  depth_max: number;
  /** Row-major float32 array of length `width * height`. */
  pixels: Float32Array;
}

export function parseDepthMap(buffer: ArrayBuffer): DepthMap {
  if (buffer.byteLength < MAP_HEADER_SIZE) {
    throw new Error("depth-binary: buffer too small for header");
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_DEPTH)) {
    throw new Error("depth-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) throw new Error(`depth-binary: unknown version ${version}`);
  const width = view.getUint32(12, true);
  const height = view.getUint32(16, true);
  const depthMin = view.getFloat32(20, true);
  const depthMax = view.getFloat32(24, true);
  const pixelCount = width * height;
  const expected = MAP_HEADER_SIZE + pixelCount * 4;
  if (buffer.byteLength < expected) {
    throw new Error(
      `depth-binary: body short — got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const pixels = new Float32Array(buffer, MAP_HEADER_SIZE, pixelCount);
  return { width, height, depth_min: depthMin, depth_max: depthMax, pixels };
}

// ---- application/x-sfm-normal-v1 ----------------------------------------

export interface NormalMap {
  width: number;
  height: number;
  /** Row-major channels-last float32 of length `width * height * 3`. */
  pixels: Float32Array;
}

export function parseNormalMap(buffer: ArrayBuffer): NormalMap {
  if (buffer.byteLength < MAP_HEADER_SIZE) {
    throw new Error("normal-binary: buffer too small for header");
  }
  const view = new DataView(buffer);
  if (!_eqMagic(view, MAGIC_NORMAL)) {
    throw new Error("normal-binary: bad magic");
  }
  const version = view.getUint32(8, true);
  if (version !== 1) throw new Error(`normal-binary: unknown version ${version}`);
  const width = view.getUint32(12, true);
  const height = view.getUint32(16, true);
  const expected = MAP_HEADER_SIZE + width * height * 3 * 4;
  if (buffer.byteLength < expected) {
    throw new Error(
      `normal-binary: body short — got ${buffer.byteLength}, expected ${expected}`,
    );
  }
  const pixels = new Float32Array(buffer, MAP_HEADER_SIZE, width * height * 3);
  return { width, height, pixels };
}
