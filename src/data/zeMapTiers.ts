import { lookupS2zeMapper, lookupS2zeMapperExact } from './s2zeMappersCatalog';

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
  'zm_crazycity': {
    tier: 1,
    tierLabel: 'Casual',
    badge: '🟢 T1 Zombie',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.2)]',
    mapper: 'Stepanof',
  },
  'zm_crazycity_cs2': {
    tier: 1,
    tierLabel: 'Casual',
    badge: '🟢 T1 Zombie',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.2)]',
    mapper: 'Stepanof',
  },
  'ze_asiangirl': {
    tier: 2,
    tierLabel: 'Standard',
    badge: '🟡 T2 Standard',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Source 2 Zombie Escape',
  },
  'ze_asiangirl_mm11el4nu4cp2io1yv7_r_p': {
    tier: 2,
    tierLabel: 'Standard',
    badge: '🟡 T2 Standard',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Source 2 Zombie Escape',
  },
  'ze_asiangirl_mm11el4nu4cp2io1yv7_r': {
    tier: 2,
    tierLabel: 'Standard',
    badge: '🟡 T2 Standard',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Source 2 Zombie Escape',
  },
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
  'ze_obj_ouroboros': {
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
  'ze_timeshifter': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_crimson_azure_nexus': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Clown',
    isHallOfFame: true,
  },
  'ze_obj_abyss': {
    tier: 5,
    tierLabel: 'Nightmare',
    badge: '🔥 T5 Nightmare',
    colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    mapper: 'Clown',
    isHallOfFame: true,
  },
  'ze_obj_annihilate': {
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
  'ze_lotr_helms_deep': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Hannibal [GER]',
    isHallOfFame: true,
  },
  'ze_resident_evil_3': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Kuroki / ViSral',
    isHallOfFame: true,
  },
  'ze_resident_evil_2': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Kuroki / ViSral',
    isHallOfFame: true,
  },
  'ze_resident_evil': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Kuroki / ViSral',
    isHallOfFame: true,
  },
  'ze_biohazard2_rpd_004': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Kuroki / ViSral',
    isHallOfFame: true,
  },
  'ze_devil_may_cry': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Airvulpes',
    isHallOfFame: true,
  },
  'ze_last_man_standing': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Alcolo Oasis',
    isHallOfFame: true,
  },
  'ze_l0v0l': {
    tier: 4,
    tierLabel: 'Hardcore',
    badge: '🔴 T4 Hardcore',
    colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]',
    mapper: 'Kaemon & Mapeadores',
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
  'ze_forestbunkers': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'TaskuVaras / Moltard',
    isHallOfFame: false,
  },
  'ze_mkzk_scarab': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'f0cker',
    isHallOfFame: false,
  },
  'ze_postal': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Luffaren',
    isHallOfFame: true,
  },
  'ze_radio_building': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Sween',
    isHallOfFame: true,
  },
  'ze_variis': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Reflex',
    isHallOfFame: false,
  },
  'ze_zombierig': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Sween',
    isHallOfFame: true,
  },
  'ze_firewall_laboratory': {
    tier: 3,
    tierLabel: 'Tactical',
    badge: '🟠 T3 Tactical',
    colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]',
    mapper: 'Mapeadores Community',
    isHallOfFame: false,
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
  'ze_only_up': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Hax / Cyber',
    isHallOfFame: false,
  },
  'ze_kitchen': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Pimski',
    isHallOfFame: false,
  },
  'ze_newyork_escape': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Gamer / TaskuVaras',
    isHallOfFame: false,
  },
  'ze_por_island': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'TaskuVaras',
    isHallOfFame: false,
  },
  'ze_paradise': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Hax',
    isHallOfFame: false,
  },
  'ze_prisonbreak_rescue': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Subzero / George',
    isHallOfFame: false,
  },
  'ze_overkill': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'TaskuVaras',
    isHallOfFame: false,
  },
  'ze_magic_carpet': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'Kaemon',
    isHallOfFame: true,
  },
  'ze_rooftop_runaway2': {
    tier: 2,
    tierLabel: 'Casual',
    badge: '🟡 T2 Casual',
    colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]',
    mapper: 'TaskuVaras',
    isHallOfFame: false,
  },

  // ==========================================
  // TIER 1: WARMUP & CLASSIC INFECTION
  // ==========================================
  'ze_aztecnoob': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Gamer',
    isHallOfFame: false,
  },
  'ze_atix_panic': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Source 2 Zombie Escape',
    isHallOfFame: false,
  },
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
  'ze_sorrento_escape': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Gamer / Fred',
    isHallOfFame: false,
  },
  'ze_panic_escape': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Hannibal [GER] / Nipper',
    isHallOfFame: true,
  },
  'ze_atix_extinction': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'Source 2 Zombie Escape',
    isHallOfFame: false,
  },
  'ze_jurassicpark': {
    tier: 1,
    tierLabel: 'Warmup',
    badge: '🟢 T1 Warmup',
    colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
    mapper: 'G-Man / UT Classic',
    isHallOfFame: false,
  },
};

