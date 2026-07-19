export interface KnotResolution {
  ref: string;
  source: 'ideal' | 'fremlin' | 'knotplot' | string;
  role: string;
  canonicalAbId: string | null;
  nativeLength: number | null;
  ropelength: number | null;
  closureGap: number | null;
  fremlinLabel: string | null;
  knotplotName: string | null;
  idealXml: string | null;
  bundlePath: string;
}

export interface ResourceHelpers {
  getResourcesDir(): string | null;
  getIdealTxtPath(): string | null;
  getKnotsFourierSeriesDir(): string | null;
  getKnotplotDir(): string | null;
  listIdealSourceFiles(): Record<string, string>;
  getIdealAb(abId: string, source?: string | null): string | null;
  getIdealLink(linkId: string, source?: string | null): string | null;
  listEmbeddedFseriesIds(): string[];
  loadFseriesKnot(label: string): string | null;
  knotplot(knotId: string): string | null;
  resolveKnotRef(
    ref: string,
    source?: string | null,
    prefer?: string[] | null,
    options?: { requireRole?: string; require_role?: string },
  ): KnotResolution | null;

  // snake_case Python aliases
  get_resources_dir(): string | null;
  get_ideal_txt_path(): string | null;
  get_knots_fourier_series_dir(): string | null;
  get_knotplot_dir(): string | null;
  list_ideal_source_files(): Record<string, string>;
  get_ideal_ab(abId: string, source?: string | null): string | null;
  get_ideal_link(linkId: string, source?: string | null): string | null;
  list_embedded_fseries_ids(): string[];
  load_fseries_knot(label: string): string | null;
  resolve_knot_ref(
    ref: string,
    source?: string | null,
    prefer?: string[] | null,
    options?: { requireRole?: string; require_role?: string },
  ): KnotResolution | null;
}

export declare const IDEAL_SOURCE_FILES: Record<string, string>;

export function attachResourceHelpers<T extends object>(exportsObj: T, packageRoot: string): T & ResourceHelpers;

export function createResourceHelpers(
  packageRoot: string,
  native?: object,
): {
  camel: Omit<ResourceHelpers, keyof { get_resources_dir: unknown }>;
  snake: Record<string, Function>;
  IDEAL_SOURCE_FILES: Record<string, string>;
};
