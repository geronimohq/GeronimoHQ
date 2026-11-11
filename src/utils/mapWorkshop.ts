import { useEffect, useState } from 'react';

/**
 * Where a map lives on the Steam Workshop, and who made it, worked out while the site is built
 * (scripts/resolve_workshop_maps.py writes /data/map_workshop.json for every map that is being played).
 * Also the Steam map collections of each server (/data/server_collections.json, the same file the desktop app reads).
 * Both files are optional: when one cannot be loaded the cards simply fall back to a workshop search link.
 */
export interface MapWorkshopEntry {
  id: string;
  mapper: string;
}

export interface MapCollectionLink {
  id: string;
  /** the collection's own name from server_collections.json (used as the tooltip) */
  label: string;
  /** what the link says: "Map collection", or "Map collection (ZE)" / "(ZM)" when a server has one list per map type */
  text: string;
}

export interface MapWorkshopData {
  maps: Record<string, MapWorkshopEntry>;
  /** server id -> its map collections (kind "maps" only) */
  collections: Record<string, MapCollectionLink[]>;
}

const EMPTY: MapWorkshopData = { maps: {}, collections: {} };
const ID_RE = /^\d{6,}$/;
const STEAM_ITEM = 'https://steamcommunity.com/sharedfiles/filedetails/?id=';

/** 'workshop/123/ZM_Foo' -> 'zm_foo' */
export function mapKey(raw?: string): string {
  return (raw || '').replace(/\\/g, '/').split('/').pop()!.trim().toLowerCase();
}

export function parseMapWorkshop(mapsJson: unknown, collectionsJson: unknown): MapWorkshopData {
  const maps: Record<string, MapWorkshopEntry> = {};
  const rawMaps = (mapsJson as { maps?: Record<string, { id?: unknown; mapper?: unknown }> } | null)?.maps;
  if (rawMaps && typeof rawMaps === 'object') {
    for (const [k, v] of Object.entries(rawMaps)) {
      if (v && typeof v.id === 'string' && ID_RE.test(v.id)) {
        maps[k.toLowerCase()] = { id: v.id, mapper: typeof v.mapper === 'string' ? v.mapper.slice(0, 80) : '' };
      }
    }
  }
  const collections: Record<string, MapCollectionLink[]> = {};
  const rawServers = (collectionsJson as { servers?: Record<string, { id?: unknown; label?: unknown; kind?: unknown; prefix?: unknown }[]> } | null)?.servers;
  if (rawServers && typeof rawServers === 'object') {
    for (const [sid, list] of Object.entries(rawServers)) {
      if (!Array.isArray(list)) continue;
      const lists = list.filter((c) => c && c.kind === 'maps' && typeof c.id === 'string' && ID_RE.test(c.id));   // 'default' items and asset packs are not map lists
      const links = lists.map((c, i) => {
        // Several lists on one server (Possession has one for ze_ and one for zm_ maps): name them by map type, not by a bare number
        const type = typeof c.prefix === 'string' ? c.prefix.replace(/_+$/, '').toUpperCase() : '';
        const text = lists.length === 1 ? 'Map collection' : type ? `Map collection (${type})` : `Map collection ${i + 1}`;
        return { id: c.id as string, label: typeof c.label === 'string' ? c.label : 'Map collection', text };
      });
      if (links.length) collections[sid] = links;
    }
  }
  return { maps, collections };
}

/** The workshop page of this map when it is known, otherwise a workshop search for it (never a dead end). */
export function mapWorkshopUrl(map: string | undefined, data: MapWorkshopData): string {
  const key = mapKey(map);
  const hit = data.maps[key];
  if (hit) return STEAM_ITEM + hit.id;
  const term = (key || 'ze_escape').replace(/(_p|_v\d+.*)/, '');
  return `https://steamcommunity.com/workshop/browse/?appid=730&searchtext=${encodeURIComponent(term)}`;
}

export function resolvedMapper(map: string | undefined, data: MapWorkshopData): string {
  return data.maps[mapKey(map)]?.mapper || '';
}

export function collectionUrl(id: string): string {
  return STEAM_ITEM + id;
}

let pending: Promise<MapWorkshopData> | null = null;

function loadOnce(): Promise<MapWorkshopData> {
  if (!pending) {
    const grab = (url: string) => fetch(url, { cache: 'no-cache' }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
    pending = Promise.all([grab('/data/map_workshop.json'), grab('/data/server_collections.json')])
      .then(([m, c]) => parseMapWorkshop(m, c))
      .catch(() => EMPTY);
  }
  return pending;
}

export function useMapWorkshop(): MapWorkshopData {
  const [data, setData] = useState<MapWorkshopData>(EMPTY);
  useEffect(() => {
    let alive = true;
    void loadOnce().then((d) => { if (alive) setData(d); });
    return () => { alive = false; };
  }, []);
  return data;
}
