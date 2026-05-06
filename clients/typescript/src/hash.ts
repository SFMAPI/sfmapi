// Web-Crypto-based SHA256 helper. Works in browsers + Node 20.

export async function sha256Hex(data: ArrayBuffer | Uint8Array): Promise<string> {
  // Force a non-shared ArrayBuffer so SubtleCrypto accepts it on all
  // platforms; copies are cheap relative to the digest itself.
  const view = data instanceof Uint8Array
    ? data
    : new Uint8Array(data);
  const copy = new Uint8Array(view.byteLength);
  copy.set(view);
  const digest = await crypto.subtle.digest("SHA-256", copy.buffer);
  const bytes = new Uint8Array(digest);
  let out = "";
  for (let i = 0; i < bytes.length; i++) {
    const b = bytes[i] ?? 0;
    out += b.toString(16).padStart(2, "0");
  }
  return out;
}

export function asUint8(data: ArrayBuffer | Uint8Array | Blob): Promise<Uint8Array> {
  if (data instanceof Uint8Array) return Promise.resolve(data);
  if (data instanceof ArrayBuffer) return Promise.resolve(new Uint8Array(data));
  return data.arrayBuffer().then((buf) => new Uint8Array(buf));
}