/**
 * Normalizes map name and retrieves Tier and Mapper attribution.
 * Handles untiered/new workshop maps via robust keyword heuristics and fallback badge.
 */
function getMapTierAndMapperRaw(mapName?: string): MapTierData {
  if (!mapName || mapName === '-' || mapName === 'Unknown') {
    return {
      mapKey: 'unknown',
      displayName: 'Unknown Map',
      tier: 'untiered',
      tierLabel: 'Untiered',
      badge: '⚪ UNTIERED',
      colorClass: 'bg-slate-900/90 text-slate-400 border-slate-700',
      mapper: '',
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

  // 3. Legendary Series Prefix Heuristic Inference & Specific Authors
  const getInferredMapper = (c: string): { mapper: string; isHoF: boolean; tier?: MapDifficultyTier; tierLabel?: string; badge?: string; colorClass?: string } | null => {
    if (c.includes('resident_evil') || c.includes('biohazard')) {
      return { mapper: 'Kuroki / ViSral', isHoF: true, tier: 4, tierLabel: 'Hardcore', badge: '🔴 T4 Hardcore', colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]' };
    }
    if (c.includes('lotr') || c.includes('helms_deep') || c.includes('isengard') || c.includes('minas')) {
      return { mapper: 'Hannibal [GER]', isHoF: true, tier: 4, tierLabel: 'Hardcore', badge: '🔴 T4 Hardcore', colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]' };
    }
    if (c.includes('ffvii') || c.includes('mako') || c.includes('cosmo')) {
      return { mapper: 'Kaemon', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('ffxii') || c.includes('westersand') || c.includes('feywood') || c.includes('paramina')) {
      return { mapper: 'Slayer / Kaemon', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('fapescape')) {
      return { mapper: 'Kim', isHoF: true, tier: 6, tierLabel: 'Hell', badge: '⚡ T6 Hell', colorClass: 'bg-fuchsia-950/90 text-fuchsia-300 border-fuchsia-500/70 shadow-[0_0_12px_rgba(217,70,239,0.4)]' };
    }
    if (c.includes('frostdrake') || c.includes('santassination') || c.includes('postal')) {
      return { mapper: 'Luffaren', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('predator') || c.includes('timeshifter') || c.includes('devil_may_cry')) {
      return { mapper: 'Airvulpes', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('shroomforest') || c.includes('mountain_escape')) {
      return { mapper: 'Moltard', isHoF: true, tier: 4, tierLabel: 'Hardcore', badge: '🔴 T4 Hardcore', colorClass: 'bg-rose-950/90 text-rose-300 border-rose-500/60 shadow-[0_0_10px_rgba(244,63,94,0.3)]' };
    }
    if (c.includes('forestbunkers') || c.includes('por_island') || c.includes('overkill')) {
      return { mapper: 'TaskuVaras / Moltard', isHoF: false, tier: 3, tierLabel: 'Tactical', badge: '🟠 T3 Tactical', colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]' };
    }
    if (c.includes('only_up') || c.includes('paradise')) {
      return { mapper: 'Hax / Cyber', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('obj_') || c.includes('crimson_azure')) {
      return { mapper: 'Clown', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('winter_warehouse') || c.includes('radio_building') || c.includes('zombierig')) {
      return { mapper: 'Sween / Waffel', isHoF: true, tier: 3, tierLabel: 'Tactical', badge: '🟠 T3 Tactical', colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]' };
    }
    if (c.includes('schizo')) {
      return { mapper: 'Platin / f0cker', isHoF: false, tier: 3, tierLabel: 'Tactical', badge: '🟠 T3 Tactical', colorClass: 'bg-amber-950/90 text-amber-300 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.25)]' };
    }
    if (c.includes('rainbow_factory')) {
      return { mapper: 'Azel / Soft Serve', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('diddle')) {
      return { mapper: 'Ayano', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.includes('deadcore')) {
      return { mapper: 'Airvulpes', isHoF: true, tier: 5, tierLabel: 'Nightmare', badge: '🔥 T5 Nightmare', colorClass: 'bg-orange-950/90 text-orange-300 border-orange-500/60 shadow-[0_0_10px_rgba(249,115,22,0.3)]' };
    }
    if (c.startsWith('zm_') || c.includes('warmup') || c.includes('infection')) {
      return { mapper: 'Nipper / Dave J.', isHoF: false, tier: 1, tierLabel: 'Warmup', badge: '🟢 T1 Warmup', colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]' };
    }
    if (c.includes('mojos') || c.includes('minigames')) {
      return { mapper: 'Mojo', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('zk_mall') || c.includes('mall_of_zombies')) {
      return { mapper: 'Killik / ZK', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('dear_cs2') || c.includes('ze_dear')) {
      return { mapper: 'Havi', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('world_escape') || c.includes('world_esc')) {
      return { mapper: 'R1cko27', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Casual', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    if (c.includes('surf')) {
      return { mapper: 'Community Surf', isHoF: false, tier: 2, tierLabel: 'Casual', badge: '🟡 T2 Surf', colorClass: 'bg-yellow-950/90 text-yellow-300 border-yellow-500/50 shadow-[0_0_8px_rgba(234,179,8,0.25)]' };
    }
    return null;
  };

  const inferred = getInferredMapper(clean) || getInferredMapper(stripped);
  if (inferred) {
    return {
      mapKey: clean,
      displayName: mapName,
      tier: inferred.tier || 'untiered',
      tierLabel: inferred.tierLabel || 'Untiered',
      badge: inferred.badge || '⚪ UNTIERED',
      colorClass: inferred.colorClass || 'bg-slate-900/90 text-slate-400 border-slate-700',
      mapper: inferred.mapper,
      isHallOfFameMapper: inferred.isHoF,
      isUntiered: false,
    };
  }

  // 4. Comprehensive S2ZE & Steam Workshop Catalog Lookup (1,486+ Official Maps)
  const s2zeMapper = lookupS2zeMapper(clean);
  if (s2zeMapper && s2zeMapper !== 'Source 2 Zombie Escape') {
    const isHoF = /Kuroki|ViSral|Hannibal|Luffaren|Airvulpes|Clown|Kaemon|Nipper|Subzero|DarkerZ|TaskuVaras|Moltard|Waffel/i.test(s2zeMapper);
    return {
      mapKey: clean,
      displayName: mapName,
      tier: 'untiered',
      tierLabel: 'Untiered',
      badge: '⚪ UNTIERED',
      colorClass: 'bg-slate-900/90 text-slate-400 border-slate-700',
      mapper: s2zeMapper,
      isHallOfFameMapper: isHoF,
      isUntiered: false, // Valid mapper confirmed from s2ze / Steam workshop catalog
    };
  }

    // 4. Heuristic Fallbacks for Untiered Maps (User Workaround)
  if (clean.startsWith('zm_') || clean.includes('warmup') || clean.includes('infection')) {
    return {
      mapKey: clean,
      displayName: mapName,
      tier: 1,
      tierLabel: 'Warmup',
      badge: '🟢 T1 Warmup',
      colorClass: 'bg-emerald-950/90 text-emerald-300 border-emerald-500/50 shadow-[0_0_8px_rgba(16,185,129,0.25)]',
      mapper: 'Classic CS:S Port',
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
      mapper: lookupS2zeMapper(clean) || lookupS2zeMapper(stripped) || '',
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
    mapper: lookupS2zeMapper(clean) || lookupS2zeMapper(stripped) || '',
    isUntiered: true,
  };
}


// Generic stand-ins the keyword fallbacks use when nothing is known about a map. They are not names of people.
const PLACEHOLDER_MAPPERS = new Set(['Community Surf', 'Nipper / Dave J.', 'Classic CS:S Port']);
const S2ZE_GENERIC = 'Source 2 Zombie Escape';
const HOF_MAPPERS = /Kuroki|ViSral|Hannibal|Luffaren|Airvulpes|Clown|Kaemon|Nipper|Subzero|DarkerZ|TaskuVaras|Moltard|Waffel/i;

/**
 * Tier + mapper for a map. The tier/badge come from the curated registry and keyword rules; the MAPPER NAME
 * comes first from the S2ZE / Steam Workshop catalog (the workshop author of that exact map), because the
 * hand-typed registry and the keyword guesses were often wrong or only a generic label.
 * Order: catalog person -> curated registry name -> catalog generic label -> "Mapper not listed" (never a made-up name).
 * The page then replaces "Mapper not listed" with the map's workshop creator when the build found one (applyResolvedMapper).
 */
export function getMapTierAndMapper(mapName?: string): MapTierData {
  const base = getMapTierAndMapperRaw(mapName);
  const exact = lookupS2zeMapperExact(base.mapKey || mapName || '');
  if (exact && exact !== S2ZE_GENERIC) {
    return { ...base, mapper: exact, isHallOfFameMapper: HOF_MAPPERS.test(exact) };
  }
  if (exact === S2ZE_GENERIC) {
    // The catalog only says the CS2 port is by the Source 2 Zombie Escape team. A hand-typed registry entry for this exact
    // map may name the original author, but a keyword/substring guess (e.g. "atix" -> Nipper) is not evidence.
    const c = (mapName || '').trim().toLowerCase();
    const st = c.replace(/_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i, '');
    const curated = ZE_MAP_TIERS_REGISTRY[c] || ZE_MAP_TIERS_REGISTRY[st];
    if (!curated) return { ...base, mapper: S2ZE_GENERIC, isHallOfFameMapper: false };
  }
  if (PLACEHOLDER_MAPPERS.has(base.mapper)) {
    return { ...base, mapper: exact === S2ZE_GENERIC ? S2ZE_GENERIC : MAPPER_NOT_LISTED, isHallOfFameMapper: false };
  }
  return base.mapper ? base : { ...base, mapper: MAPPER_NOT_LISTED };       // never an empty "by:" pill
}

export const MAPPER_NOT_LISTED = 'Mapper not listed';

/**
 * Fills "Mapper not listed" from the workshop creator that scripts/resolve_workshop_maps.py found for this exact map
 * (see src/utils/mapWorkshop.ts). A mapper the catalog or the curated registry already names is never replaced.
 */
export function applyResolvedMapper(tier: MapTierData, resolved?: string): MapTierData {
  if (!resolved || (tier.mapper && tier.mapper !== MAPPER_NOT_LISTED)) return tier;
  return { ...tier, mapper: resolved, isHallOfFameMapper: HOF_MAPPERS.test(resolved) };
}
