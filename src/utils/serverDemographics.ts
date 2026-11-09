export interface DemographicItem {
  code: string;
  name: string;
  flag: string;
  color: string;
  percentage: number;
  count: number;
  pingRange?: string;
  description?: string;
}

export interface ServerDemographicsResult {
  dominantCountry: DemographicItem;
  dominantContinent: DemographicItem;
  dominantLatency: DemographicItem;
  countries: DemographicItem[];
  continents: DemographicItem[];
  latencies: DemographicItem[];
  summary: string;
}

interface CountryMeta {
  name: string;
  flag: string;
  color: string;
  continent: 'NA' | 'EU' | 'ASIA' | 'CIS' | 'LATAM' | 'OTHER';
}

const COUNTRY_METAS: Record<string, CountryMeta> = {
  US: { name: 'United States', flag: '🇺🇸', color: '#00f0ff', continent: 'NA' },
  CA: { name: 'Canada', flag: '🇨🇦', color: '#38bdf8', continent: 'NA' },
  VN: { name: 'Vietnam', flag: '🇻🇳', color: '#ef4444', continent: 'ASIA' },
  PH: { name: 'Philippines', flag: '🇵🇭', color: '#eab308', continent: 'ASIA' },
  JP: { name: 'Japan', flag: '🇯🇵', color: '#ec4899', continent: 'ASIA' },
  KR: { name: 'South Korea', flag: '🇰🇷', color: '#06b6d4', continent: 'ASIA' },
  CN: { name: 'China', flag: '🇨🇳', color: '#f87171', continent: 'ASIA' },
  ID: { name: 'Indonesia', flag: '🇮🇩', color: '#f97316', continent: 'ASIA' },
  IN: { name: 'India', flag: '🇮🇳', color: '#fbbf24', continent: 'ASIA' },
  UK: { name: 'United Kingdom', flag: '🇬🇧', color: '#6366f1', continent: 'EU' },
  FR: { name: 'France', flag: '🇫🇷', color: '#10b981', continent: 'EU' },
  DE: { name: 'Germany', flag: '🇩🇪', color: '#f59e0b', continent: 'EU' },
  ES: { name: 'Spain', flag: '🇪🇸', color: '#fb923c', continent: 'EU' },
  PL: { name: 'Poland', flag: '🇵🇱', color: '#a855f7', continent: 'EU' },
  RU: { name: 'Russia / CIS', flag: '🇷🇺', color: '#c084fc', continent: 'CIS' },
  BR: { name: 'Brazil / LatAm', flag: '🇧🇷', color: '#22c55e', continent: 'LATAM' },
  OTHER: { name: 'Other Regions', flag: '🌎', color: '#94a3b8', continent: 'OTHER' },
};

/**
 * Calculates continuous diurnal gaming activity factor (0.20 to 1.00).
 * Peak activity occurs during evening hours (20:00 - 23:00 local time),
 * with the trough occurring in the morning (05:00 - 09:00 local time).
 */
function getDiurnalFactor(localHour: number): number {
  const angle = ((localHour - 21) * 2 * Math.PI) / 24;
  const cosVal = Math.cos(angle);
  return 0.20 + 0.80 * ((cosVal + 1) / 2);
}

/**
 * Returns estimated ping range string from player origin country to server datacenter.
 */
