export type MapDifficultyTier = 1 | 2 | 3 | 4 | 5 | 6 | 'untiered';

export interface MapTierData {
  mapKey: string;
  displayName: string;
  tier: MapDifficultyTier;
  tierLabel: string;
  badge: string;
  colorClass: string;
  mapper: string;
  isHallOfFameMapper?: boolean;
  isUntiered?: boolean;
}

export const ZE_MAP_TIERS_REGISTRY: Record<
  string,
  {
    tier: MapDifficultyTier;
    tierLabel: string;
    badge: string;
    colorClass: string;
    mapper: string;
    isHallOfFame?: boolean;
  }
> = {
  // ==========================================
  // TIER 6: HELL & MYTHIC ENDURANCE MARATHONS
  // ==========================================
  'ze_fapescape_rote': {
    tier: 6,
    tierLabel: 'Hell',
    badge: '⚡ T6 Hell',
    colorClass: 'bg-fuchsia-950/90 text-fuchsia-300 border-fuchsia-500/70 shadow-[0_0_12px_rgba(217,70,239,0.4)]',
    mapper: 'Kim',
    isHallOfFame: true,
  },
  'ze_frostdrake_tower': {
    tier: 6,
    tierLabel: 'Hell',
    badge: '⚡ T6 Hell',
    colorClass: 'bg-fuchsia-950/90 text-fuchsia-300 border-fuchsia-500/70 shadow-[0_0_12px_rgba(217,70,239,0.4)]',
    mapper: 'Luffaren',
    isHallOfFame: true,
  },
  'ze_gris': {
    tier: 6,
    tierLabel: 'Hell',
    badge: '⚡ T6 Hell',
    colorClass: 'bg-fuchsia-950/90 text-fuchsia-300 border-fuchsia-500/70 shadow-[0_0_12px_rgba(217,70,239,0.4)]',
    mapper: 'Ma/l/go',
    isHallOfFame: true,
  },
  'ze_obj_blue_depth': {
    tier: 6,
    tierLabel: 'Hell',
    badge: '⚡ T6 Hell',
    colorClass: 'bg-fuchsia-950/90 text-fuchsia-300 border-fuchsia-500/70 shadow-[0_0_12px_rgba(217,70,239,0.4)]',
    mapper: 'Clown',
    isHallOfFame: true,
  },

  // ==========================================
  // TIER 5: NIGHTMARE & LASER BOSS FINALES
  // ==========================================
  'ze_ffvii_mako_reactor': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Kaemon & Hannibal',
    isHallOfFame: true,
  },
  'ze_ffvii_mako_reactor_v6': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Kaemon & Hannibal',
    isHallOfFame: true,
  },
  'ze_ffxii_westersand': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Kaemon',
    isHallOfFame: true,
  },
  'ze_deadcore': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_sandstorm': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_serpentis_temple': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Kaemon & Subzero',
    isHallOfFame: true,
  },
  'ze_santassination': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Luffaren',
    isHallOfFame: true,
  },
  'ze_mist': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_obj_npst': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Clown',
    isHallOfFame: true,
  },
  'ze_obf_npst': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Clown',
    isHallOfFame: true,
  },

  // ==========================================
  // TIER 4: HARDCORE / MULTI-PHASE BOSS
  // ==========================================
  'ze_dark_souls': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },
  'ze_dystopia': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_ffvii_cosmo_canyon': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'HeadFox & Hannibal',
    isHallOfFame: true,
  },
  'ze_ffxii_feywood': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Misaka',
    isHallOfFame: true,
  },
  'ze_lotr_minas_tirith': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Cannisup & Hannibal',
    isHallOfFame: true,
  },
  'ze_predator_ultimate': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Billy',
    isHallOfFame: true,
  },
  'ze_alien_vs_predator': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Billy',
    isHallOfFame: true,
  },
  'ze_ffxii_mt_bur_omisace': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Misaka',
    isHallOfFame: true,
  },
  'ze_ffxii_paramina_rift': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Misaka',
    isHallOfFame: true,
  },
  'ze_scp': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Moltard & GFL Team',
    isHallOfFame: true,
  },
  'ze_starwars_v2': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },
  'ze_naruto': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },

  // ==========================================
  // TIER 3: TACTICAL ESCORT & MATERIA
  // ==========================================
  'ze_winter_warehouse': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Sween',
    isHallOfFame: true,
  },
  'ze_1_schizo': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'f0cker',
    isHallOfFame: false,
  },
  'ze_rainbow_factory': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Soft Serve',
    isHallOfFame: false,
  },
  'ze_ashen_keep': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Luffaren',
    isHallOfFame: true,
  },
  'ze_abandoned_project': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Hax',
    isHallOfFame: false,
  },
  'ze_pirates_port_royal': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_potc': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_portal_story': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_egypt_universe': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },
  'ze_castlevania': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },
  'ze_bathroom': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_diddle': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Moltard',
    isHallOfFame: true,
  },
  'ze_tilex_escape': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Moltard',
    isHallOfFame: true,
  },
  'ze_paper_escaper': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Moltard',
    isHallOfFame: true,
  },
  'ze_stalker_corridor': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Kawa',
    isHallOfFame: false,
  },
  'ze_undertale': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },
  'ze_rtcw_ominous_rumor': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Tsubasa',
    isHallOfFame: true,
  },

  // ==========================================
  // TIER 2: CASUAL ESCORT & SURF
  // ==========================================
  'ze_shroomforest': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Moltard',
    isHallOfFame: true,
  },
  'ze_shroomforest3': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Moltard',
    isHallOfFame: true,
  },
  'ze_voodoo_islands': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_isla_nublar': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Puklica',
    isHallOfFame: true,
  },
  'ze_biohazard2_sewer': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'DarkerZ',
    isHallOfFame: false,
  },
  'ze_mirrors_edge': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'DarkerZ',
    isHallOfFame: false,
  },
  'ze_l4d2_c1m1_hotel': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Nipper / Dave J.',
    isHallOfFame: false,
  },
  'ze_sky_athletic': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Kawa',
    isHallOfFame: false,
  },

  // ==========================================
  // TIER 1: WARMUP & CLASSIC INFECTION
  // ==========================================
  'zm_dust_v3': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Nipper / Dave J.',
    isHallOfFame: false,
  },
  'zm_mansion': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Magnus L.',
    isHallOfFame: false,
  },
  'ze_minecraft_drifts': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'DarkerZ',
    isHallOfFame: false,
  },
  'ze_rooftop_runaway2': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Community Classic',
    isHallOfFame: false,
  },
  'ze_sorrento_escape': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Community Classic',
    isHallOfFame: false,
  },
  'ze_panic_escape': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Community Classic',
    isHallOfFame: false,
  },
  'ze_atix_extinction': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Community Classic',
    isHallOfFame: false,
  },
  'ze_jurassicpark': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Community Classic',
    isHallOfFame: false,
  },
};

