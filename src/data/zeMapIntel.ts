export interface ZEMapIntelEntry {
  mapKey: string;
  displayName: string;
  difficulty: 'CASUAL / WARMUP' | 'MEDIUM / TACTICAL' | 'HARDCORE / BOSS' | 'EXTREME / LASER HELL';
  difficultyColor: string;
  stages: string;
  bosses: string[];
  materiaItems: string[];
  laserTips: string;
  soundtrackCue: string;
  overview: string;
}

export const ZE_MAP_ENCYCLOPEDIA: ZEMapIntelEntry[] = [
  {
    mapKey: 'ze_ffvii_mako_reactor',
    displayName: 'FFVII: Mako Reactor (v5 / v6)',
    difficulty: 'EXTREME / LASER HELL',
    difficultyColor: 'red',
    stages: '4 Stages (Normal, Hard, Extreme, Extreme II + Sephiroth Bridge)',
    bosses: ['Guard Scorpion / Bahamut', 'Sephiroth (Bridge Laser Finale)'],
    materiaItems: ['Wind (Push)', 'Gravity (Black Hole)', 'Electro', 'Fire', 'Ice (Freeze)', 'Heal (Cure)', 'Earth (Wall)', 'Ultima (Nuke)'],
    laserTips: 'On Extreme II Bridge: equip Low Viewmodel (FOV 68, Z:-2) and Knife out. Watch Sephiroth’s sword swing height—high glow = crouch; ankle glow = jump timing.',
    soundtrackCue: 'Nobuo Uematsu / Pendulum — The Island & One-Winged Angel',
    overview: 'The most iconic Zombie Escape map in Counter-Strike history. Demands disciplined Materia management inside the reactor core and frame-perfect laser dodging on the final extraction bridge.',
  },
  {
    mapKey: 'ze_ffxii_westersand',
    displayName: 'FFXII: Dalmasca Westersand (v7 / v8)',
    difficulty: 'EXTREME / LASER HELL',
    difficultyColor: 'red',
    stages: '4 Stages + God / Chaos Mode (Airship & Tomb Finale)',
    bosses: ['Belias the Gigas', 'Chaos Walker of the Wheel', 'Judge Gabranth (Airship Lasers)'],
    materiaItems: ['Wind Staff', 'Heal Staff', 'Warp / Slow', 'Fire / Blizzard', 'Holy (Final Nuke)'],
    laserTips: 'During Airship Deck ending: stay centered on the narrow gangway, duck Boss audio to 22% so you hear crouch-laser callouts clearly, and never jump early on diagonal crisscrossing beams.',
    soundtrackCue: 'Hitoshi Sakimoto & Two Steps From Hell — Dalmasca Estersand / Protectors of the Earth',
    overview: 'Massive desert temple & sky-airship epic featuring sandstorms, Chocobo mounts, multi-phase Judge boss battles, and some of the fastest diagonal ending lasers in ZE.',
  },
  {
    mapKey: 'ze_dark_souls',
    displayName: 'Dark Souls: Prepare to Die',
    difficulty: 'HARDCORE / BOSS',
    difficultyColor: 'amber',
    stages: 'Multi-Route Castle Progression (Sen’s Fortress -> Anor Londo)',
    bosses: ['Iron Golem', 'Ornstein & Smough', 'Gwyn Lord of Cinder'],
    materiaItems: ['Estus Flask (Heal)', 'Lightning Spear', 'Chaos Firestorm', 'Force Miracle', 'Divine Blessing'],
    laserTips: 'Focus on stamina/pendulum traps in Sen’s Fortress and save Force Miracle for narrow castle stairways before boss fog gates.',
    soundtrackCue: 'Motoi Sakuraba — Ornstein & Smough / Gwyn, Lord of Cinder',
    overview: 'Atmospheric medieval dark-fantasy fortress packed with swinging pendulum blades, mimic chests, item upgrades, and punishing boss arenas.',
  },
  {
    mapKey: 'ze_deadcore',
    displayName: 'Deadcore (Simulation Core)',
    difficulty: 'EXTREME / LASER HELL',
    difficultyColor: 'red',
    stages: 'Stages A, B, C & D (Radiation / Pure Laser Finale)',
    bosses: ['Geometric Core Guardian', ' stage-D Omnidirectional Laser Cube'],
    materiaItems: ['Ammo Box', 'Heal Emitter', 'Barrier Shield', 'Gravity Pulse'],
    laserTips: 'Stage D is pure 360-degree rhythm & laser survival. Turn off First-Person Bullet Tracers (r_drawtracers_firstperson 0) to keep your screen 100% clear during cube rotations.',
    soundtrackCue: 'Blue Stahli / Celldweller / Drum & Bass Boss Mix',
    overview: 'High-speed neon cybernetic obstacle & boss map revered by veteran ZE laser jumpers for its relentless Stage D finale.',
  },
  {
    mapKey: 'ze_mist',
    displayName: 'Mist (Q4 / Escort)',
    difficulty: 'EXTREME / LASER HELL',
    difficultyColor: 'red',
    stages: 'Single Marathon Stage + Dragon & Final Bridge Lasers',
    bosses: ['Crimson Wyvern Dragon', 'Final Crystal Ascent Lasers'],
    materiaItems: ['Heal', 'Push Ring', 'Freeze Crystal', 'Speed Boost'],
    laserTips: 'Final bridge features stacked double-jump and crouch-jump lasers. Use Null-Movement binds (A/D) for sharp strafe adjustments between beams.',
    soundtrackCue: 'Symphonic Metal / Touhou & Castlevania Boss Themes',
    overview: 'Short but ruthlessly intense boss-and-laser gauntlet where a single missed crouch-jump wipes half the human team.',
  },
  {
    mapKey: 'ze_lotr_minas_tirith',
    displayName: 'LOTR: Minas Tirith',
    difficulty: 'HARDCORE / BOSS',
    difficultyColor: 'amber',
    stages: '4 Stages (Osgiliath -> White City Tier 7 / Ghost Army)',
    bosses: ['Nazgûl Fellbeast', 'Armored Cave Troll', 'Balrog / Witch-King'],
    materiaItems: ['Gandalf the White (Light Push)', 'Aragorn Banner', 'Legolas Bow', 'Oil Cauldron', 'Catapult'],
    laserTips: 'Defend inner courtyard gates until the 30-second horn blows; never block ladders during vertical wall retreats.',
    soundtrackCue: 'Howard Shore — The Bridge of Khazad-dûm & The White Tree',
    overview: 'Grand-scale 64-player siege across the seven tiers of Minas Tirith culminating in the arrival of the Army of the Dead.',
  },
  {
    mapKey: 'ze_sky_athletic',
    displayName: 'Sky Athletic Parkour',
    difficulty: 'MEDIUM / TACTICAL',
    difficultyColor: 'cyan',
    stages: '4 Stages + Extreme Heaven Mode',
    bosses: ['Giant Sky Cloud Boss (Meteor & Wind Attacks)'],
    materiaItems: ['Heal Cloud', 'Push Gust', 'Ice Platform', 'Launch Pad'],
    laserTips: 'Keep knife out for 250 u/s air-strafe speed across floating cloud platforms and watch for sudden wind-pull phases on the boss platform.',
    soundtrackCue: 'Upbeat Chiptune / Anime Arcade Sky OST',
    overview: 'Bright, fast-paced sky movement & parkour map ideal for practicing CS2 sub-tick air-strafing and coordinated boss dodges.',
  },
  {
    mapKey: 'ze_surf_vortex',
    displayName: 'Surf Vortex (CS2)',
    difficulty: 'CASUAL / WARMUP',
    difficultyColor: 'lime',
    stages: '3 Surf & Hold Stages',
    bosses: ['Vortex Core Reactor'],
    materiaItems: ['Gravity Low-G', 'Freeze Mine', 'Push Wave'],
    laserTips: 'Smoothly board ramps at a shallow angle; avoid pressing W while surfing on inclined wedges.',
    soundtrackCue: 'Synthwave / Liquid Drum & Bass Surf Mix',
    overview: 'High-velocity combat surf Zombie Escape map combining long neon ramps with tight teleporter holds.',
  },
];

