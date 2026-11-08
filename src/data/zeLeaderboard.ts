export interface TopPlayerMVP {
  rank: number;
  name: string;
  clan: string;
  flag: string;
  score: number;
  winRate: number;
  specialtyTitle: string;
  medal: string;
  source: string;
}

export interface SpeedrunClearRecord {
  id: string;
  mapName: string;
  stage: string;
  clearTime: string;
  tierBadge: string;
  tierColor: string;
  clanName: string;
  survivorsCount: number;
  date: string;
  recordSource: string;
}

export const ZE_SEASON_INFO = {
  seasonName: 'Season 2026-11 (Autumn Assault)',
  daysRemaining: 21,
  totalMatchesTracked: 14280,
};

export const TOP_PLAYERS_OF_THE_MONTH: TopPlayerMVP[] = [
  {
    rank: 1,
    name: 'Kaemon_Enjoyer',
    clan: 'GFL Clan',
    flag: '🇺🇸',
    score: 14820,
    winRate: 78.4,
    specialtyTitle: 'Materia Master (Ultima & Heal)',
    medal: '🥇',
    source: 'GFL HLstatsX Ranked #1',
  },
  {
    rank: 2,
    name: 'CyberDrifter_99',
    clan: 'EXG Elite',
    flag: '🇨🇳',
    score: 13450,
    winRate: 74.2,
    specialtyTitle: 'Laser Jump God (Zero Bridge Wipes)',
    medal: '🥈',
    source: 'NERV CS2ZE PR Rank #1',
  },
  {
    rank: 3,
    name: 'TokyoGhoul',
    clan: 'PSE Vanguard',
    flag: '🇯🇵',
    score: 12980,
    winRate: 71.9,
    specialtyTitle: 'Choke Anchor & Boss Burst DPS',
    medal: '🥉',
    source: 's2ze Ruby Bot Global #1',
  },
  {
    rank: 4,
    name: 'FrenchEscape',
    clan: 'Mapeadores',
    flag: '🇫🇷',
    score: 11200,
    winRate: 69.5,
    specialtyTitle: 'Tactical Caller & Push Specialist',
    medal: '🏅',
    source: 'Mapeadores HLstats #1',
  },
  {
    rank: 5,
    name: 'Revenant_KR',
    clan: 'RSS Tactical',
    flag: '🇰🇷',
    score: 10850,
    winRate: 68.1,
    specialtyTitle: 'Sub-tick Bunnyhop Scout',
    medal: '🏅',
    source: 'RSS Tactical Season #1',
  },
  {
    rank: 6,
    name: 'Torero_ESP',
    clan: 'c0La-Team',
    flag: '🇪🇸',
    score: 10420,
    winRate: 66.8,
    specialtyTitle: 'Zombie Infiltrator & Choke Breaker',
    medal: '🏅',
    source: 'c0La Season Stats #1',
  },
];

export const FASTEST_MAP_CLEARS: SpeedrunClearRecord[] = [
  {
    id: 'clear-1',
    mapName: 'ze_ffvii_mako_reactor_v6',
    stage: 'Extreme II + Sephiroth Bridge',
    clearTime: '18:42',
    tierBadge: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    clanName: 'GFL / EXG Allied Strike',
    survivorsCount: 64,
    date: 'Nov 4, 2026',
    recordSource: 's2ze Season Archive',
  },
  {
    id: 'clear-2',
    mapName: 'ze_dark_souls',
    stage: 'Sen’s Fortress -> Gwyn Lord of Cinder',
    clearTime: '22:15',
    tierBadge: '🔴 T4 Hardcore',
    tierColor: 'bg-rose-950/80 text-rose-300 border-rose-500/50',
    clanName: 'EXG Elite Squad',
    survivorsCount: 48,
    date: 'Nov 6, 2026',
    recordSource: 'NERV CS2ZE Logs',
  },
  {
    id: 'clear-3',
    mapName: 'ze_deadcore',
    stage: 'Stage D (Omnidirectional Laser Cube)',
    clearTime: '11:30',
    tierBadge: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    clanName: 'PSE Speedrun Core',
    survivorsCount: 39,
    date: 'Nov 2, 2026',
    recordSource: 'PSE Match Telemetry',
  },
  {
    id: 'clear-4',
    mapName: 'ze_santassination_p',
    stage: 'Act III (Santa Laser Finale)',
    clearTime: '15:40',
    tierBadge: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    clanName: 'Mapeadores Vanguard',
    survivorsCount: 52,
    date: 'Nov 5, 2026',
    recordSource: 'Mapeadores Server Logs',
  },
  {
    id: 'clear-5',
    mapName: 'ze_pirates_port_royal',
    stage: 'Stage 5 (Kraken Boss Extraction)',
    clearTime: '19:10',
    tierBadge: '🟠 T3 Tactical',
    tierColor: 'bg-amber-950/80 text-amber-300 border-amber-500/50',
    clanName: 'RSS Tactical Alliance',
    survivorsCount: 58,
    date: 'Nov 7, 2026',
    recordSource: 'RSS Match Archive',
  },
  {
    id: 'clear-6',
    mapName: 'ze_frostdrake_tower_p',
    stage: 'Extreme Dragon Ascent Finale',
    clearTime: '16:25',
    tierBadge: '⚡ T6 Hell',
    tierColor: 'bg-fuchsia-950/80 text-fuchsia-300 border-fuchsia-500/50',
    clanName: 'c0La Allied Jumpers',
    survivorsCount: 42,
    date: 'Nov 8, 2026',
    recordSource: 'Global Speedrun Archive',
  },
];
