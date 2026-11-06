export interface ZEServer {
  id: string;
  name: string;
  region: string;
  regionCategory: 'na' | 'eu' | 'asia' | 'china';
  countryCode: string;
  host: string;
  port: number;
  isFeatured?: boolean;
  discord?: string;
  website?: string;
  defaultMap?: string;
  tickRate?: number;
}

export const ZE_SERVERS: ZEServer[] = [
  // FEATURED / NORTH AMERICA
  {
    id: 'gfl',
    name: 'GFL Clan Zombie Escape 24/7',
    region: 'North America (Chicago, US)',
    regionCategory: 'na',
    countryCode: 'US',
    host: '74.91.124.21',
    port: 27015,
    isFeatured: true,
    discord: 'https://discord.gg/gflze',
    defaultMap: 'ze_predator_ultimate_p3',
    tickRate: 128,
  },

  // JAPAN
  {
    id: 'possession',
    name: 'Possession Zombie Escape (PSE)',
    region: 'East Asia (Tokyo, JP)',
    regionCategory: 'asia',
    countryCode: 'JP',
    host: '103.62.49.55',
    port: 27015,
    isFeatured: false,
    discord: 'https://discord.gg/pse',
    defaultMap: 'ze_frostdrake_tower_v1',
    tickRate: 128,
  },

  // EUROPE
  {
    id: 'mapeadores',
    name: 'Mapeadores Zombie Escape',
    region: 'Europe (France / Spain)',
    regionCategory: 'eu',
    countryCode: 'EU',
    host: '87.98.228.196',
    port: 27040,
    isFeatured: false,
    discord: 'https://discord.gg/Mapeadores',
    defaultMap: 'ze_santassination_v3',
    tickRate: 128,
  },
  {
    id: 'cola',
    name: 'cOLa-TeaM Zombie Escape',
    region: 'Europe (Spain)',
    regionCategory: 'eu',
    countryCode: 'ES',
    host: '178.33.160.187',
    port: 27015,
    isFeatured: false,
    discord: 'https://discord.gg/colateam',
    defaultMap: 'ze_shroomforest_v4_5',
    tickRate: 128,
  },

  // KOREA
  {
    id: 'rss',
    name: 'RSS Zombie Escape (Revenant)',
    region: 'East Asia (Seoul, KR)',
    regionCategory: 'asia',
    countryCode: 'KR',
    host: 'rsscs2.kr',
    port: 27015,
    isFeatured: false,
    discord: 'https://discord.gg/rssze',
    defaultMap: 'ze_ffvii_mako_reactor_v5_3',
    tickRate: 128,
  },

  // RUSSIA
  {
    id: 'net4all',
    name: 'Net4All.ru Zombie Escape',
    region: 'Eastern Europe (Moscow, RU)',
    regionCategory: 'eu',
    countryCode: 'RU',
    host: '46.174.53.69',
    port: 27019,
    isFeatured: false,
    website: 'https://net4all.ru',
    defaultMap: 'ze_paranoid_rezurrection_v11',
    tickRate: 128,
  },

  // CHINA CLUSTERS (EXG COMMUNITY)
  {
    id: 'exg_8',
    name: 'EXG ZE Node #8 (Main Cluster)',
    region: 'China (Hong Kong / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '202.189.10.89',
    port: 27002,
    website: 'https://s2ze.com',
    defaultMap: 'ze_pirates_v1_1',
    tickRate: 128,
  },
  {
    id: 'exg_3',
    name: 'EXG ZE Node #3',
    region: 'China (Hong Kong / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '202.189.4.122',
    port: 27001,
    website: 'https://s2ze.com',
    defaultMap: 'ze_castlevania_64_v1_3',
    tickRate: 128,
  },
  {
    id: 'exg_16',
    name: 'EXG ZE Node #16',
    region: 'China (Hong Kong / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '202.189.10.208',
    port: 27002,
    website: 'https://s2ze.com',
    defaultMap: 'ze_tilex_ultimate_v2',
    tickRate: 128,
  },
  {
    id: 'exg_11',
    name: 'EXG ZE Node #11',
    region: 'China (Hong Kong / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '202.189.10.208',
    port: 27001,
    website: 'https://s2ze.com',
    defaultMap: 'ze_atix_panic_v1',
    tickRate: 128,
  },
  {
    id: 'exg_pve',
    name: 'EXG PVE Boss Attack #1',
    region: 'China (Hong Kong / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '202.189.5.229',
    port: 27001,
    website: 'https://s2ze.com',
    defaultMap: 'ze_ffxii_westersand_v8',
    tickRate: 128,
  },
  {
    id: '93x_1',
    name: '93X Zombie Escape #1',
    region: 'China (Shanghai / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '43.142.148.163',
    port: 27015,
    defaultMap: 'ze_gris_v1_13',
    tickRate: 128,
  },
  {
    id: 'ub_ze',
    name: 'UB Community Zombie Escape',
    region: 'China (Beijing / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '106.14.181.187',
    port: 27015,
    defaultMap: 'ze_lila_panic_escape_v2',
    tickRate: 128,
  },
  {
    id: 'zg_ze',
    name: 'ZG Community Zombie Escape',
    region: 'China (Guangzhou / BGP)',
    regionCategory: 'china',
    countryCode: 'CN',
    host: '124.220.158.232',
    port: 27015,
    defaultMap: 'ze_mountain_escape_v1',
    tickRate: 128,
  },
];
