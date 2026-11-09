import React, { useState } from 'react';
import { Mail, Copy, Check, Send, ShieldCheck, Terminal, Radio } from 'lucide-react';

export const DeployHudFooter: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const contactEmail = 'contact@geronimohq.com';

  const copyEmail = () => {
    navigator.clipboard.writeText(contactEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <footer id="contact" className="relative w-full border-t border-[#1E2E26] bg-[#070B09]/95 backdrop-blur-xl pt-12 pb-8 px-4 mt-16 z-10">
      <div className="max-w-6xl mx-auto">
        
        {/* Main Footer Hub */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10 pb-8 border-b border-[#1E2E26]">
          
          {/* Col 1: About GeronimoHQ */}
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                GERONIMO<span className="text-cyan-400">HQ</span> // BASE OPS
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-tech leading-relaxed">
              Personal digital headquarters of Geronimo. Dedicated to high-performance gaming software, custom Counter-Strike 2 telemetry, and underground zombie escape communities.
            </p>
            <div className="flex items-center gap-2 text-[11px] font-code text-cyan-400/80">
              <Radio className="w-3.5 h-3.5 text-cyan-400" />
              <span>FREQUENCY: ENCRYPTED // 24/7 ONLINE</span>
            </div>

            {/* Troll Base Address & Phone Hotline */}
            <div className="p-3 bg-slate-900/70 border border-slate-800 rounded-xl space-y-1.5 text-[11px] font-code text-slate-400">
              <div className="text-cyan-300 font-bold flex items-center gap-1.5">
                <span>🏢 HQ PHYSICAL LOCATION:</span>
              </div>
              <p className="text-slate-300 leading-tight">
                Sector 7G, Mako Reactor Core #1, Midgar Upper Plate <br />
                <span className="text-slate-400">(Sub-Basement 07, Cyber Bunker, GeronimoHQ)</span>
              </p>
              <div className="text-amber-300 font-bold pt-1 flex items-center gap-1">
                <span>📞 BANANA HOTLINE:</span>
                <span className="text-amber-200">1-800-RAM-DOWNLOAD (Ext. 6090-TI)</span>
              </div>
              <div className="text-[10px] text-slate-400">
                Alt Relay: +1 (420) 69-PEPE-HQ &bull; Toll-Free 24/7 Meme Dispatch
              </div>
            </div>
          </div>

          {/* Col 2: Direct Contact Transmission */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-fuchsia-400" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                TRANSMISSION LINK
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-tech leading-relaxed">
              Need more downloaded RAM? Broke your ankles on Cybo lasers, got a cursed ZE map suggestion, or wanna flame our 420W toaster? Transmit your signal to Geronimo HQ via direct encrypted pigeon:
            </p>

            {/* Email Terminal Card */}
            <div className="p-3 bg-slate-900/90 border border-fuchsia-500/40 rounded-xl flex items-center justify-between gap-2 shadow-[0_0_20px_rgba(255,0,127,0.15)]">
              <div className="flex items-center gap-2 truncate">
                <span className="w-2 h-2 rounded-full bg-fuchsia-400" />
                <code className="text-fuchsia-300 font-code text-xs md:text-sm font-bold tracking-wide truncate">
                  {contactEmail}
                </code>
              </div>

              <div className="flex items-center gap-1.5 flex-shrink-0">
                {/* Copy Button */}
                <button
                  onClick={copyEmail}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded border border-slate-700 transition-colors cursor-pointer"
                  title="Copy email address"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
                </button>

                {/* Mailto Send Button */}
                <a
                  href={`mailto:${contactEmail}?subject=Inquiry%20from%20GeronimoHQ`}
                  className="px-2.5 py-1.5 bg-fuchsia-950/80 hover:bg-fuchsia-900 text-fuchsia-300 rounded text-xs font-code border border-fuchsia-500/50 flex items-center gap-1.5 transition-all shadow-[0_0_10px_rgba(255,0,127,0.3)]"
                >
                  <Send className="w-3 h-3" />
                  <span>MAIL</span>
                </a>
              </div>
            </div>

            <div className="text-[10px] font-code text-slate-400 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              Protected relay &bull; Direct inbox routing
            </div>
          </div>

          {/* Col 3: System Status & Quick Links */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-lime-400" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                CORE PROTOCOLS
              </h3>
            </div>

            <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2 text-xs font-code">
              <div className="flex justify-between py-0.5 border-b border-[#1E2E26]">
                <span className="text-slate-400">CS2 APP</span>
                <span className="text-emerald-400 font-bold">v1.4.0 // LIVE READY</span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#1E2E26]">
                <span className="text-slate-400">ZE CLUSTER</span>
                <span className="text-lime-300 font-bold">128 TICK // ACTIVE</span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#1E2E26]">
                <span className="text-slate-400">CLOUD RAM</span>
                <span className="text-cyan-300 font-bold">128 GB // DOWNLOADED</span>
              </div>
              <div className="flex justify-between py-0.5 border-b border-[#1E2E26]">
                <span className="text-slate-400">MEME CORE</span>
                <span className="text-yellow-400 font-bold">PEPE &amp; BANANA PHONE</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-400">RTX 6090 Ti</span>
                <span className="text-rose-400 font-bold">OVERCLOCKED // 420W</span>
              </div>
            </div>

            <div className="pt-1 flex items-center gap-4 text-xs font-code text-slate-400">
              <a href="#hero-stage" className="hover:text-cyan-400 transition-colors">
                &uarr; Back to Top
              </a>
              <span className="text-slate-700">&bull;</span>
              <a href="#cs2-command" className="hover:text-fuchsia-400 transition-colors">
                CS2 Portal
              </a>
              <span className="text-slate-700">&bull;</span>
              <a href="#server-radar" className="hover:text-lime-400 transition-colors">
                Server Radar
              </a>
            </div>
          </div>

        </div>

        {/* Bottom Clean Copyright Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-code text-slate-400">
          <div className="flex flex-col sm:flex-row items-center gap-2 text-center sm:text-left">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>GERONIMO HQ &copy; {new Date().getFullYear()} // ALL SYSTEMS NOMINAL</span>
            </div>
            <span className="hidden sm:inline text-slate-700">&bull;</span>
            <span className="text-[11px] text-slate-400">
              Zero RAM Refunds &bull; 100% Downloaded RAM Certified &bull; All Rights Reserved By The Meme Syndicate
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-slate-400">CYBERPUNK HUD</span>
            <span className="text-slate-300">PROD BUILD</span>
            <span className="text-cyan-400 font-bold">v1.1.0-LIVE</span>
          </div>
        </div>

      </div>
    </footer>
  );
};
