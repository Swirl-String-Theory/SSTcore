export type KnotCatalogSource = 'ideal' | 'fseries' | 'knotplot';

export interface KnotCatalogEntry {
  knotId?: string;
  label?: string;
  components?: unknown[];
  L?: number;
  D?: number;
  family?: string;
  status?: string;
  [key: string]: unknown;
}

export interface KnotCatalog {
  source: KnotCatalogSource;
  ids: string[];
  db: Record<string, KnotCatalogEntry>;
}

export declare const CATALOG_FILES: Record<
  KnotCatalogSource,
  { file: string; idsName: string; dbName: string }
>;

export function loadIdealCatalog(): KnotCatalog;
export function loadFseriesCatalog(): KnotCatalog;
export function loadKnotplotCatalog(): KnotCatalog;
export function loadAllKnotCatalogs(): {
  ideal: KnotCatalog;
  fseries: KnotCatalog;
  knotplot: KnotCatalog;
};
export function catalogPaths(): Record<KnotCatalogSource, string>;
