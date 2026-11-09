import zeMapCatalog from './zeMapCatalog.json';

export interface S2ZEMapMeta {
  mapper: string;
  image?: string;
  addon?: string;
}

export const S2ZE_OFFICIAL_MAPS_CATALOG: Record<string, S2ZEMapMeta> = zeMapCatalog as Record<string, S2ZEMapMeta>;

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
