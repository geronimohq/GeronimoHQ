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

export interface HardestMapFastRotationRecord {
  id: string;
  mapName: string;
  difficultyTier: string;
  tierColor: string;
  sessionDuration: string;
  rotationOutcome: string;
  outcomeType: 'flawless_win' | 'fast_clutch' | 'quick_rotation';
  clanServer: string;
  humanSurvivors: number;
  notes: string;
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

export const HARDEST_MAPS_FAST_ROTATIONS: HardestMapFastRotationRecord[] = [
  {
    id: 'fast-rot-1',
    mapName: 'ze_deadcore_s7',
    difficultyTier: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    sessionDuration: '11:20',
    rotationOutcome: '🏆 Flawless 1-Shot Clear (0 Wipes • 0 Extends)',
    outcomeType: 'flawless_win',
    clanServer: 'PSE Speedrun Core (Tokyo)',
    humanSurvivors: 39,
    notes: 'Conquered Stage D on Attempt #1; 0 wipes, 0 extends used. Map voted off in record 11m 20s total server session!',
    date: 'Nov 2, 2026',
    recordSource: 'PSE Match Telemetry',
  },
  {
    id: 'fast-rot-2',
    mapName: 'ze_santassination_p',
    difficultyTier: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    sessionDuration: '13:50',
    rotationOutcome: '🏆 Flawless 1-Shot Clear (0 Wipes • 0 Extends)',
    outcomeType: 'flawless_win',
    clanServer: 'Mapeadores (EU Spain/France)',
    humanSurvivors: 52,
    notes: 'Santa Laser Finale defeated on attempt #1. Clean extraction nuke triggered and map changed in under 14 minutes.',
    date: 'Nov 5, 2026',
    recordSource: 'Mapeadores Server Logs',
  },
  {
    id: 'fast-rot-3',
    mapName: 'ze_frostdrake_tower_p',
    difficultyTier: '⚡ T6 Hell',
    tierColor: 'bg-fuchsia-950/80 text-fuchsia-300 border-fuchsia-500/50',
    sessionDuration: '14:10',
    rotationOutcome: '🏆 Flawless 1-Shot Clear (0 Wipes • 0 Extends)',
    outcomeType: 'flawless_win',
    clanServer: 'c0La Allied Jumpers (Europe)',
    humanSurvivors: 42,
    notes: 'Mythic T6 Dragon Ascent cleared with zero human falls. Server completed the entire campaign and rotated in 14m 10s.',
    date: 'Nov 8, 2026',
    recordSource: 'Global Speedrun Archive',
  },
  {
    id: 'fast-rot-4',
    mapName: 'ze_gris_p',
    difficultyTier: '⚡ T6 Hell',
    tierColor: 'bg-fuchsia-950/80 text-fuchsia-300 border-fuchsia-500/50',
    sessionDuration: '15:45',
    rotationOutcome: '🏆 Flawless 1-Shot Clear (0 Wipes • 0 Extends)',
    outcomeType: 'flawless_win',
    clanServer: 'EXG Elite Squad (China)',
    humanSurvivors: 48,
    notes: 'Ultra-precision jumping lasers conquered with zero wipes; entire map voted off in 15m 45s instead of the usual 60m slog.',
    date: 'Nov 6, 2026',
    recordSource: 'NERV CS2ZE Logs',
  },
  {
    id: 'fast-rot-5',
    mapName: 'ze_fapescape_rote_p',
    difficultyTier: '⚡ T6 Hell',
    tierColor: 'bg-fuchsia-950/80 text-fuchsia-300 border-fuchsia-500/50',
    sessionDuration: '16:30',
    rotationOutcome: '🏆 Flawless 1-Shot Clear (0 Wipes • 0 Extends)',
    outcomeType: 'flawless_win',
    clanServer: 'GFL / EXG Allied Strike',
    humanSurvivors: 61,
    notes: 'Flawless boss burst DPS and laser bridge navigation; all stages cleared back-to-back with 0 extends burned.',
    date: 'Nov 4, 2026',
    recordSource: 's2ze Season Archive',
  },
  {
    id: 'fast-rot-6',
    mapName: 'ze_sandstorm_go_v1_4',
    difficultyTier: '🔥 T5 Nightmare',
    tierColor: 'bg-orange-950/80 text-orange-300 border-orange-500/50',
    sessionDuration: '17:15',
    rotationOutcome: '⚡ 1-Wipe Clutch Win (0 Extends Used)',
    outcomeType: 'fast_clutch',
    clanServer: 'GFL Clan (US Chicago)',
    humanSurvivors: 56,
    notes: 'Pyramid laser finale clutched on attempt #2 after an early round 1 reset; total session ended in 17m 15s.',
    date: 'Nov 7, 2026',
    recordSource: 'GFL Match Telemetry',
  },
];
