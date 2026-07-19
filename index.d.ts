// index.d.ts - TypeScript definitions for SSTcore (npm) — aligned with N-API exports

export type Vec3 = [number, number, number] | { x: number; y: number; z: number };
export type Vec3Array = Vec3[] | Float64Array | number[];

export interface EngineInfo {
  packageVersion: string;
  engineVersion: string;
  canonVersion: string;
  nodeApiVersion: number;
  numericProfile: string;
  compiler: string;
  platform: string;
  architecture: string;
}

export interface Capabilities {
  biotSavart: boolean;
  knotGeometry: boolean;
  frenetHelicity: boolean;
  magnusIntegrator: boolean;
  sstIntegrator: boolean;
  continuousReach: boolean;
  wasmFallback: boolean;
}

export interface BiotSavartInvariants {
  hCharge: number;
  hMass: number;
  aMu: number;
}

export interface FrenetFrames {
  T: Float64Array;
  N: Float64Array;
  B: Float64Array;
}

export interface CurvatureTorsion {
  curvature: number[];
  torsion: number[];
}

export interface ListBindingsResult {
  functions: string[];
  classes: string[];
  attributes: string[];
  counts: { functions: number; classes: number; attributes: number };
}

/**
 * SSTcore Node surface (native N-API). Optional members may be absent on WASM stubs.
 */
export interface SSTcoreModule {
  version: string;
  engineVersion?: string;
  canonVersion?: string;
  nodeApiVersion?: number;
  numericProfile?: string;
  nativeAddonName?: string;
  isAvailable: boolean;
  isNative: boolean;
  isWasm: boolean;
  error?: string;

  engineInfo(): EngineInfo;
  getCapabilities(): Capabilities;
  listBindings(pattern?: string, includePrivate?: boolean): ListBindingsResult;

  // Biot–Savart
  computeVelocity(curve: Vec3Array, gridPoints: Vec3Array): Float64Array;
  computeVorticity(velocity: Vec3Array, shape: [number, number, number], spacing: number): Float64Array;
  extractInterior(field: Vec3Array, shape: [number, number, number], margin: number): Float64Array;
  computeInvariants(vSub: Vec3Array, wSub: Vec3Array, rSq: number[]): BiotSavartInvariants;
  biotSavartVelocity(
    r: Vec3,
    filamentPoints: Vec3Array,
    tangentVectors: Vec3Array,
    circulation?: number,
  ): Vec3;
  biotSavartVelocityGrid(polyline: Vec3Array, grid: Vec3Array): Float64Array;

  // Field kernels / ops
  dipoleFieldAtPoint?: (...args: any[]) => any;
  biotSavartWireGrid?: (...args: any[]) => any;
  dipoleRingFieldGrid?: (...args: any[]) => any;
  biotSavartVectorPotentialGrid?: (...args: any[]) => any;
  fieldKernelsAvailable?: boolean;
  curl3dCentral?: (...args: any[]) => any;
  fieldOpsAvailable?: boolean;

  // Fluid
  computePressureField(velocityMagnitude: number[], rhoAe: number, pInfinity: number): number[];
  computeVelocityMagnitude(velocity: Vec3Array): number[];
  evolvePositionsEuler(positions: Vec3Array, velocity: Vec3Array, dt: number): Float64Array;
  computeHelicityField(velocity: Vec3Array, vorticity: Vec3Array, dV: number): number;
  swirlClockRate(dvDx: number, duDy: number): number;
  computeKineticEnergy(velocity: Vec3Array, rhoAe: number): number;

  // Frenet / helicity / RK4
  computeFrenetFrames(X: Vec3Array): FrenetFrames;
  computeCurvatureTorsion(T: Vec3Array, N: Vec3Array): CurvatureTorsion;
  computeHelicity(velocity: Vec3Array, vorticity: Vec3Array): number;
  evolveVortexKnot(positions: Vec3Array, tangents: Vec3Array, dt: number, gamma?: number): Float64Array;
  rk4Integrate(positions: Vec3Array, tangents: Vec3Array, dt: number, gamma?: number): Float64Array;