export function getMapIntelForMapName(mapName?: string): ZEMapIntelEntry {
  const clean = (mapName || '').toLowerCase();
  const exact = ZE_MAP_ENCYCLOPEDIA.find((m) => clean.includes(m.mapKey));
  if (exact) return exact;

  if (clean.includes('surf')) {
    return {
      mapKey: clean,
      displayName: mapName || 'ZE Surf Map',
      difficulty: 'MEDIUM / TACTICAL',
      difficultyColor: 'cyan',
      stages: '3–4 Surf & Hold Stages',
      bosses: ['Ramp Guardian / Core Finale'],
      materiaItems: ['Push / Wind', 'Freeze Mine', 'Heal Kit'],
      laserTips: 'Keep W released on surf ramps, use A/D null-movement binds for clean air-strafes, and watch teleporter exit traps.',
      soundtrackCue: 'Liquid Drum & Bass / Electronic Surf Mix',
      overview: `Live CS2 Zombie Escape Surf map (${mapName}). Combine high-speed ramp movement with coordinated human knockback at choke points.`,
    };
  }

  return {
    mapKey: clean || 'ze_custom',
    displayName: mapName || 'Community ZE Map',
    difficulty: 'HARDCORE / BOSS',
    difficultyColor: 'fuchsia',
    stages: 'Multi-Stage Progression + Boss & Extraction Finale',
    bosses: ['Stage Boss Arena (Watch HUD HP Bar)', 'Final Extraction Hold / Laser Sequence'],
    materiaItems: ['Heal / Medkit', 'Wind / Push', 'Freeze / Slow', 'Electro / Fire', 'Ultimate Nuke'],
    laserTips: 'Use the ZE Laser-Jump Low Viewmodel (FOV 68, Z:-2) and bind a Boss Audio Ducking key (F7 -> 22% volume) so you never miss laser callouts.',
    soundtrackCue: 'Dynamic Map VPK Soundtrack (Inspect via Soundtrack Intel button)',
    overview: `Active 64-player CS2 Zombie Escape map (${mapName}). Coordinate door holds, rotate 5 seconds before timers expire, and conserve grenades for boss phases.`,
  };
}

export interface HourlyPopPoint {
  hourLabel: string;
  globalPlayers: number;
  gflPlayers: number;
}

export const HOURLY_POPULATION_24H: HourlyPopPoint[] = [
  { hourLabel: '00:00', globalPlayers: 480, gflPlayers: 58 },
  { hourLabel: '02:00', globalPlayers: 420, gflPlayers: 52 },
  { hourLabel: '04:00', globalPlayers: 390, gflPlayers: 46 },
  { hourLabel: '06:00', globalPlayers: 450, gflPlayers: 49 },
  { hourLabel: '08:00', globalPlayers: 560, gflPlayers: 55 },
  { hourLabel: '10:00', globalPlayers: 690, gflPlayers: 61 },
  { hourLabel: '12:00', globalPlayers: 820, gflPlayers: 63 },
  { hourLabel: '14:00', globalPlayers: 940, gflPlayers: 64 },
  { hourLabel: '16:00', globalPlayers: 1080, gflPlayers: 64 },
  { hourLabel: '18:00', globalPlayers: 1210, gflPlayers: 64 },
  { hourLabel: '20:00', globalPlayers: 1290, gflPlayers: 64 },
  { hourLabel: '22:00', globalPlayers: 1120, gflPlayers: 64 },
];
