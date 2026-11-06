import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ZE_SERVERS, type ZEServer } from '../data/zeServers';
import { 
  fetchLiveTelemetry, 
  getMapStartTime, 
  formatMapElapsed, 
  getEstimatedRegionalPing,
  getMapThumbnailUrl,
  getMap3DViewerUrl,
  type LiveTelemetryPayload, 
  type PlayerEntry 
} from '../utils/serverQuery';
import { 
  Play, 
  Copy, 
  Check, 
  Search, 
  Globe, 
  ExternalLink, 
  Radio, 
  MapPin, 
  Sparkles,
  Zap,
  Users,
  Shield,
  X,
  Clock,
  Trophy,
  Rocket,
  ArrowUpDown,
  ChevronUp,
  ChevronDown,
  Music,
  Volume2
} from 'lucide-react';

type PrimaryTab = 'global' | 'china';
type ChinaSubFilter = 'all' | 'exg' | 'fys' | 'ub' | 'zl' | '93x';

export const ServerRadarPreview: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState<PrimaryTab>('global');
  const [selectedChinaFilter, setSelectedChinaFilter] = useState<ChinaSubFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [telemetry, setTelemetry] = useState<LiveTelemetryPayload | null>(null);

  // Player Modal State & Sorting
  type PlayerSortField = 'name' | 'score' | 'duration';
  type PlayerSortOrder = 'asc' | 'desc';
  const [activeModalServer, setActiveModalServer] = useState<ZEServer | null>(null);
  const [modalSearch, setModalSearch] = useState('');
  const [playerSortField, setPlayerSortField] = useState<PlayerSortField>('duration');
  const [playerSortOrder, setPlayerSortOrder] = useState<PlayerSortOrder>('desc');
  const [showMusicModal, setShowMusicModal] = useState(false);

  const handlePlayerSort = (field: PlayerSortField) => {
    if (playerSortField === field) {
      setPlayerSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setPlayerSortField(field);
      setPlayerSortOrder(field === 'name' ? 'asc' : 'desc');
    }
  };

  // Initial & periodic telemetry fetch (auto-refreshes every 5s with cache-busting)
  const loadTelemetry = useCallback(async () => {
    const data = await fetchLiveTelemetry();
    if (data) {
      setTelemetry(data);
    }
  }, []);

  useEffect(() => {
    loadTelemetry();
    // 5-second automatic polling loop for near-real-time updates
    const pollTimer = setInterval(() => {
      fetchLiveTelemetry().then((data) => {
        if (data) setTelemetry(data);
      });
    }, 5000);
    return () => clearInterval(pollTimer);
  }, [loadTelemetry]);

  // 1-second ticker for live map elapsed counters
  const [nowSec, setNowSec] = useState(() => Math.floor(Date.now() / 1000));
  useEffect(() => {
    const timer = setInterval(() => {
      setNowSec(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Featured GFL server definition & live telemetry
  const gflServer = useMemo(() => ZE_SERVERS.find((s) => s.id === 'gfl') || ZE_SERVERS[0], []);
  const gflLive = telemetry?.servers?.['gfl'];
  const gflMap = gflLive?.map && gflLive.map !== '-' ? gflLive.map : gflServer.defaultMap;
  const gflMapStart = getMapStartTime('gfl', gflMap, gflLive?.map_start_time);
  const gflMapElapsed = Math.max(0, nowSec - gflMapStart);
  const gflRegionalPing = getEstimatedRegionalPing(gflServer.region);

  // Global servers (5 nodes - strictly non-China, excluding premier featured GFL)
  const globalServers = useMemo(() => {
    return ZE_SERVERS.filter((s) => s.regionCategory !== 'china' && s.id !== 'gfl');
  }, []);

  // China servers (35 nodes)
  const chinaServers = useMemo(() => {
    return ZE_SERVERS.filter((s) => s.regionCategory === 'china');
  }, []);

  // Filtered servers based on active primary tab & search
  const filteredServers = useMemo(() => {
    const baseList = selectedTab === 'global' ? globalServers : chinaServers;

    return baseList.filter((server) => {
      // Planet China Sub-Filter
      if (selectedTab === 'china') {
        if (selectedChinaFilter !== 'all' && server.cluster !== selectedChinaFilter) {
          return false;
        }
      }

      // Search Query Filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const liveInfo = telemetry?.servers?.[server.id];
        const matchesName = server.name.toLowerCase().includes(q);
        const matchesRegion = server.region.toLowerCase().includes(q);
        const matchesHost = `${server.host}:${server.port}`.toLowerCase().includes(q);
        const matchesDefaultMap = server.defaultMap?.toLowerCase().includes(q) ?? false;
        const matchesLiveMap = liveInfo?.map?.toLowerCase().includes(q) ?? false;
        const matchesCluster = server.clusterName.toLowerCase().includes(q);
        return matchesName || matchesRegion || matchesHost || matchesDefaultMap || matchesLiveMap || matchesCluster;
      }

      return true;
    });
  }, [selectedTab, selectedChinaFilter, searchQuery, globalServers, chinaServers, telemetry]);

  const handleCopy = (server: ZEServer) => {
    const cmd = `connect ${server.host}:${server.port}`;
    navigator.clipboard.writeText(cmd);
    setCopiedId(server.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Modal player filtering & sorting
  const activePlayersList = useMemo(() => {
    if (!activeModalServer) return [];
    const serverLive = telemetry?.servers?.[activeModalServer.id];
    const list: PlayerEntry[] = serverLive?.players_list || [];
    const filtered = !modalSearch.trim()
      ? [...list]
      : list.filter((p) => p.name.toLowerCase().includes(modalSearch.toLowerCase()));

    return filtered.sort((a, b) => {
      let cmp = 0;
      if (playerSortField === 'name') {
        cmp = a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
      } else if (playerSortField === 'score') {
        cmp = a.score - b.score;
      } else if (playerSortField === 'duration') {
        cmp = (a.seconds || 0) - (b.seconds || 0);
      }
      return playerSortOrder === 'asc' ? cmp : -cmp;
    });
  }, [activeModalServer, telemetry, modalSearch, playerSortField, playerSortOrder]);

  return (
    <section id="server-radar" className="relative w-full max-w-6xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 border-b border-lime-500/30 pb-5">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-lime-950/80 text-lime-300 border border-lime-500/50">
              MODULE 02 // DIRECT GAME CONNECTOR
            </span>
            <span className="text-[10px] font-code px-2 py-0.5 rounded bg-emerald-950/90 text-emerald-300 border border-emerald-500/50 flex items-center gap-1.5 uppercase font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              LIVE RADAR
            </span>
            <span className="text-xs font-code text-slate-400">
              COMMUNITY SERVERS // 128 TICK
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider">
            ZOMBIE ESCAPE SERVER BROWSER
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-3xl">
            Live CS2 Zombie Escape server radar with real active maps, live player counts, and player rosters. Click <strong>"CONNECT VIA STEAM"</strong> to launch CS2 and join instantly!
          </p>
        </div>

        {/* Global Live Stats */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-950/80 border border-slate-800 px-3.5 py-2 rounded-xl text-xs font-code text-slate-300 shadow-md">
            <Radio className="w-3.5 h-3.5 text-lime-400 animate-pulse" />
            <span>
              <strong className="text-lime-300">{telemetry?.online_servers ?? 33}</strong> / {ZE_SERVERS.length} NODES ONLINE
            </span>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* PINNED PREMIER FEATURED GFL CARD                                     */}
      {/* ==================================================================== */}
      <div className="mb-8 p-6 rounded-2xl bg-gradient-to-br from-slate-950/95 via-slate-900/90 to-amber-950/40 border border-amber-500/50 shadow-[0_0_35px_rgba(251,191,36,0.18)] backdrop-blur-md relative overflow-hidden">
        {/* Top-Right Corner: GFL Community Links (Website & Discord) */}
        <div className="sm:absolute sm:top-5 sm:right-6 flex items-center gap-2.5 z-10 mb-3 sm:mb-0">
          {gflServer.website && (
            <a
              href={gflServer.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-code text-slate-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors px-2.5 py-1 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 shadow-sm"
              title="Visit GFL Clan Portal"
            >
              <span>Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {gflServer.discord && (
            <a
              href={gflServer.discord}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-code text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 transition-colors font-medium px-2.5 py-1 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-indigo-500/50 shadow-sm"
              title="Join GFL Clan Official Discord"
            >
              <span>Discord</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Left Info */}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="px-2 py-0.5 text-[10px] font-code rounded bg-amber-950/90 text-amber-300 border border-amber-500/60 font-bold flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-400" />
                PREMIER FEATURED SERVER
              </span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-bold">
                🇺🇸 US CHICAGO
              </span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-500/50 font-bold">
                GLOBAL SERVER
              </span>
              <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 font-bold">
                128 TICK
              </span>
            </div>

            <h3 className="text-xl md:text-2xl font-cyber font-black text-white mb-2 flex items-center gap-2">
              <span>{gflServer.name}</span>
            </h3>

            {/* Big Map Preview & Telemetry Display */}
            <div className="flex flex-col md:flex-row items-start md:items-center gap-4 bg-slate-900/90 p-3 rounded-xl border border-slate-800 mb-3">
              {/* Prominent Map Thumbnail */}
              <div className="relative w-28 h-18 sm:w-32 sm:h-20 rounded-lg overflow-hidden border border-fuchsia-500/40 bg-slate-950 flex-shrink-0 shadow-[0_0_15px_rgba(255,0,128,0.15)] group">
                <img 
                  src={getMapThumbnailUrl(gflMap)} 
                  alt={gflMap}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=300&q=80';
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent pointer-events-none" />
                <span className="absolute bottom-1 left-1.5 text-[9px] font-cyber text-fuchsia-300 font-bold drop-shadow uppercase">
                  MAP INTEL
                </span>
              </div>

              {/* Map Information & Telemetry Stats */}
              <div className="flex flex-col gap-2 flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 text-xs font-code">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <MapPin className="w-3.5 h-3.5 text-fuchsia-400 flex-shrink-0" />
                    <span className="text-slate-400">Map:</span>
                    <strong className="text-sm font-bold text-fuchsia-300 truncate max-w-[200px]">
                      {gflMap}
                    </strong>
                  </div>

                  <span className="text-cyan-300 font-code text-xs font-bold bg-cyan-950/90 px-2 py-0.5 rounded-md border border-cyan-500/40 flex items-center gap-1 shadow-[0_0_10px_rgba(0,240,255,0.25)]">
                    <Clock className="w-3 h-3 text-cyan-400 animate-pulse" />
                    {formatMapElapsed(gflMapElapsed)} on map
                  </span>

                  <a
                    href={getMap3DViewerUrl(gflMap)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[11px] font-code px-2 py-0.5 rounded-md bg-blue-950/80 text-blue-300 hover:text-white border border-blue-500/40 hover:border-blue-400 flex items-center gap-1 transition-colors shadow-sm"
                    title="Explore 3D Map layout on maps.cybo.dev (Powered by cybo)"
                  >
                    <Globe className="w-3 h-3 text-blue-400" />
                    <span>3D Map ↗</span>
                  </a>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs font-code text-slate-300">
                  <div className="flex items-center gap-1.5 bg-slate-950/80 px-2 py-0.5 rounded-md border border-slate-800">
                    <Users className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-slate-400">Players:</span>
                    <strong className="text-emerald-300 font-bold">
                      {gflLive?.players && gflLive.players !== '-/-' ? gflLive.players : '62/64'}
                    </strong>
                  </div>

                  <div className="flex items-center gap-1.5 bg-slate-950/80 px-2 py-0.5 rounded-md border border-slate-800" title={`Estimated latency: ${gflRegionalPing.userLocation} ➔ ${gflRegionalPing.serverLocation}`}>
                    <Radio className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-slate-400">Est. Ping:</span>
                    <strong className="text-cyan-300 font-bold">
                      {gflRegionalPing.display}
                    </strong>
                    <span className="text-[10px] text-slate-400 font-normal">({gflRegionalPing.route})</span>
                  </div>

                  <div className="text-[11px] font-code text-slate-400">
                    <code>IP: {gflServer.host}:{gflServer.port}</code>
                  </div>
                </div>
              </div>
            </div>

            {/* Live Match Intelligence (Round Scores, Extends & Soundtrack) - Always Visible */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="px-2.5 py-1 rounded-lg text-xs font-code bg-slate-900/90 border border-slate-800 text-slate-300 flex items-center gap-2">
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  🛡️ Humans: {telemetry?.gfl_match_now ? telemetry.gfl_match_now.human_score : 0}
                </span>
                <span className="text-slate-500">vs</span>
                <span className="text-rose-400 font-bold flex items-center gap-1">
                  🧟 Zombies: {telemetry?.gfl_match_now ? telemetry.gfl_match_now.zombie_score : 0}
                </span>
              </span>

              <span className="px-2.5 py-1 rounded-lg text-xs font-code bg-slate-900/90 border border-slate-800 text-amber-300 font-semibold flex items-center gap-1">
                <Clock className="w-3 h-3 text-amber-400" />
                Extends: {telemetry?.gfl_match_now ? telemetry.gfl_match_now.extend_count : 0}/3
              </span>

              {/* Soundtrack Button - ALWAYS Visible */}
              <button
                onClick={() => setShowMusicModal(true)}
                className={`px-2.5 py-1 rounded-lg text-xs font-code flex items-center gap-1.5 transition-all cursor-pointer border ${
                  telemetry?.gfl_map_musics && telemetry.gfl_map_musics.length > 0
                    ? 'bg-purple-950/90 hover:bg-purple-900 border-purple-500/50 text-purple-200 hover:text-white shadow-[0_0_12px_rgba(168,85,247,0.3)]'
                    : 'bg-slate-900/90 hover:bg-slate-800 border-slate-700 text-purple-300/80 hover:text-purple-200'
                }`}
                title="View map custom soundtrack with YouTube links"
              >
                <Music className="w-3.5 h-3.5 text-purple-400" />
                <span>
                  Soundtrack {telemetry?.gfl_map_musics && telemetry.gfl_map_musics.length > 0 
                    ? `(${telemetry.gfl_map_musics.length} Tracks)` 
                    : '(Intel)'}
                </span>
              </button>
            </div>

            {/* Desktop Slot Sniper Banner */}
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-center gap-2.5 text-xs font-tech text-slate-300">
              <Zap className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span>
                <strong>Server Full at 64/64?</strong> The <a href="#cs2-command" className="text-fuchsia-400 underline hover:text-fuchsia-300 font-code">CS2 Command Center desktop app</a> includes an automated <strong>Silent Slot Sniper</strong> that runs in your Windows tray and auto-joins the millisecond a player disconnects!
              </span>
            </div>
          </div>

          {/* Right Action CTAs */}
          <div className="flex flex-col sm:flex-row lg:flex-col items-stretch lg:items-end justify-center gap-2.5 flex-shrink-0">
            <a
              href={`steam://connect/${gflServer.host}:${gflServer.port}`}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 via-orange-500 to-lime-500 hover:from-amber-400 hover:to-lime-400 text-slate-950 font-cyber text-xs tracking-wider font-black rounded-xl shadow-[0_0_25px_rgba(251,191,36,0.4)] transition-all cursor-pointer transform hover:-translate-y-0.5"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>CONNECT VIA STEAM</span>
            </a>

            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setActiveModalServer(gflServer);
                  setModalSearch('');
                }}
                className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-amber-400 text-slate-200 rounded-lg text-xs font-code transition-colors cursor-pointer"
                title="View active players connected to GFL"
              >
                <Users className="w-3.5 h-3.5 text-amber-400" />
                <span>👥 PLAYERS</span>
              </button>

              <button
                onClick={() => handleCopy(gflServer)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-lime-400 text-slate-200 rounded-lg text-xs font-code transition-colors cursor-pointer flex items-center gap-1"
                title="Copy console connect command"
              >
                {copiedId === gflServer.id ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400 font-bold">COPIED</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-slate-400" />
                    <span>COPY IP</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SIMPLIFIED PRIMARY TABS: GLOBAL (6) vs PLANET CHINA (35)             */}
      {/* ==================================================================== */}
      <div className="flex flex-col gap-3 mb-6">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
          
          {/* Clean 2-Tab Navigation */}
          <div className="flex items-center gap-2 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 backdrop-blur-md">
            {/* Global Servers Tab */}
            <button
              onClick={() => setSelectedTab('global')}
              className={`px-4 py-2 text-xs font-cyber tracking-wider font-bold rounded-lg transition-all cursor-pointer flex items-center gap-2 ${
                selectedTab === 'global'
                  ? 'bg-gradient-to-r from-lime-500/20 to-emerald-500/20 text-lime-300 border border-lime-400/60 shadow-[0_0_15px_rgba(57,255,20,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Globe className="w-3.5 h-3.5 text-lime-400" />
              <span>GLOBAL SERVERS ({globalServers.length})</span>
            </button>

            {/* Planet China Meme Tab */}
            <button
              onClick={() => {
                setSelectedTab('china');
                setSelectedChinaFilter('all');
              }}
              className={`px-4 py-2 text-xs font-cyber tracking-wider font-bold rounded-lg transition-all cursor-pointer flex items-center gap-2 ${
                selectedTab === 'china'
                  ? 'bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-rose-300 border border-rose-400/60 shadow-[0_0_15px_rgba(244,63,94,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Rocket className="w-3.5 h-3.5 text-rose-400 animate-bounce" />
              <span>PLANET CHINA ({chinaServers.length}) 🚀🇨🇳</span>
            </button>
          </div>

          {/* Search Input */}
          <div className="relative min-w-[280px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by server name, map, or IP..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs font-code text-slate-200 placeholder-slate-500 focus:outline-none focus:border-lime-400 transition-colors"
            />
          </div>

        </div>

        {/* Planet China Sub-Clan Filter Bar (Only shown on Planet China tab) */}
        {selectedTab === 'china' && (
          <div className="flex flex-wrap items-center gap-2 p-2.5 rounded-xl bg-slate-950/90 border border-rose-500/30 backdrop-blur-md">
            <span className="text-[11px] font-code text-rose-400 font-bold px-2 flex items-center gap-1">
              CLAN HUBS:
            </span>
            <button
              onClick={() => setSelectedChinaFilter('all')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === 'all'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              ALL PLANET CHINA (35)
            </button>
            <button
              onClick={() => setSelectedChinaFilter('exg')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === 'exg'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              EXG 社区 (16)
            </button>
            <button
              onClick={() => setSelectedChinaFilter('fys')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === 'fys'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              风云社 / FyS (6)
            </button>
            <button
              onClick={() => setSelectedChinaFilter('ub')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === 'ub'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              萌UB / MoeUB (6)
            </button>
            <button
              onClick={() => setSelectedChinaFilter('zl')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === 'zl'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              僵尸乐园 / ZL (5)
            </button>
            <button
              onClick={() => setSelectedChinaFilter('93x')}
              className={`px-2.5 py-1 text-xs font-code rounded-lg transition-all cursor-pointer ${
                selectedChinaFilter === '93x'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              93X 社区 (2)
            </button>
          </div>
        )}
      </div>

      {/* ==================================================================== */}
      {/* SERVER GRID                                                          */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredServers.map((server) => {
          const isCopied = copiedId === server.id;
          const steamProtocolUrl = `steam://connect/${server.host}:${server.port}`;
          const liveInfo = telemetry?.servers?.[server.id];
          const isOnline = liveInfo?.online ?? true;
          const currentMap = liveInfo?.map && liveInfo.map !== '-' ? liveInfo.map : server.defaultMap;
          const currentPlayers = liveInfo?.players && liveInfo.players !== '-/-' ? liveInfo.players : null;
          const mapStart = getMapStartTime(server.id, currentMap, liveInfo?.map_start_time);
          const mapDuration = Math.max(0, nowSec - mapStart);
          const regionalPing = getEstimatedRegionalPing(server.region);

          return (
            <div
              key={server.id}
              className={`relative p-5 rounded-xl border transition-all backdrop-blur-md flex flex-col justify-between group ${
                server.isFeatured
                  ? 'bg-gradient-to-br from-slate-950/90 via-slate-900/70 to-amber-950/30 border-amber-500/40 shadow-[0_0_25px_rgba(251,191,36,0.15)]'
                  : 'bg-slate-950/60 border-slate-800 hover:border-lime-500/40 hover:shadow-[0_0_20px_rgba(57,255,20,0.1)]'
              }`}
            >
              <div>
                {/* Top Badge Row */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-bold">
                      {server.countryCode}
                    </span>
                    <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-900/90 border border-slate-800 text-slate-400">
                      {server.clusterName}
                    </span>
                    {server.isFeatured && (
                      <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/90 text-amber-300 border border-amber-500/50 flex items-center gap-1 font-bold">
                        <Sparkles className="w-3 h-3 text-amber-400" /> FEATURED
                      </span>
                    )}
                    <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
                      128T
                    </span>
                  </div>

                  {/* External Community Links */}
                  <div className="flex items-center gap-2">
                    {server.discord && (
                      <a
                        href={server.discord}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] font-code text-slate-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                      >
                        Discord <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    {server.website && (
                      <a
                        href={server.website}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] font-code text-slate-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                      >
                        Portal <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>

                {/* Server Name */}
                <h3 className="font-cyber font-bold text-white text-base group-hover:text-lime-300 transition-colors mb-1 truncate">
                  {server.name}
                </h3>

                {/* Region & Host IP */}
                <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs font-tech text-slate-400 mb-3">
                  <span className="flex items-center gap-1">
                    <Globe className="w-3 h-3 text-cyan-400" />
                    {server.region}
                  </span>
                  <span className="text-[11px] font-code text-slate-400">
                    <code>{server.host}:{server.port}</code>
                  </span>
                </div>

                {/* Live Telemetry Pill Row */}
                <div className="flex flex-wrap items-center gap-2 mb-4">
                  {/* Current Active Map & Live Timer */}
                  <div className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-code text-slate-300">
                    {/* Prominent Map Thumbnail */}
                    <div className="w-14 h-9 sm:w-16 sm:h-10 rounded-md overflow-hidden border border-slate-700 bg-slate-950 flex-shrink-0 shadow-sm group-hover:border-lime-400/50 transition-colors">
                      <img 
                        src={getMapThumbnailUrl(currentMap)} 
                        alt={currentMap} 
                        className="w-full h-full object-cover"
                        onError={(e) => { 
                          (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=300&q=80';
                        }}
                      />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-1 text-[11px] text-slate-400">
                        <MapPin className="w-3 h-3 text-fuchsia-400 flex-shrink-0" />
                        <span>Map:</span>
                        <strong className="text-fuchsia-300 font-bold truncate max-w-[120px] sm:max-w-[150px]">
                          {currentMap || 'ze_escape'}
                        </strong>
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-cyan-300 text-[10px] font-bold bg-cyan-950/80 px-1.5 py-0.2 rounded border border-cyan-500/30 flex items-center gap-0.5">
                          <Clock className="w-2.5 h-2.5 text-cyan-400" />
                          {formatMapElapsed(mapDuration)}
                        </span>
                        <a
                          href={getMap3DViewerUrl(currentMap)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] font-code px-1.5 py-0.2 rounded bg-blue-950/80 text-blue-300 hover:text-white border border-blue-500/30 hover:border-blue-400 flex items-center gap-0.5 transition-colors"
                          title="Explore 3D Map model on maps.cybo.dev (Powered by cybo)"
                        >
                          <span>3D</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    </div>
                  </div>

                  {/* Player Count */}
                  {currentPlayers ? (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-code">
                      <Users className="w-3 h-3 text-emerald-400" />
                      <span className="text-slate-400">Players:</span>
                      <span className="text-emerald-300 font-bold">{currentPlayers}</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-code text-slate-400">
                      <Users className="w-3 h-3 text-slate-500" />
                      <span>{isOnline ? 'Online' : 'Offline'}</span>
                    </div>
                  )}

                  {/* Realistic Estimated Regional Ping */}
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-code text-cyan-300" title={`Estimated route latency: ${regionalPing.userLocation} ➔ ${regionalPing.serverLocation}`}>
                    <Radio className="w-3 h-3 text-cyan-400" />
                    <span className="font-bold">{regionalPing.display}</span>
                    <span className="text-[10px] text-slate-500 font-normal hidden sm:inline">({regionalPing.route})</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center gap-2">
                {/* 1-Click Steam Connect */}
                <a
                  href={steamProtocolUrl}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-gradient-to-r from-emerald-600 to-lime-600 hover:from-emerald-500 hover:to-lime-500 text-white font-cyber text-xs tracking-wider font-bold rounded-lg shadow-[0_0_15px_rgba(57,255,20,0.3)] transition-all cursor-pointer"
                  title="Directly launches Steam and connects to this server"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>CONNECT VIA STEAM</span>
                </a>

                {/* Non-China Server: Live Players Modal */}
                {server.allowPlayerRoster ? (
                  <button
                    onClick={() => {
                      setActiveModalServer(server);
                      setModalSearch('');
                    }}
                    className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-cyan-400 text-slate-300 hover:text-white rounded-lg text-xs font-code flex items-center gap-1 transition-colors cursor-pointer flex-shrink-0"
                    title="View real-time player list"
                  >
                    <Users className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="hidden sm:inline">PLAYERS</span>
                  </button>
                ) : (
                  <div
                    className="px-2.5 py-2 bg-slate-950 border border-slate-800/80 rounded-lg text-[10px] font-code text-slate-400 flex items-center gap-1 flex-shrink-0"
                    title="Player names query blocked by community privacy policy"
                  >
                    <Shield className="w-3 h-3 text-slate-400" />
                    <span className="hidden sm:inline">SHIELDED</span>
                  </div>
                )}

                {/* Copy IP Button */}
                <button
                  onClick={() => handleCopy(server)}
                  className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-lime-400 text-slate-300 hover:text-white rounded-lg text-xs font-code flex items-center gap-1 transition-colors cursor-pointer flex-shrink-0"
                  title="Copy console command: connect IP:PORT"
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400 font-bold hidden sm:inline">COPIED</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 text-slate-400" />
                      <span className="hidden sm:inline">COPY</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          );
        })}
      </div>

      {filteredServers.length === 0 && (
        <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
          <p className="text-sm font-code text-slate-400">
            No Zombie Escape servers match query "{searchQuery}".
          </p>
        </div>
      )}

      {/* ==================================================================== */}
      {/* LIVE PLAYERS ROSTER MODAL                                            */}
      {/* ==================================================================== */}
      {activeModalServer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-2xl bg-slate-950 border border-cyan-500/50 rounded-2xl p-6 shadow-[0_0_50px_rgba(0,240,255,0.25)] flex flex-col max-h-[85vh]">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 text-[10px] font-code rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-bold">
                    ACTIVE PLAYERS
                  </span>
                  <span className="text-xs font-code text-slate-400">
                    A2S_PLAYER LIVE STREAM
                  </span>
                </div>
                <h3 className="text-lg md:text-xl font-cyber font-bold text-white flex items-center gap-2">
                  <span>{activeModalServer.name}</span>
                </h3>
                <div className="flex items-center gap-3 text-xs font-code text-slate-400 mt-1">
                  <code>{activeModalServer.host}:{activeModalServer.port}</code>
                  <span>&bull;</span>
                  <span className="text-emerald-400">
                    {telemetry?.servers?.[activeModalServer.id]?.players || `${activePlayersList.length} Connected`}
                  </span>
                </div>
              </div>

              <button
                onClick={() => setActiveModalServer(null)}
                className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Search & Count Bar */}
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={modalSearch}
                  onChange={(e) => setModalSearch(e.target.value)}
                  placeholder="Filter players by name..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs font-code text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400 transition-colors"
                />
              </div>
              <span className="text-xs font-code text-cyan-300 flex-shrink-0">
                {activePlayersList.length} Players Listed
              </span>
            </div>

            {/* Players Table */}
            <div className="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-900/50">
              <table className="w-full text-left text-xs font-code">
                <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3 w-12 text-center text-slate-500">#</th>
                    <th 
                      onClick={() => handlePlayerSort('name')}
                      className="py-2.5 px-3 cursor-pointer hover:text-cyan-300 transition-colors select-none group"
                      title="Sort by Player Name (A-Z / Z-A)"
                    >
                      <div className="flex items-center gap-1.5">
                        <span>Player Name</span>
                        {playerSortField === 'name' ? (
                          playerSortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronDown className="w-3.5 h-3.5 text-cyan-400" />
                        ) : (
                          <ArrowUpDown className="w-3 h-3 text-slate-600 group-hover:text-slate-400 transition-colors" />
                        )}
                      </div>
                    </th>
                    <th 
                      onClick={() => handlePlayerSort('score')}
                      className="py-2.5 px-3 text-right cursor-pointer hover:text-emerald-300 transition-colors select-none group"
                      title="Sort by Score (Highest First / Lowest First)"
                    >
                      <div className="flex items-center justify-end gap-1.5">
                        <span>Score</span>
                        {playerSortField === 'score' ? (
                          playerSortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-emerald-400" /> : <ChevronDown className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <ArrowUpDown className="w-3 h-3 text-slate-600 group-hover:text-slate-400 transition-colors" />
                        )}
                      </div>
                    </th>
                    <th 
                      onClick={() => handlePlayerSort('duration')}
                      className="py-2.5 px-3 text-center cursor-pointer hover:text-cyan-300 transition-colors select-none group"
                      title="Sort by Session Duration (Longest Played / Recently Joined)"
                    >
                      <div className="flex items-center justify-center gap-1.5">
                        <span>Session Duration</span>
                        {playerSortField === 'duration' ? (
                          playerSortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronDown className="w-3.5 h-3.5 text-cyan-400" />
                        ) : (
                          <ArrowUpDown className="w-3 h-3 text-slate-600 group-hover:text-slate-400 transition-colors" />
                        )}
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50 text-slate-300">
                  {activePlayersList.length > 0 ? (
                    activePlayersList.map((player, idx) => (
                      <tr key={idx} className="hover:bg-cyan-950/20 transition-colors">
                        <td className="py-2 px-3 text-center text-slate-500">
                          {idx === 0 ? <Trophy className="w-3.5 h-3.5 text-amber-400 inline" /> : idx + 1}
                        </td>
                        <td className="py-2 px-3 font-semibold text-white">
                          {player.name}
                        </td>
                        <td className="py-2 px-3 text-right text-emerald-400 font-bold">
                          {player.score.toLocaleString()}
                        </td>
                        <td className="py-2 px-3 text-center text-slate-400 flex items-center justify-center gap-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{player.time}</span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-slate-500">
                        {modalSearch ? `No players match "${modalSearch}"` : 'No active player data currently available.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Modal Footer */}
            <div className="pt-4 border-t border-slate-800 mt-4 flex items-center justify-between text-[11px] font-tech text-slate-400">
              <span>
                Real-time query via Valve Source A2S_PLAYER protocol.
              </span>
              <a
                href={`steam://connect/${activeModalServer.host}:${activeModalServer.port}`}
                className="px-4 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-cyber text-xs rounded-lg transition-all"
              >
                JOIN SERVER NOW
              </a>
            </div>

          </div>
        </div>
      )}

      {/* GFL Map Soundtrack Modal */}
      {showMusicModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-950 border border-purple-500/50 rounded-2xl p-6 max-w-2xl w-full max-h-[85vh] flex flex-col shadow-[0_0_50px_rgba(168,85,247,0.25)] relative">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-800 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded text-[10px] font-cyber bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold">
                    OFFICIAL SOUNDTRACKS
                  </span>
                  <span className="text-xs font-code text-slate-400">
                    {telemetry?.gfl_map_musics ? telemetry.gfl_map_musics.length : 0} Tracks Available
                  </span>
                </div>
                <h3 className="text-lg font-cyber font-bold text-white flex items-center gap-2">
                  <Music className="w-5 h-5 text-purple-400" />
                  <span>{gflMap}</span>
                </h3>
                <p className="text-xs font-tech text-slate-400 mt-1">
                  Custom soundtracks mapped for this Zombie Escape level. Click to stream on YouTube!
                </p>
              </div>

              <button
                onClick={() => setShowMusicModal(false)}
                className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Tracklist List or Empty State */}
            {telemetry?.gfl_map_musics && telemetry.gfl_map_musics.length > 0 ? (
              <div className="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-900/50 divide-y divide-slate-800/60 p-2 space-y-1">
                {telemetry.gfl_map_musics.map((song, idx) => {
                  const ytId = song.youtube_music || song.youtube_video;
                  const ytUrl = ytId ? `https://www.youtube.com/watch?v=${ytId}` : null;
                  return (
                    <div key={idx} className="p-3 rounded-lg hover:bg-purple-950/20 transition-colors flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="w-6 text-center text-xs font-code text-purple-400/80 font-bold">
                          {idx + 1}
                        </span>
                        <div className="min-w-0">
                          <div className="text-xs font-code font-bold text-slate-100 truncate">
                            {song.name}
                          </div>
                          <div className="flex items-center gap-2 text-[11px] font-tech text-slate-400 mt-0.5">
                            <Clock className="w-3 h-3 text-slate-500" />
                            <span>{formatMapElapsed(Math.floor(song.duration || 0))}</span>
                          </div>
                        </div>
                      </div>

                      {ytUrl ? (
                        <a
                          href={ytUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 px-3 py-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-500/40 text-red-300 hover:text-white text-xs font-code flex items-center gap-1.5 transition-colors"
                        >
                          <Play className="w-3 h-3 fill-current text-red-400" />
                          <span>YouTube ↗</span>
                        </a>
                      ) : (
                        <span className="text-[11px] font-tech text-slate-600">No stream link</span>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800/80 my-4 flex-1 flex flex-col items-center justify-center">
                <Music className="w-12 h-12 text-purple-400/50 mb-3" />
                <h4 className="text-base font-cyber font-bold text-slate-200 mb-1">
                  No Custom Soundtracks Cataloged for {gflMap}
                </h4>
                <p className="text-xs font-tech text-slate-400 max-w-md mx-auto leading-relaxed">
                  This map either uses standard ambient soundscapes or custom music entity triggers have not been indexed in the community audio database yet.
                </p>
                <div className="mt-4 p-3 rounded-lg bg-purple-950/40 border border-purple-500/30 text-xs font-code text-purple-300 max-w-md mx-auto">
                  💡 Popular maps with active soundtracks: <strong>ze_journey_p</strong> (10 tracks), <strong>ze_isla_nublar_p</strong> (3 tracks), <strong>ze_frostdrake_tower_p</strong> (4 tracks).
                </div>
              </div>
            )}

            {/* Modal Footer */}
            <div className="pt-4 border-t border-slate-800 mt-4 flex items-center justify-between text-[11px] font-tech text-slate-400">
              <span className="flex items-center gap-1.5">
                <Volume2 className="w-3.5 h-3.5 text-purple-400" />
                Audio tracks extracted from CS2 workshop map entities
              </span>
              <button
                onClick={() => setShowMusicModal(false)}
                className="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 font-code text-xs rounded-lg transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Community Attribution & Credits */}
      <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-purple-950/40 via-slate-950/80 to-cyan-950/40 border border-purple-500/30 backdrop-blur-md">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-4 h-4 text-purple-400 flex-shrink-0" />
            <div className="text-xs font-tech text-slate-300">
              <span className="font-bold text-white uppercase tracking-wider">Community Intelligence Credits: </span>
              Special thanks to <strong className="text-purple-300">queeniemella (InterStella0)</strong> from{' '}
              <a href="https://zegraph.xyz" target="_blank" rel="noopener noreferrer" className="text-purple-400 underline hover:text-purple-300 font-code">zegraph.xyz</a>{' '}
              for the live ZE match score telemetry & map thumbnail CDN, and{' '}
              <strong className="text-cyan-300">cybo</strong> from{' '}
              <a href="https://maps.cybo.dev" target="_blank" rel="noopener noreferrer" className="text-cyan-400 underline hover:text-cyan-300 font-code">maps.cybo.dev</a>{' '}
              for interactive 3D map spatial models.
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0 text-[11px] font-code">
            <a href="https://zegraph.xyz" target="_blank" rel="noopener noreferrer" className="px-2.5 py-1 rounded-lg bg-purple-900/30 hover:bg-purple-900/50 border border-purple-500/40 text-purple-200 transition-colors">
              ZE Graph ↗
            </a>
            <a href="https://maps.cybo.dev" target="_blank" rel="noopener noreferrer" className="px-2.5 py-1 rounded-lg bg-cyan-900/30 hover:bg-cyan-900/50 border border-cyan-500/40 text-cyan-200 transition-colors">
              Cybo 3D ↗
            </a>
          </div>
        </div>
      </div>

      {/* Bottom Information Notice */}
      <div className="mt-8 p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex items-center gap-3 text-xs font-tech text-slate-400">
        <Zap className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span>
          <strong>Direct Steam Connect Protocol:</strong> Clicking <strong>"CONNECT VIA STEAM"</strong> invokes <code className="text-lime-300">steam://connect/IP:PORT</code>, automatically opening Counter-Strike 2 directly into the community server without typing console commands.
        </span>
      </div>
    </section>
  );
};