  // Knot geometry / topology
  computeWrithe(curve: Vec3Array): number;
  computeLinkingNumber(curveA: Vec3Array, curveB: Vec3Array): number;
  computeTwist?: (...args: any[]) => any;
  computeCenterlineHelicity?: (...args: any[]) => any;
  detectReconnectionCandidates?: (...args: any[]) => any;
  knotComputeBiotSavartVelocityGrid?: (...args: any[]) => any;
  knotComputeVorticityGrid?: (...args: any[]) => any;
  knotExtractInteriorField?: (...args: any[]) => any;
  computeHelicityInvariants?: (...args: any[]) => any;
  parseFseriesMulti?: (...args: any[]) => any;
  indexOfLargestFourierBlock?: (...args: any[]) => any;
  evaluateFourierBlock?: (...args: any[]) => any;
  pdFromCurve?: (...args: any[]) => any;
  loadKnot?: (...args: any[]) => any;
  getEmbeddedKnotFiles?: (...args: any[]) => any;
  getEmbeddedIdealFiles?: (...args: any[]) => any;
  knotAvailable?: boolean;

  // Integrators
  createMagnusBernoulliIntegrator?: (...args: any[]) => any;
  magnusComputeForce?: (...args: any[]) => any;
  magnusComputeSwirlCoulombAccel?: (...args: any[]) => any;
  magnusIntegratorAvailable?: boolean;
  computeSstMass(points: Vec3Array, gamma?: number): number | number[];
  sstIntegratorAvailable?: boolean;

  // SST extensions (fseries metrics)
  sampleCurveCentered?: (...args: any[]) => any;
  computeCurveMetricsFromFseries?: (...args: any[]) => any;
  curveLengthFromFseries?: (...args: any[]) => any;
  minNonNeighborDistanceFromFseries?: (...args: any[]) => any;
  reachProxyFromFseries?: (...args: any[]) => any;
  computeFilamentEnergyFromFseries?: (...args: any[]) => any;
  computeHelicityFromFseries?: (...args: any[]) => any;
  canonicalizeFseriesFileInplace?: (...args: any[]) => any;
  batchHelicityFromDir?: (...args: any[]) => any;
  compareFseriesFiles?: (...args: any[]) => any;
  sstExtensionsAvailable?: boolean;

  // Timefield / gravity / vortex / vorticity / thermo / radiation / swirl / hyperbolic / ab initio
  timeFieldAvailable?: boolean;
  hyperbolicVolumeAvailable?: boolean;
  radiationFlowAvailable?: boolean;
  swirlFieldAvailable?: boolean;
  thermoDynamicsAvailable?: boolean;
  timeEvolutionAvailable?: boolean;
  vortexRingAvailable?: boolean;
  vorticityDynamicsAvailable?: boolean;
  sstGravityAvailable?: boolean;
  abInitioAvailable?: boolean;
  ParticleEvaluator?: new (...args: any[]) => any;
  TimeEvolution?: new (...args: any[]) => any;
  GoldenNLSClosure?: new (...args: any[]) => any;

  // Python-parity resource helpers (JS layer; camelCase + snake_case)
  getResourcesDir?: () => string | null;
  getIdealTxtPath?: () => string | null;
  getKnotsFourierSeriesDir?: () => string | null;
  getKnotplotDir?: () => string | null;
  listIdealSourceFiles?: () => Record<string, string>;
  getIdealAb?: (abId: string, source?: string | null) => string | null;
  getIdealLink?: (linkId: string, source?: string | null) => string | null;
  listEmbeddedFseriesIds?: () => string[];
  loadFseriesKnot?: (label: string) => string | null;
  knotplot?: (knotId: string) => string | null;
  resolveKnotRef?: (...args: any[]) => any;
  get_resources_dir?: () => string | null;
  get_ideal_txt_path?: () => string | null;
  get_knots_fourier_series_dir?: () => string | null;
  get_knotplot_dir?: () => string | null;
  list_ideal_source_files?: () => Record<string, string>;
  get_ideal_ab?: (abId: string, source?: string | null) => string | null;
  get_ideal_link?: (linkId: string, source?: string | null) => string | null;
  list_embedded_fseries_ids?: () => string[];
  load_fseries_knot?: (label: string) => string | null;
  resolve_knot_ref?: (...args: any[]) => any;

  [key: string]: any;
}

declare const sstcore: SSTcoreModule;
export = sstcore;
