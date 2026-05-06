import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

import { SfmApiClient, SfmApiError } from "@sfmapi/client";

import { decodePoints, type DecodedPoints } from "./binary";

const $ = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T;

const baseInput = $<HTMLInputElement>("base");
const ridInput = $<HTMLInputElement>("rid");
const seqSelect = $<HTMLSelectElement>("seq");
const keyInput = $<HTMLInputElement>("key");
const loadBtn = $<HTMLButtonElement>("load");
const previewBtn = $<HTMLButtonElement>("preview");
const tilesBtn = $<HTMLButtonElement>("tiles");
const statusBox = $<HTMLDivElement>("status");
const canvasHost = $<HTMLDivElement>("canvas-host");

// ---- Three.js scaffolding --------------------------------------------------

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0d12);

const camera = new THREE.PerspectiveCamera(
  60,
  canvasHost.clientWidth / Math.max(1, canvasHost.clientHeight),
  0.01,
  10000,
);
camera.position.set(2, 2, 4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(canvasHost.clientWidth, canvasHost.clientHeight);
canvasHost.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

// World axes for orientation; tiny so they don't overpower point clouds.
scene.add(new THREE.AxesHelper(0.5));

let pointsObj: THREE.Points | null = null;

function disposePoints() {
  if (pointsObj) {
    scene.remove(pointsObj);
    pointsObj.geometry.dispose();
    (pointsObj.material as THREE.Material).dispose();
    pointsObj = null;
  }
}

function buildPoints(decoded: DecodedPoints): THREE.Points {
  const geom = new THREE.BufferGeometry();
  geom.setAttribute(
    "position",
    new THREE.BufferAttribute(decoded.positions, 3),
  );
  // sRGB byte colors -> linear floats so Three.js color management plays nice.
  const linear = new Float32Array(decoded.colors.length);
  for (let i = 0; i < decoded.colors.length; i++) {
    const v = (decoded.colors[i] ?? 0) / 255;
    linear[i] = v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  }
  geom.setAttribute("color", new THREE.BufferAttribute(linear, 3));
  geom.computeBoundingBox();
  geom.computeBoundingSphere();

  const mat = new THREE.PointsMaterial({
    size: 0.012,
    vertexColors: true,
    sizeAttenuation: true,
    transparent: false,
  });
  return new THREE.Points(geom, mat);
}

function fitCameraTo(target: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(target);
  if (box.isEmpty()) return;
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z) || 1;
  const fov = (camera.fov * Math.PI) / 180;
  const dist = (maxDim / 2) / Math.tan(fov / 2);
  camera.position.copy(center).add(new THREE.Vector3(dist, dist * 0.6, dist));
  camera.near = Math.max(dist / 1000, 0.001);
  camera.far = dist * 100;
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

// ---- API integration -------------------------------------------------------

function makeClient() {
  const baseUrl = baseInput.value.trim() || "http://localhost:8080";
  const apiKey = keyInput.value.trim();
  return new SfmApiClient({
    baseUrl,
    ...(apiKey ? { apiKey } : {}),
  });
}

function setStatus(msg: string, ok = true) {
  statusBox.textContent = msg;
  statusBox.style.borderColor = ok ? "#1d2230" : "#7c5cff";
}

async function refreshSnapshots() {
  const rid = ridInput.value.trim();
  if (!rid) {
    seqSelect.innerHTML = "";
    return;
  }
  try {
    setStatus(`Listing snapshots for ${rid}...`);
    const seqs = await makeClient().listSnapshots(rid);
    seqSelect.innerHTML = "";
    if (seqs.length === 0) {
      const opt = new Option("(no sealed snapshots)", "", true, true);
      opt.disabled = true;
      seqSelect.add(opt);
      setStatus(`No sealed snapshots for ${rid}.`, false);
      return;
    }
    for (const s of seqs.reverse()) {
      seqSelect.add(new Option(`#${s}`, String(s)));
    }
    setStatus(`Found ${seqs.length} snapshot(s). Pick one and click Load.`);
  } catch (err) {
    if (err instanceof SfmApiError) {
      setStatus(`HTTP ${err.statusCode}: ${err.message}`, false);
    } else {
      setStatus(`Failed: ${(err as Error).message}`, false);
    }
  }
}

async function loadPoints(preview: boolean) {
  const rid = ridInput.value.trim();
  const seq = Number.parseInt(seqSelect.value, 10);
  if (!rid || !Number.isFinite(seq)) {
    setStatus("Need a reconstruction id and a snapshot seq.", false);
    return;
  }
  loadBtn.disabled = true;
  previewBtn.disabled = true;
  try {
    const name = preview ? "points_preview.bin" : "points.bin";
    setStatus(`Fetching snapshot ${seq} ${name}...`);
    const t0 = performance.now();
    const buf = await makeClient().readSnapshotFile(rid, seq, name);
    const decoded = decodePoints(buf);
    const t1 = performance.now();
    disposePoints();
    pointsObj = buildPoints(decoded);
    scene.add(pointsObj);
    fitCameraTo(pointsObj);
    setStatus(
      `Loaded ${decoded.header.count.toLocaleString()} points` +
        ` (${(buf.byteLength / 1024 / 1024).toFixed(2)} MiB) in ${
          (t1 - t0).toFixed(0)
        } ms.`,
    );
  } catch (err) {
    if (err instanceof SfmApiError) {
      setStatus(`HTTP ${err.statusCode}: ${err.message}`, false);
    } else {
      setStatus(`Failed: ${(err as Error).message}`, false);
    }
  } finally {
    loadBtn.disabled = false;
    previewBtn.disabled = false;
  }
}

// ---- Tile-based progressive load ------------------------------------------

interface TileEntry {
  level: number;
  x: number;
  y: number;
  z: number;
  count: number;
  byte_size: number;
}

interface TileIndex {
  bbox_min: [number, number, number] | null;
  bbox_max: [number, number, number] | null;
  max_level: number;
  tile_count: number;
  tiles: TileEntry[];
}

async function loadTiles() {
  const rid = ridInput.value.trim();
  const seq = Number.parseInt(seqSelect.value, 10);
  if (!rid || !Number.isFinite(seq)) {
    setStatus("Need a reconstruction id and a snapshot seq.", false);
    return;
  }
  tilesBtn.disabled = true;
  loadBtn.disabled = true;
  previewBtn.disabled = true;
  try {
    const baseUrl = baseInput.value.trim() || "http://localhost:8080";
    const apiKey = keyInput.value.trim();
    const headers: Record<string, string> = {};
    if (apiKey) headers["Authorization"] = `Bearer ${apiKey}`;

    setStatus(`Fetching tile index for snapshot ${seq}...`);
    const t0 = performance.now();
    const idxResp = await fetch(
      `${baseUrl}/v1/reconstructions/${rid}/snapshots/${seq}/tiles/index.json`,
      { headers },
    );
    if (!idxResp.ok) {
      setStatus(
        `Tile index fetch failed (HTTP ${idxResp.status}); falling back to preview.`,
        false,
      );
      await loadPoints(true);
      return;
    }
    const index: TileIndex = await idxResp.json();
    if (!index.tiles.length) {
      setStatus("Tile index empty.", false);
      return;
    }
    // Render coarse-to-fine: level 0 first (so the user sees something
    // immediately), then deeper levels in parallel.
    disposePoints();
    const byLevel = new Map<number, TileEntry[]>();
    for (const t of index.tiles) {
      const arr = byLevel.get(t.level) ?? [];
      arr.push(t);
      byLevel.set(t.level, arr);
    }
    const sortedLevels = [...byLevel.keys()].sort((a, b) => a - b);

    let totalPoints = 0;
    let totalBytes = 0;

    // Each level replaces the prior one (deeper = more detail). For
    // really huge clouds we'd merge instead, but for the example
    // viewer "newest level wins" gives a snappy progressive feel.
    for (const level of sortedLevels) {
      const tiles = byLevel.get(level)!;
      const blobs = await Promise.all(
        tiles.map((t) =>
          fetch(
            `${baseUrl}/v1/reconstructions/${rid}/snapshots/${seq}/tiles/${level}/${t.x}/${t.y}/${t.z}.bin`,
            { headers },
          ).then((r) => r.arrayBuffer()),
        ),
      );
      // Concatenate decoded points into one geometry.
      let n = 0;
      for (const b of blobs) n += decodePoints(b).header.count;
      const positions = new Float32Array(n * 3);
      const colors = new Uint8Array(n * 3);
      let off = 0;
      for (const b of blobs) {
        const dec = decodePoints(b);
        positions.set(dec.positions, off * 3);
        colors.set(dec.colors, off * 3);
        off += dec.header.count;
        totalBytes += b.byteLength;
      }
      totalPoints = n;
      disposePoints();
      pointsObj = buildPoints({
        header: {
          count: n,
          bboxMin: index.bbox_min ?? [0, 0, 0],
          bboxMax: index.bbox_max ?? [0, 0, 0],
        },
        positions,
        colors,
      });
      scene.add(pointsObj);
      fitCameraTo(pointsObj);
      const elapsed = performance.now() - t0;
      setStatus(
        `Level ${level}: ${totalPoints.toLocaleString()} pts ` +
          `(${(totalBytes / 1024 / 1024).toFixed(2)} MiB total) in ${elapsed.toFixed(0)} ms`,
      );
    }
  } catch (err) {
    if (err instanceof SfmApiError) {
      setStatus(`HTTP ${err.statusCode}: ${err.message}`, false);
    } else {
      setStatus(`Failed: ${(err as Error).message}`, false);
    }
  } finally {
    tilesBtn.disabled = false;
    loadBtn.disabled = false;
    previewBtn.disabled = false;
  }
}

// ---- Wiring ----------------------------------------------------------------

ridInput.addEventListener("change", () => void refreshSnapshots());
loadBtn.addEventListener("click", () => void loadPoints(false));
previewBtn.addEventListener("click", () => void loadPoints(true));
tilesBtn.addEventListener("click", () => void loadTiles());
window.addEventListener("keydown", (e) => {
  if (e.key === "r" || e.key === "R") {
    camera.position.set(2, 2, 4);
    controls.target.set(0, 0, 0);
    controls.update();
  } else if ((e.key === "f" || e.key === "F") && pointsObj) {
    fitCameraTo(pointsObj);
  }
});
window.addEventListener("resize", () => {
  const w = canvasHost.clientWidth;
  const h = canvasHost.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
});

function animate() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();

// Restore previous session values from localStorage.
for (const [k, el] of Object.entries({
  base: baseInput,
  rid: ridInput,
  key: keyInput,
})) {
  const saved = localStorage.getItem(`sfmapi-viewer-${k}`);
  if (saved) (el as HTMLInputElement).value = saved;
  el.addEventListener("change", () => {
    localStorage.setItem(`sfmapi-viewer-${k}`, (el as HTMLInputElement).value);
  });
}
if (ridInput.value) void refreshSnapshots();
