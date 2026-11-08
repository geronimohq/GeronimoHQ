export interface TopPlayerMVP {
  rank: number;
  name: string;
  clan: string;
  flag: string;
  score: number;
  winRate: number;
  specialtyTitle: string;
  medal: string;
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
  },
];
