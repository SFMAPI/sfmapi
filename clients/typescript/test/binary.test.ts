import { describe, expect, it } from "vitest";

import {
  parseDepthMap,
  parseNormalMap,
  parsePointsBinary,
} from "../src/binary.js";

const u32 = (n: number): Uint8Array => {
  const b = new Uint8Array(4);
  new DataView(b.buffer).setUint32(0, n, true);
  return b;
};

const u64 = (n: bigint): Uint8Array => {
  const b = new Uint8Array(8);
  new DataView(b.buffer).setBigUint64(0, n, true);
  return b;
};

const f32 = (n: number): Uint8Array => {
  const b = new Uint8Array(4);
  new DataView(b.buffer).setFloat32(0, n, true);
  return b;
};

const concat = (...parts: ArrayLike<number>[]): ArrayBuffer => {
  const total = parts.reduce((acc, p) => acc + p.length, 0);
  const out = new Uint8Array(total);
  let off = 0;
  for (const p of parts) {
    out.set(p as Uint8Array, off);
    off += p.length;
  }
  return out.buffer;
};

describe("parsePointsBinary", () => {
  it("decodes a single-record blob", () => {
    const buf = concat(
      new Uint8Array([0x53, 0x46, 0x4d, 0x50, 0x33, 0x44, 0x00, 0x00]), // magic
      u32(1), // version
      u64(1n), // count
      f32(0), f32(0), f32(0), // bbox_min
      f32(1), f32(2), f32(3), // bbox_max
      // record:
      f32(1), f32(2), f32(3),
      new Uint8Array([255, 128, 64, 0]), // rgb + pad
      new Uint8Array([5, 0]), // track_len uint16 le
      u64(42n),
    );
    const parsed = parsePointsBinary(buf);
    expect(parsed.count).toBe(1);
    expect(parsed.records).toHaveLength(1);
    const r0 = parsed.records[0]!;
    expect(r0.xyz).toEqual([1, 2, 3]);
    expect(r0.rgb).toEqual([255, 128, 64]);
    expect(r0.track_len).toBe(5);
    expect(r0.point3d_id).toBe(42n);
  });

  it("rejects bad magic", () => {
    const buf = new ArrayBuffer(44);
    expect(() => parsePointsBinary(buf)).toThrow(/bad magic/);
  });
});

describe("parseDepthMap", () => {
  it("decodes a 2x2 depth map", () => {
    const buf = concat(
      new Uint8Array([0x53, 0x46, 0x4d, 0x44, 0x50, 0x54, 0x48, 0x00]), // magic
      u32(1), // version
      u32(2), u32(2), // w, h
      f32(1), f32(4), // depth_min, depth_max
      u32(0), // _pad
      f32(1), f32(2), f32(3), f32(4),
    );
    const dm = parseDepthMap(buf);
    expect(dm.width).toBe(2);
    expect(dm.height).toBe(2);
    expect(dm.depth_min).toBeCloseTo(1);
    expect(dm.depth_max).toBeCloseTo(4);
    expect(Array.from(dm.pixels)).toEqual([1, 2, 3, 4]);
  });

  it("rejects bad magic", () => {
    const buf = new ArrayBuffer(32);
    expect(() => parseDepthMap(buf)).toThrow(/bad magic/);
  });
});

describe("parseNormalMap", () => {
  it("decodes a 1x1 normal map", () => {
    const buf = concat(
      new Uint8Array([0x53, 0x46, 0x4d, 0x4e, 0x52, 0x4d, 0x00, 0x00]), // magic
      u32(1),
      u32(1), u32(1),
      f32(0), f32(0), u32(0),
      f32(0), f32(0), f32(1), // upward normal
    );
    const nm = parseNormalMap(buf);
    expect(nm.width).toBe(1);
    expect(nm.height).toBe(1);
    expect(Array.from(nm.pixels)).toEqual([0, 0, 1]);
  });
});
