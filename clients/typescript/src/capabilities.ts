// Type-only mirror of `app/core/capabilities.py`. Keep this file in
// lock-step with the server's registry — the canonical capability
// names are part of the wire standard.

export interface BackendInfo {
  name: string;
  version: string;
  vendor?: string;
}

/** Wire schema version of the Capabilities envelope. Bump when the
 * *shape* changes (new top-level fields, type changes); independent
 * of the feature flags themselves. */
export const CAPABILITIES_SCHEMA_VERSION = 1;

export interface Capabilities {
  /** Wire schema version. See {@link CAPABILITIES_SCHEMA_VERSION}. */
  schema_version: number;
  backend: BackendInfo;
  /** Flat dict from canonical capability name to bool. Absence means
   * "unsupported"; clients MUST treat unknown keys as opaque. */
  features: Record<string, boolean>;
}

/** CORE capabilities — every conforming server advertises these as
 * `true`. */
export const CORE_CAPABILITIES = [
  "projects.crud",
  "datasets.crud",
  "images.crud",
  "uploads.chunked",
  "jobs.read",
  "events.sse",
  "spec.read",
] as const;

/** OPTIONAL capabilities — backends report any subset. */
export const OPTIONAL_CAPABILITIES = [
  // Feature pipeline (legacy bundled flag)
  "features.extract",
  "matches.exhaustive",
  "matches.sequential",
  "matches.spatial",
  "matches.vocabtree",
  "matches.verify",
  // Per-extractor
  "features.extract.sift",
  "features.extract.superpoint",
  "features.extract.aliked",
  "features.extract.disk",
  "features.extract.r2d2",
  "features.extract.d2net",
  // Pair-selection strategies
  "pairs.exhaustive",
  "pairs.sequential",
  "pairs.spatial",
  "pairs.vocabtree",
  "pairs.retrieval",
  "pairs.from_poses",
  // Per-matcher
  "matchers.nn-mutual",
  "matchers.nn-ratio",
  "matchers.superglue",
  "matchers.lightglue",
  "matchers.loftr",
  "matchers.mast3r",
  // Mapping
  "map.incremental",
  "map.global",
  "map.hierarchical",
  "map.spherical",
  // Refinement
  "ba.standard",
  "ba.two_stage",
  "ba.featuremetric",
  "triangulate.retri",
  "relocalize.images",
  "pgo.optimize",
  // Multi-session / map operations
  "recon.merge",
  // Multi-image localization
  "localize.batch",
  "localize.sequence",
  // Output
  "export.ply",
  "export.nvm",
  "export.colmap_text",
  "export.colmap_bin",
  "export.nerfstudio",
  "export.gaussian_splatting",
  "export.instant_ngp",
  "export.kapture",
  // Dense MVS
  "dense.patch_match_stereo",
  "dense.stereo_fusion",
  // Mesh + texture
  "mesh.poisson",
  "mesh.delaunay",
  "mesh.texture",
  // Retrieval / similarity
  "similarity.dhash",
  "similarity.vlad",
  // Localization
  "localize.from_memory",
  // Geometry tooling
  "georegister.sim3",
  "spherical.to_cubemap",
  "spherical.render_cubemap",
  // Inputs
  "pose_priors.read_write",
  "inputs.imu",
  "inputs.timestamps",
  // Data ingest
  "video.frame_extract",
  "import.kapture",
  // Snapshot inspection
  "observations.by_image",
  "observations.by_point",
  // Segmentation
  "segment.sam",
] as const;

export type CoreCapability = (typeof CORE_CAPABILITIES)[number];
export type OptionalCapability = (typeof OPTIONAL_CAPABILITIES)[number];
export type CanonicalCapability = CoreCapability | OptionalCapability;

/** Returns true iff the capabilities snapshot advertises `name`. */
export function supports(caps: Capabilities, name: string): boolean {
  return Boolean(caps.features?.[name]);
}