function getCountryPingRange(countryCode: string, serverRegion: string): string {
  const reg = (serverRegion || '').toLowerCase();
  const isNA = reg.includes('us') || reg.includes('chicago') || reg.includes('north america') || reg === 'na';
  const isEU = reg.includes('france') || reg.includes('fr') || reg.includes('spain') || reg.includes('es') || reg.includes('eu');
  const isAsia = reg.includes('japan') || reg.includes('tokyo') || reg.includes('jp') || reg.includes('korea') || reg.includes('kr') || reg.includes('china') || reg.includes('cn');
  const isCIS = reg.includes('russia') || reg.includes('ru') || reg.includes('net4all') || reg.includes('cis');

  if (isNA) {
    switch (countryCode) {
      case 'US': return '25–65 ms';
      case 'CA': return '35–70 ms';
      case 'UK': return '100–125 ms';
      case 'FR': return '105–130 ms';
      case 'DE': return '110–135 ms';
      case 'ES': return '110–140 ms';
      case 'PL': return '115–145 ms';
      case 'RU': return '135–175 ms';
      case 'BR': return '130–170 ms';
      case 'JP': return '165–195 ms';
      case 'KR': return '170–205 ms';
      case 'CN': return '190–235 ms';
      case 'VN': return '195–235 ms';
      case 'PH': return '190–235 ms';
      case 'ID': return '200–240 ms';
      case 'IN': return '210–250 ms';
      default: return '120–220 ms';
    }
  }

  if (isEU) {
    switch (countryCode) {
      case 'FR':
      case 'DE':
      case 'ES':
      case 'UK':
      case 'PL': return '15–45 ms';
      case 'RU': return '50–85 ms';
      case 'US':
      case 'CA': return '95–130 ms';
      case 'BR': return '140–180 ms';
      default: return '180–240 ms+';
    }
  }

  if (isAsia) {
    switch (countryCode) {
      case 'JP':
      case 'KR':
      case 'CN':
      case 'VN':
      case 'PH':
      case 'ID': return '15–60 ms';
      case 'IN': return '70–110 ms';
      case 'RU': return '100–150 ms';
      case 'US':
      case 'CA': return '140–190 ms';
      default: return '180–240 ms+';
    }
  }

  if (isCIS) {
    switch (countryCode) {
      case 'RU': return '20–55 ms';
      case 'PL':
      case 'DE':
      case 'FR': return '50–85 ms';
      case 'UK': return '60–95 ms';
      case 'CN':
      case 'IN': return '110–160 ms';
      default: return '130–200 ms';
    }
  }

  return '50–150 ms';
}

/**
 * Calculates real-time geographic demographics and latency distribution of connected players.
 * Combines:
 *  1. Physical datacenter location routing & latency tiers
 *  2. Real-time global diurnal gaming cycles (UTC time-of-day peaks)
 *  3. Deep active player roster linguistic, script, and clan tag analysis
 */
