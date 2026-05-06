/**
 * Decoder for `application/x-sfm-points-v1`.
 *
 * Wire format (mirrors `app/schemas/points_binary.py`):
 *
 *   Header (44 bytes, little-endian):
 *     magic      8 bytes = "SFMP3D\0\0"
 *     version    uint32  = 1
 *     count      uint64
 *     bbox_min   3 x float32 (12 B)
 *     bbox_max   3 x float32 (12 B)
 *
 *   Each record (26 bytes, little-endian):
 *     xyz        3 x float32 (12)
 *     rgb        3 x uint8   (3)
 *     _pad       1 x uint8   (1)
 *     track_len  uint16      (2)
 *     point3d_id uint64      (8)
 */

const MAGIC = "SFMP3D\0\0";
export const HEADER_SIZE = 44;
export const RECORD_SIZE = 26;

export interface PointsHeader {
  count: number;
  bboxMin: [number, number, number];
  bboxMax: [number, number, number];
}

export interface DecodedPoints {
  header: PointsHeader;
  /** Float32Array of length 3*count: [x0,y0,z0, x1,y1,z1, ...]. */
  positions: Float32Array;
  /** Uint8Array of length 3*count: [r0,g0,b0, r1,g1,b1, ...]. */
  colors: Uint8Array;
}

export function readHeader(buf: ArrayBuffer): PointsHeader {
  if (buf.byteLength < HEADER_SIZE) {
    throw new Error(`buffer too small for header (got ${buf.byteLength} bytes)`);
  }
  const view = new DataView(buf);
  const magicBytes = new Uint8Array(buf, 0, 8);
  let magic = "";
  for (let i = 0; i < 8; i++) magic += String.fromCharCode(magicBytes[i] ?? 0);
  if (magic !== MAGIC) {
    throw new Error(`bad magic (got ${JSON.stringify(magic)})`);
  }
  const version = view.getUint32(8, true);
  if (version !== 1) throw new Error(`unsupported points version: ${version}`);
  // BigInt because uint64. Convert to Number; counts above 2^53 don't happen.
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
  return { count, bboxMin, bboxMax };
}

export function decodePoints(buf: ArrayBuffer): DecodedPoints {
  const header = readHeader(buf);
  const expectedSize = HEADER_SIZE + RECORD_SIZE * header.count;
  if (buf.byteLength < expectedSize) {
    throw new Error(
      `buffer truncated: have ${buf.byteLength}, expected ${expectedSize} for ${header.count} points`,
    );
  }
  const positions = new Float32Array(header.count * 3);
  const colors = new Uint8Array(header.count * 3);
  // The records are tightly packed (26 B) so DataView is the safe path.
  const view = new DataView(buf);
  for (let i = 0; i < header.count; i++) {
    const off = HEADER_SIZE + i * RECORD_SIZE;
    positions[i * 3 + 0] = view.getFloat32(off + 0, true);
    positions[i * 3 + 1] = view.getFloat32(off + 4, true);
    positions[i * 3 + 2] = view.getFloat32(off + 8, true);
    colors[i * 3 + 0] = view.getUint8(off + 12);
    colors[i * 3 + 1] = view.getUint8(off + 13);
    colors[i * 3 + 2] = view.getUint8(off + 14);
  }
  return { header, positions, colors };
}
