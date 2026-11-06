import React, { useState, useMemo } from 'react';
import { ZE_SERVERS, type ZEServer } from '../data/zeServers';
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
  Zap
} from 'lucide-react';

type RegionFilter = 'all' | 'featured' | 'na' | 'eu' | 'asia' | 'china';

export const ServerRadarPreview: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState<RegionFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const filteredServers = useMemo(() => {
    return ZE_SERVERS.filter((server) => {
      // Filter by category
      if (selectedFilter === 'featured' && !server.isFeatured) return false;
      if (selectedFilter === 'na' && server.regionCategory !== 'na') return false;
      if (selectedFilter === 'eu' && server.regionCategory !== 'eu') return false;
      if (selectedFilter === 'asia' && server.regionCategory !== 'asia') return false;
      if (selectedFilter === 'china' && server.regionCategory !== 'china') return false;

      // Filter by search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = server.name.toLowerCase().includes(q);
        const matchesRegion = server.region.toLowerCase().includes(q);
        const matchesHost = server.host.toLowerCase().includes(q);
        const matchesMap = server.defaultMap?.toLowerCase().includes(q) ?? false;
        return matchesName || matchesRegion || matchesHost || matchesMap;
      }

      return true;
    });
  }, [selectedFilter, searchQuery]);

  const handleCopy = (server: ZEServer) => {
    const cmd = `connect ${server.host}:${server.port}`;
    navigator.clipboard.writeText(cmd);
    setCopiedId(server.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <section id="server-radar" className="relative w-full max-w-6xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-lime-500/30 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-lime-950/80 text-lime-300 border border-lime-500/50">
              MODULE 02 // DIRECT GAME CONNECTOR
            </span>
            <span className="text-xs font-code text-slate-400">
              COMMUNITY SERVERS // 128 TICK
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
            ZOMBIE ESCAPE SERVER BROWSER
            <span className="text-xs font-code px-2 py-1 bg-emerald-950 text-emerald-300 border border-emerald-500/40 rounded uppercase animate-pulse">
              LIVE DIRECTORY
            </span>
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-3xl">
            Direct Steam Protocol Launcher for Counter-Strike 2 Zombie Escape. Click <strong>"CONNECT VIA STEAM"</strong> on any server to launch CS2 and join immediately without opening the console!
          </p>
        </div>

        {/* Global Stats Pill */}
        <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 px-3 py-2 rounded-xl text-xs font-code">
          <Radio className="w-4 h-4 text-lime-400 animate-pulse" />
          <span className="text-slate-300">
            <strong className="text-lime-300">{ZE_SERVERS.length}</strong> ACTIVE NODES LISTED
          </span>
        </div>
      </div>

      {/* Control Bar: Filters & Search */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 mb-6">
        
        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 backdrop-blur-md">
          <button
            onClick={() => setSelectedFilter('all')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
              selectedFilter === 'all'
                ? 'bg-lime-500/20 text-lime-300 border border-lime-400/60 shadow-[0_0_12px_rgba(57,255,20,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ALL ({ZE_SERVERS.length})
          </button>
          <button
            onClick={() => setSelectedFilter('featured')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer flex items-center gap-1 ${
              selectedFilter === 'featured'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-400/60 shadow-[0_0_12px_rgba(251,191,36,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3 h-3 text-amber-400" />
            FEATURED
          </button>
          <button
            onClick={() => setSelectedFilter('na')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
              selectedFilter === 'na'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-[0_0_12px_rgba(0,240,255,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            NORTH AMERICA
          </button>
          <button
            onClick={() => setSelectedFilter('eu')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
              selectedFilter === 'eu'
                ? 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-400/60 shadow-[0_0_12px_rgba(255,0,127,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            EUROPE
          </button>
          <button
            onClick={() => setSelectedFilter('asia')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
              selectedFilter === 'asia'
                ? 'bg-sky-500/20 text-sky-300 border border-sky-400/60 shadow-[0_0_12px_rgba(56,189,248,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ASIA (JP / KR)
          </button>
          <button
            onClick={() => setSelectedFilter('china')}
            className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
              selectedFilter === 'china'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-400/60 shadow-[0_0_12px_rgba(244,63,94,0.3)]'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            CHINA CLUSTERS
          </button>
        </div>

        {/* Live Search Input */}
        <div className="relative min-w-[260px]">
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

      {/* Server Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredServers.map((server) => {
          const isCopied = copiedId === server.id;
          const steamProtocolUrl = `steam://connect/${server.host}:${server.port}`;

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
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-bold">
                      {server.countryCode}
                    </span>
                    {server.isFeatured && (
                      <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/90 text-amber-300 border border-amber-500/50 flex items-center gap-1 font-bold">
                        <Sparkles className="w-3 h-3 text-amber-400" /> FEATURED
                      </span>
                    )}
                    <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
                      128 TICK
                    </span>
                  </div>

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
                      Web <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                {/* Server Name */}
                <h3 className="font-cyber font-bold text-white text-base group-hover:text-lime-300 transition-colors mb-1 truncate">
                  {server.name}
                </h3>

                {/* Region & Default Map */}
                <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs font-tech text-slate-400 mb-4">
                  <span className="flex items-center gap-1">
                    <Globe className="w-3 h-3 text-cyan-400" />
                    {server.region}
                  </span>
                  {server.defaultMap && (
                    <span className="flex items-center gap-1 text-slate-300">
                      <MapPin className="w-3 h-3 text-fuchsia-400" />
                      <code className="text-[11px] text-fuchsia-300">{server.defaultMap}</code>
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons: Direct Steam Connect + Copy IP */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center gap-2">
                {/* 1-Click Steam Connect Button */}
                <a
                  href={steamProtocolUrl}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-gradient-to-r from-emerald-600 to-lime-600 hover:from-emerald-500 hover:to-lime-500 text-white font-cyber text-xs tracking-wider font-bold rounded-lg shadow-[0_0_15px_rgba(57,255,20,0.3)] transition-all cursor-pointer"
                  title="Directly launches Steam and connects to this server"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>CONNECT VIA STEAM</span>
                </a>

                {/* Copy IP Button */}
                <button
                  onClick={() => handleCopy(server)}
                  className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-lime-400 text-slate-300 hover:text-white rounded-lg text-xs font-code flex items-center gap-1.5 transition-colors cursor-pointer flex-shrink-0"
                  title="Copy console command: connect IP:PORT"
                >
                  {isCopied ? (
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

      {/* Bottom Helpful Pro-Tip */}
      <div className="mt-6 p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex items-center gap-3 text-xs font-tech text-slate-400">
        <Zap className="w-4 h-4 text-amber-400 flex-shrink-0" />
        <span>
          <strong>How Direct Connect Works:</strong> Clicking <strong>"CONNECT VIA STEAM"</strong> invokes the Windows Steam client protocol (<code className="text-lime-300">steam://connect/</code>), automatically launching CS2 and queueing connection to the selected Zombie Escape map without typing anything into the game console.
        </span>
      </div>
    </section>
  );
};
