// AUDIT P4: only the mapper names are used. zeMapCatalog.json (466 kB, with image URLs and
// addon ids) was bundled whole into the main JS. zeMapMappers.json is generated from it
// (same keys, same order: { map: mapper }); regenerate with scripts/build_map_mappers.py.
import zeMapMappers from './zeMapMappers.json';

export interface S2ZEMapMeta {
  mapper: string;
  image?: string;
  addon?: string;
}

export const S2ZE_OFFICIAL_MAPS_CATALOG: Record<string, S2ZEMapMeta> = Object.fromEntries(
  Object.entries(zeMapMappers as Record<string, string>).map(([k, mapper]) => [k, { mapper }]),
);

/**
 * Look up exact real mapper name for any CS2 map from the official database.
 */
export function lookupS2zeMapper(mapKey: string): string | null {
  if (!mapKey) return null;
  const clean = mapKey.trim().toLowerCase();
  
  if (S2ZE_OFFICIAL_MAPS_CATALOG[clean]) {
    return S2ZE_OFFICIAL_MAPS_CATALOG[clean].mapper;
  }
  
  const stripped = clean.replace(/_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i, '');
  if (S2ZE_OFFICIAL_MAPS_CATALOG[stripped]) {
    return S2ZE_OFFICIAL_MAPS_CATALOG[stripped].mapper;
  }
  
  // Substring match
  for (const [k, meta] of Object.entries(S2ZE_OFFICIAL_MAPS_CATALOG)) {
    if (k.length > 5 && (clean.includes(k) || k.includes(clean))) {
      return meta.mapper;
    }
  }
  return null;
}

/**
 * Exact catalog hit only (map name, or the name without a _p / _v5 style suffix); no substring guessing.
 * Used to correct the keyword-based mapper guesses in getMapTierAndMapper.
 */
export function lookupS2zeMapperExact(mapKey: string): string | null {
  if (!mapKey) return null;
  const clean = mapKey.trim().toLowerCase();
  if (S2ZE_OFFICIAL_MAPS_CATALOG[clean]) return S2ZE_OFFICIAL_MAPS_CATALOG[clean].mapper;
  const stripped = clean.replace(/_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i, '');
  return S2ZE_OFFICIAL_MAPS_CATALOG[stripped]?.mapper ?? null;
}
