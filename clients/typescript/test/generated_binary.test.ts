// Verifies the generated SDK's binary wire-format parsers decode
// canonical byte buffers correctly. Synthesizes payloads via
// DataView so the test runs without a live server; cross-language
// parity is enforced by Python's
// test_e_generated_ergonomics.py::test_parse_*_round_trip_against_server_encoder.

import { describe, expect, it } from "vitest";

import {
  parsePointsBinary,
  parseDepthMap,
  parseNormalMap,
  WireFormatError,
} from "../src/_generated/client.js";

const POINTS_HEADER_SIZE = 44;
const POINTS_RECORD_SIZE = 26;
const MAP_HEADER_SIZE = 32;

function writeMagic(view: DataView, magic: number[]) {
  for (let i = 0; i < magic.length; i++) view.setUint8(i, magic[i]!);
}

function makePointsBlob(points: Array<{
  xyz: [number, number, number];
  rgb: [number, number, number];
  track_len: number;
  point3d_id: bigint;
}>, bboxMin: [number, number, number], bboxMax: [number, number, number]): ArrayBuffer {
  const total = POINTS_HEADER_SIZE + points.length * POINTS_RECORD_SIZE;
  const buf = new ArrayBuffer(total);
  const view = new DataView(buf);
  writeMagic(view, [0x53, 0x46, 0x4d, 0x50, 0x33, 0x44, 0x00, 0x00]);
  view.setUint32(8, 1, true);                        // version
  view.setBigUint64(12, BigInt(points.length), true); // count
  view.setFloat32(20, bboxMin[0], true);
  view.setFloat32(24, bboxMin[1], true);
  view.setFloat32(28, bboxMin[2], true);
  view.setFloat32(32, bboxMax[0], true);
  view.setFloat32(36, bboxMax[1], true);
  view.setFloat32(40, bboxMax[2], true);
  for (let i = 0; i < points.length; i++) {
    const off = POINTS_HEADER_SIZE + i * POINTS_RECORD_SIZE;
    const p = points[i]!;
    view.setFloat32(off, p.xyz[0], true);
    view.setFloat32(off + 4, p.xyz[1], true);
    view.setFloat32(off + 8, p.xyz[2], true);
    view.setUint8(off + 12, p.rgb[0]);
    view.setUint8(off + 13, p.rgb[1]);
    view.setUint8(off + 14, p.rgb[2]);
    view.setUint8(off + 15, 0); // padding
    view.setUint16(off + 16, p.track_len, true);
    view.setBigUint64(off + 18, p.point3d_id, true);
  }
  return buf;
}

function makeDepthBlob(width: number, height: number, dmin: number, dmax: number, pixels: Float32Array): ArrayBuffer {
  const total = MAP_HEADER_SIZE + width * height * 4;
  const buf = new ArrayBuffer(total);
  const view = new DataView(buf);
  writeMagic(view, [0x53, 0x46, 0x4d, 0x44, 0x50, 0x54, 0x48, 0x00]);
  view.setUint32(8, 1, true);
  view.setUint32(12, width, true);
  view.setUint32(16, height, true);
  view.setFloat32(20, dmin, true);
  view.setFloat32(24, dmax, true);
  view.setUint32(28, 0, true); // pad
  new Float32Array(buf, MAP_HEADER_SIZE, width * height).set(pixels);
  return buf;
}

function makeNormalBlob(width: number, height: number, pixels: Float32Array): ArrayBuffer {
  const total = MAP_HEADER_SIZE + width * height * 3 * 4;
  const buf = new ArrayBuffer(total);
  const view = new DataView(buf);
  writeMagic(view, [0x53, 0x46, 0x4d, 0x4e, 0x52, 0x4d, 0x00, 0x00]);
  view.setUint32(8, 1, true);
  view.setUint32(12, width, true);
  view.setUint32(16, height, true);
  view.setFloat32(20, 0, true);
  view.setFloat32(24, 0, true);
  view.setUint32(28, 0, true);
  new Float32Array(buf, MAP_HEADER_SIZE, width * height * 3).set(pixels);
  return buf;
}

describe("generated TS parsePointsBinary", () => {
  it("round-trips a synthesized 2-point payload", () => {
    const buf = makePointsBlob(
      [
        { xyz: [1, 2, 3], rgb: [255, 0, 0], track_len: 5, point3d_id: 100n },
        { xyz: [4.5, -1.5, 0.25], rgb: [0, 128, 255], track_len: 12, point3d_id: 0xDEADBEEFn },
      ],
      [0, -1.5, 0],
      [4.5, 2, 3],
    );
    const out = parsePointsBinary(buf);
    expect(out.count).toBe(2);
    expect(out.bbox_min).toEqual([0, -1.5, 0]);
    expect(out.bbox_max).toEqual([4.5, 2, 3]);
    expect(out.records[0]!.point3d_id).toBe(100n);
    expect(out.records[0]!.xyz).toEqual([1, 2, 3]);
    expect(out.records[0]!.rgb).toEqual([255, 0, 0]);
    expect(out.records[0]!.track_len).toBe(5);
    expect(out.records[1]!.point3d_id).toBe(0xDEADBEEFn);
  });

  it("rejects bad magic with WireFormatError", () => {
    const buf = new ArrayBuffer(POINTS_HEADER_SIZE);
    new DataView(buf).setUint32(0, 0xCAFEBABE, true);
    expect(() => parsePointsBinary(buf)).toThrow(WireFormatError);
  });

  it("rejects short buffer", () => {
    expect(() => parsePointsBinary(new ArrayBuffer(8))).toThrow(WireFormatError);
  });
});

describe("generated TS parseDepthMap", () => {
  it("round-trips a synthesized 3x2 depth map", () => {
    const pixels = new Float32Array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]);
    const buf = makeDepthBlob(3, 2, 0.5, 3.0, pixels);
    const out = parseDepthMap(buf);
    expect(out.width).toBe(3);
    expect(out.height).toBe(2);
    expect(out.depth_min).toBe(0.5);
    expect(out.depth_max).toBe(3.0);
    expect(Array.from(out.pixels)).toEqual(Array.from(pixels));
  });

  it("rejects short buffer", () => {
    expect(() => parseDepthMap(new ArrayBuffer(0))).toThrow(WireFormatError);
  });
});

describe("generated TS parseNormalMap", () => {
  it("round-trips a synthesized 2x1 normal map", () => {
    const pixels = new Float32Array([0, 1, 0, 0, 0, 1]);
    const buf = makeNormalBlob(2, 1, pixels);
    const out = parseNormalMap(buf);
    expect(out.width).toBe(2);
    expect(out.height).toBe(1);
    expect(Array.from(out.pixels)).toEqual(Array.from(pixels));
  });

  it("rejects bad magic", () => {
    const buf = new ArrayBuffer(MAP_HEADER_SIZE);
    new DataView(buf).setUint32(0, 0xCAFEBABE, true);
    expect(() => parseNormalMap(buf)).toThrow(WireFormatError);
  });
});