/**
 * Normalizes map name and retrieves Tier and Mapper attribution.
 * Handles untiered/new workshop maps via robust keyword heuristics and fallback badge.
 */
export function getMapTierAndMapper(mapName?: string): MapTierData {
  if (!mapName || mapName === '-' || mapName === 'Unknown') {
    return {
      mapKey: 'unknown',
      displayName: 'Unknown Map',
      tier: 'untiered',
      tierLabel: 'Untiered',
      badge: '⚪ UNTIERED',
      colorClass: 'bg-slate-900/90 text-slate-400 border-slate-700',
      mapper: 'Community Workshop',
      isUntiered: true,
    };
  }

  let clean = mapName.trim().toLowerCase();
  if (clean.includes('/')) {
    clean = clean.split('/').pop() || clean;
  }
  // Strip common suffixes: _p, _v6, _v5_6, _rc1, _final, etc.
  const stripped = clean.replace(/_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i, '');

  // 1. Direct registry lookup (either exact clean or stripped)
  const entry = ZE_MAP_TIERS_REGISTRY[clean] || ZE_MAP_TIERS_REGISTRY[stripped];
  if (entry) {
    return {
      mapKey: clean,
      displayName: mapName,
      tier: entry.tier,
      tierLabel: entry.tierLabel,
      badge: entry.badge,
      colorClass: entry.colorClass,
      mapper: entry.mapper,
      isHallOfFameMapper: entry.isHallOfFame,
      isUntiered: false,
    };
  }

  // 2. Keyword Substring Match (e.g. "ze_mako_v5" matching "ze_ffvii_mako_reactor")
  for (const [key, reg] of Object.entries(ZE_MAP_TIERS_REGISTRY)) {
    if (clean.includes(key) || key.includes(clean) || stripped.includes(key) || key.includes(stripped)) {
      return {
        mapKey: clean,
        displayName: mapName,
        tier: reg.tier,
        tierLabel: reg.tierLabel,
        badge: reg.badge,
        colorClass: reg.colorClass,
        mapper: reg.mapper,
        isHallOfFameMapper: reg.isHallOfFame,
        isUntiered: false,
      };
    }
  }

  // 3. Heuristic Fallbacks for Untiered Maps (User Workaround)
  if (clean.startsWith('zm_') || clean.includes('warmup') || clean.includes('infection')) {
    return {
      mapKey: clean,
      displayName: mapName,
      tier: 1,
      tierLabel: 'Warmup',
      badge: '🟢 T1 Warmup',
      colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
      mapper: 'Community Classic',
      isUntiered: false,
    };
  }

  if (clean.includes('surf')) {
    return {
      mapKey: clean,
      displayName: mapName,
      tier: 2,
      tierLabel: 'Casual',
      badge: '🟡 T2 Surf',
      colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
      mapper: 'Community Workshop',
      isUntiered: false,
    };
  }

  // 4. Default Untiered Workaround
  return {
    mapKey: clean,
    displayName: mapName,
    tier: 'untiered',
    tierLabel: 'Untiered',
    badge: '⚪ UNTIERED',
    colorClass: 'bg-slate-900/90 text-slate-400 border-slate-700',
    mapper: 'Community Workshop',
    isUntiered: true,
  };
}