export function getServerDemographics(
  serverRegion: string,
  totalPlayers: number,
  playerNames: string[] = []
): ServerDemographicsResult {
  const idleItem: DemographicItem = {
    code: 'IDLE',
    name: 'Server Empty',
    flag: '💤',
    color: '#64748b',
    percentage: 100,
    count: 0,
    pingRange: '0 ms',
  };

  if (totalPlayers <= 0) {
    return {
      dominantCountry: idleItem,
      dominantContinent: idleItem,
      dominantLatency: idleItem,
      countries: [idleItem],
      continents: [idleItem],
      latencies: [idleItem],
      summary: 'No active players currently connected.',
    };
  }

  const now = new Date();
  const utcHour = now.getUTCHours() + now.getUTCMinutes() / 60;

  // Regional local time offsets for diurnal activity curves
  const naHour = (utcHour - 6 + 24) % 24;      // US Central (Chicago)
  const euHour = (utcHour + 1) % 24;           // Western/Central Europe
  const asiaHour = (utcHour + 8) % 24;         // East/Southeast Asia (PH, VN, CN, SG)
  const cisHour = (utcHour + 3) % 24;          // Moscow / CIS
  const latamHour = (utcHour - 3 + 24) % 24;   // Brazil / South America

  const naDiurnal = getDiurnalFactor(naHour);
  const euDiurnal = getDiurnalFactor(euHour);
  const asiaDiurnal = getDiurnalFactor(asiaHour);
  const cisDiurnal = getDiurnalFactor(cisHour);
  const latamDiurnal = getDiurnalFactor(latamHour);

  // Initialize country counts
  const countryCounts: Record<string, number> = {};
  for (const c of Object.keys(COUNTRY_METAS)) {
    countryCounts[c] = 0;
  }

  let attributedPlayerCount = 0;

  // Analyze connected player roster for linguistic, script, and regional signals
  for (const rawName of playerNames) {
    if (!rawName || rawName === 'Connecting...') continue;
    const name = rawName.trim();
    const lower = name.toLowerCase();

    let matchedCountry: string | null = null;

    // 1. Vietnamese signals (diacritics, syllables, clan tags)
    if (
      /[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]/i.test(name) ||
      /\b(vn|vie|vietnam|viet)\b|[[(_](vn|vie)[\])_]/i.test(lower) ||
      /(?:duy|huy|nguyen|tran|hoang|phan|vu|viet|banh)/i.test(lower)
    ) {
      matchedCountry = 'VN';
    }
    // 2. Japanese signals (Hiragana, Katakana, Kanji, anime names, -kun/-san)
    else if (
      /[\u3040-\u30ff]/.test(name) ||
      /\b(jp|jpn|japan)\b|[[(_](jp|jpn)[\])_]/i.test(lower) ||
      /(?:kakashi|riku|dojima|daishin|kuroki|kitsune)/i.test(lower) ||
      /kun\b|san\b/i.test(lower)
    ) {
      matchedCountry = 'JP';
    }
    // 3. Korean signals (Hangul, tags)
    else if (/[\uac00-\ud7af]/.test(name) || /\b(kr|kor|korea)\b|[[(_](kr|kor)[\])_]/i.test(lower)) {
      matchedCountry = 'KR';
    }
    // 4. Chinese signals (CJK Hanzi, tags)
    else if (/[\u4e00-\u9fff]/.test(name) || /\b(cn|chn|china)\b|[[(_](cn|chn)[\])_]/i.test(lower)) {
      matchedCountry = 'CN';
    }
    // 5. Filipino signals
    else if (/\b(ph|phl|pinoy|pilipinas)\b|[[(_](ph|phl)[\])_]/i.test(lower) || lower.includes('geronimo')) {
      matchedCountry = 'PH';
    }
    // 6. Indonesian / Malay signals
    else if (/\b(id|ina|indo|indonesia)\b|[[(_](id|ina)[\])_]/i.test(lower) || lower.includes('kaleng')) {
      matchedCountry = 'ID';
    }
    // 7. Indian / South Asian signals
    else if (/\b(in|ind|india)\b|[[(_](in|ind)[\])_]/i.test(lower) || /(?:rajesh|darinda|singh|kumar)/i.test(lower)) {
      matchedCountry = 'IN';
    }
    // 8. Russian / Cyrillic signals
    else if (/[\u0400-\u04ff]/.test(name) || /\b(ru|rus|russia)\b|[[(_](ru|rus)[\])_]/i.test(lower) || /(?:alexey|vladimir)/i.test(lower)) {
      matchedCountry = 'RU';
    }
    // 9. Latin America signals
    else if (/\b(br|bra|brasil|brazil|arg|argentina|cl|latam)\b|[[(_](br|bra|arg|cl|latam)[\])_]/i.test(lower)) {
      matchedCountry = 'BR';
    }
    // 10. European clan tags
    else if (/\b(fr|fra|france)\b|[[(_](fr|fra)[\])_]/i.test(lower)) {
      matchedCountry = 'FR';
    } else if (/\b(de|ger|germany)\b|[[(_](de|ger)[\])_]/i.test(lower)) {
      matchedCountry = 'DE';
    } else if (/\b(uk|gb|britain)\b|[[(_](uk|gb)[\])_]/i.test(lower)) {
      matchedCountry = 'UK';
    } else if (/\b(es|esp|spain)\b|[[(_](es|esp)[\])_]/i.test(lower)) {
      matchedCountry = 'ES';
    } else if (/\b(pl|poland)\b|[[(_](pl|pol)[\])_]/i.test(lower)) {
      matchedCountry = 'PL';
    }
    // 11. North American clan tags
    else if (/\b(us|usa)\b|[[(_](us|usa|na)[\])_]/i.test(lower)) {
      matchedCountry = 'US';
    } else if (/\b(ca|can|canada)\b|[[(_](ca|can)[\])_]/i.test(lower)) {
      matchedCountry = 'CA';
    }

    if (matchedCountry) {
      countryCounts[matchedCountry] += 1;
      attributedPlayerCount += 1;
    }
  }

  // Unattributed players (players with standard Western gamer handles)
  // are distributed based on live diurnal activity weighted by datacenter routing proximity.
  const unattributed = Math.max(0, totalPlayers - attributedPlayerCount);

  const reg = (serverRegion || '').toLowerCase();
  const isNA = reg.includes('us') || reg.includes('chicago') || reg.includes('north america') || reg === 'na';
  const isEU = reg.includes('france') || reg.includes('fr') || reg.includes('spain') || reg.includes('es') || reg.includes('eu');
  const isAsia = reg.includes('japan') || reg.includes('tokyo') || reg.includes('jp') || reg.includes('korea') || reg.includes('kr') || reg.includes('china') || reg.includes('cn');

  let diurnalWeights: Record<string, number>;
  if (isNA) {
    diurnalWeights = {
      US: 1.6 * naDiurnal * 0.85,
      CA: 1.6 * naDiurnal * 0.15,
      UK: 0.9 * euDiurnal * 0.32,
      DE: 0.9 * euDiurnal * 0.28,
      FR: 0.9 * euDiurnal * 0.22,
      ES: 0.9 * euDiurnal * 0.18,
      PL: 0.9 * euDiurnal * 0.10,
      VN: 0.7 * asiaDiurnal * 0.22,
      PH: 0.7 * asiaDiurnal * 0.22,
      JP: 0.7 * asiaDiurnal * 0.16,
      CN: 0.7 * asiaDiurnal * 0.14,
      ID: 0.7 * asiaDiurnal * 0.10,
      IN: 0.7 * asiaDiurnal * 0.08,
      KR: 0.7 * asiaDiurnal * 0.08,
      RU: 0.5 * cisDiurnal,
      BR: 0.5 * latamDiurnal,
      OTHER: 0.3,
    };
  } else if (isEU) {
    diurnalWeights = {
      FR: 1.8 * euDiurnal * 0.35,
      DE: 1.8 * euDiurnal * 0.25,
      ES: 1.8 * euDiurnal * 0.20,
      UK: 1.8 * euDiurnal * 0.15,
      PL: 1.8 * euDiurnal * 0.10,
      RU: 0.9 * cisDiurnal,
      US: 0.6 * naDiurnal * 0.85,
      CA: 0.6 * naDiurnal * 0.15,
      BR: 0.4 * latamDiurnal,
      VN: 0.3 * asiaDiurnal,
      PH: 0.3 * asiaDiurnal,
      JP: 0.3 * asiaDiurnal,
      OTHER: 0.25,
    };
  } else if (isAsia) {
    diurnalWeights = {
      JP: 1.8 * asiaDiurnal * 0.35,
      KR: 1.8 * asiaDiurnal * 0.20,
      CN: 1.8 * asiaDiurnal * 0.20,
      VN: 1.8 * asiaDiurnal * 0.12,
      PH: 1.8 * asiaDiurnal * 0.10,
      ID: 1.8 * asiaDiurnal * 0.08,
      RU: 0.6 * cisDiurnal,
      US: 0.4 * naDiurnal,
      UK: 0.3 * euDiurnal,
      OTHER: 0.2,
    };
  } else {
    diurnalWeights = {
      RU: 1.5 * cisDiurnal,
      PL: 1.0 * euDiurnal,
      DE: 0.8 * euDiurnal,
      US: 0.4 * naDiurnal,
      CN: 0.4 * asiaDiurnal,
      OTHER: 0.3,
    };
  }

  const sumDiurnal = Object.values(diurnalWeights).reduce((a, b) => a + b, 0) || 1;
  for (const [code, weight] of Object.entries(diurnalWeights)) {
    if (countryCounts[code] !== undefined) {
      countryCounts[code] += (weight / sumDiurnal) * unattributed;
    }
  }

  const sumTotal = Object.values(countryCounts).reduce((a, b) => a + b, 0) || 1;

  // Build Country Demographics List
  const countryItems: DemographicItem[] = Object.entries(countryCounts)
    .map(([code, count]) => {
      const pct = Math.round((count / sumTotal) * 100);
      const meta = COUNTRY_METAS[code] || COUNTRY_METAS.OTHER;
      const pingRange = getCountryPingRange(code, serverRegion);
      return {
        code,
        name: meta.name,
        flag: meta.flag,
        color: meta.color,
        percentage: pct,
        count: Math.max(1, Math.round(count)),
        pingRange,
      };
    })
    .filter((item) => item.percentage > 0)
    .sort((a, b) => b.percentage - a.percentage);

  // Continental Aggregation
  const continentSums: Record<string, number> = { NA: 0, EU: 0, ASIA: 0, CIS: 0, LATAM: 0, OTHER: 0 };
  for (const c of countryItems) {
    const meta = COUNTRY_METAS[c.code] || COUNTRY_METAS.OTHER;
    continentSums[meta.continent] = (continentSums[meta.continent] || 0) + c.percentage;
  }

  const continentPing = (cont: string): string => {
    if (isNA) {
      if (cont === 'NA') return '< 70 ms';
      if (cont === 'EU') return '95–135 ms';
      if (cont === 'CIS') return '135–175 ms';
      if (cont === 'LATAM') return '130–170 ms';
      if (cont === 'ASIA') return '170–240 ms+';
      return '120–220 ms';
    }
    if (isEU) {
      if (cont === 'EU') return '< 50 ms';
      if (cont === 'CIS') return '50–85 ms';
      if (cont === 'NA') return '95–130 ms';
      if (cont === 'LATAM') return '140–180 ms';
      return '180–240 ms+';
    }
    if (isAsia) {
      if (cont === 'ASIA') return '< 60 ms';
      if (cont === 'CIS') return '100–150 ms';
      if (cont === 'NA') return '140–190 ms';
      return '180–240 ms+';
    }
    return '50–150 ms';
  };

  const continentMeta: Record<string, { name: string; flag: string; color: string }> = {
    ASIA: { name: 'Asia-Pacific', flag: '🌏', color: '#f59e0b' },
    EU: { name: 'Europe', flag: '🇪🇺', color: '#10b981' },
    NA: { name: 'North America', flag: '🇺🇸', color: '#00f0ff' },
    CIS: { name: 'CIS / East EU', flag: '🇷🇺', color: '#c084fc' },
    LATAM: { name: 'Latin America', flag: '🇧🇷', color: '#22c55e' },
    OTHER: { name: 'Other Regions', flag: '🌎', color: '#94a3b8' },
  };

  const continentItems: DemographicItem[] = Object.entries(continentSums)
    .filter(([, pct]) => pct > 0)
    .map(([code, pct]) => ({
      code,
      name: continentMeta[code]?.name || code,
      flag: continentMeta[code]?.flag || '🌐',
      color: continentMeta[code]?.color || '#94a3b8',
      percentage: pct,
      count: Math.round((pct / 100) * totalPlayers),
      pingRange: continentPing(code),
    }))
    .sort((a, b) => b.percentage - a.percentage);

  // Latency Tiers (Physical Scoreboard Ping Spectrum)
  let lowPingPct = 0;
  let midPingPct = 0;
  let highPingPct = 0;

  if (isNA) {
    lowPingPct = continentSums.NA || 0;
    midPingPct = (continentSums.EU || 0) + (continentSums.LATAM || 0);
    highPingPct = (continentSums.ASIA || 0) + (continentSums.CIS || 0) + (continentSums.OTHER || 0);
  } else if (isEU) {
    lowPingPct = (continentSums.EU || 0) + (continentSums.CIS || 0);
    midPingPct = continentSums.NA || 0;
    highPingPct = (continentSums.ASIA || 0) + (continentSums.LATAM || 0) + (continentSums.OTHER || 0);
  } else if (isAsia) {
    lowPingPct = continentSums.ASIA || 0;
    midPingPct = (continentSums.CIS || 0) + (continentSums.NA || 0);
    highPingPct = (continentSums.EU || 0) + (continentSums.LATAM || 0) + (continentSums.OTHER || 0);
  } else {
    lowPingPct = (continentSums.CIS || 0) + (continentSums.EU || 0);
    midPingPct = continentSums.ASIA || 0;
    highPingPct = continentSums.NA || 0;
  }

  // Normalize latency tiers to sum to 100%
  const sumLatency = (lowPingPct + midPingPct + highPingPct) || 1;
  const normLow = Math.round((lowPingPct / sumLatency) * 100);
  const normMid = Math.round((midPingPct / sumLatency) * 100);
  const normHigh = Math.max(0, 100 - normLow - normMid);

  const latencyItems: DemographicItem[] = [
    {
      code: 'HIGH',
      name: 'High Ping (140–240ms+)',
      flag: '⚡',
      color: '#c084fc',
      percentage: normHigh,
      count: Math.round((normHigh / 100) * totalPlayers),
      pingRange: '140–240 ms+',
      description: 'Trans-oceanic and distant international connections (Asia-Pac / Global routes)'
    },
    {
      code: 'MID',
      name: 'Mid Ping (70–140ms)',
      flag: '⚡',
      color: '#10b981',
      percentage: normMid,
      count: Math.round((normMid / 100) * totalPlayers),
      pingRange: '70–140 ms',
      description: 'Cross-continental connections (Europe, Latin America)'
    },
    {
      code: 'LOW',
      name: 'Low Ping (< 70ms)',
      flag: '⚡',
      color: '#00f0ff',
      percentage: normLow,
      count: Math.round((normLow / 100) * totalPlayers),
      pingRange: '< 70 ms',
      description: 'Local players closest to physical server datacenter'
    },
  ].sort((a, b) => b.percentage - a.percentage);

  const dominantCountry = countryItems[0] || idleItem;
  const dominantContinent = continentItems[0] || idleItem;
  const dominantLatency = latencyItems[0] || idleItem;

  const summary = `${dominantContinent.flag} ${dominantContinent.name} is the top demographic with ~${dominantContinent.percentage}% of players (${dominantContinent.pingRange} ping), with ${normLow}% local (<70ms) and ${normMid + normHigh}% international (70–240ms+).`;

  return {
    dominantCountry,
    dominantContinent,
    dominantLatency,
    countries: countryItems,
    continents: continentItems,
    latencies: latencyItems,
    summary,
  };
}
