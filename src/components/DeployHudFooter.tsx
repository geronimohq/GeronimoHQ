import React, { useState } from 'react';
import { Globe, Server, CheckCircle2, Copy, ExternalLink } from 'lucide-react';

export const DeployHudFooter: React.FC = () => {
  const [copiedType, setCopiedType] = useState<string | null>(null);

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopiedType(type);
    setTimeout(() => setCopiedType(null), 2000);
  };

  return (
    <footer id="deploy-info" className="relative w-full border-t border-cyan-500/20 bg-[#04060b]/95 backdrop-blur-xl pt-12 pb-8 px-4 mt-16 z-10">
      <div className="max-w-6xl mx-auto">
        
        {/* Top Grid: Porkbun DNS & Deployment Specs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10 pb-8 border-b border-slate-800">
          
          {/* Col 1: Porkbun DNS Configuration Guide */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-cyan-400" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                PORKBUN DNS CONFIGURATION // GERONIMOHQ.COM
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-tech leading-relaxed">
              To point your domain <strong className="text-cyan-300">geronimohq.com</strong> from Porkbun to Vercel or Cloudflare Pages, add these records in your Porkbun Domain Management panel:
            </p>

            <div className="space-y-2 text-xs font-code">
              {/* Record 1: A Record */}
              <div className="p-3 bg-slate-900/90 border border-cyan-500/30 rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-[10px] text-slate-500">ROOT DOMAIN (A RECORD)</div>
                  <div className="text-cyan-300 font-bold">@ &rarr; 76.76.21.21</div>
                </div>
                <button
                  onClick={() => copyToClipboard('76.76.21.21', 'a-record')}
                  className="px-2.5 py-1 bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 rounded text-[11px] border border-cyan-500/50 flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <Copy className="w-3 h-3" />
                  {copiedType === 'a-record' ? 'COPIED' : 'COPY'}
                </button>
              </div>

              {/* Record 2: CNAME Record */}
              <div className="p-3 bg-slate-900/90 border border-fuchsia-500/30 rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-[10px] text-slate-500">SUBDOMAIN (CNAME RECORD)</div>
                  <div className="text-fuchsia-300 font-bold">www &rarr; cname.vercel-dns.com</div>
                </div>
                <button
                  onClick={() => copyToClipboard('cname.vercel-dns.com', 'cname-record')}
                  className="px-2.5 py-1 bg-fuchsia-950/80 hover:bg-fuchsia-900 text-fuchsia-300 rounded text-[11px] border border-fuchsia-500/50 flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <Copy className="w-3 h-3" />
                  {copiedType === 'cname-record' ? 'COPIED' : 'COPY'}
                </button>
              </div>
            </div>

            <div className="text-[11px] font-code text-slate-500 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Automated Free SSL / Let's Encrypt certificate will issue within ~5 mins of propagation.
            </div>
          </div>

          {/* Col 2: Architecture & Deployment Status */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-fuchsia-400" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                PRODUCTION BUILD PIPELINE
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-tech leading-relaxed">
              Optimized Vite React bundle with zero-config static hosting ready for Vercel, Netlify, or Cloudflare Pages.
            </p>

            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2 text-xs font-code">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">FRAMEWORK</span>
                <span className="text-cyan-300 font-bold">Vite 6 + React 19 + Tailwind v4</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">OUTPUT DIRECTORY</span>
                <span className="text-fuchsia-300 font-bold">dist/</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">BUILD COMMAND</span>
                <span className="text-lime-300 font-bold">npm run build</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">TARGET DOMAIN</span>
                <span className="text-white font-bold">geronimohq.com</span>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-1">
              <a
                href="https://porkbun.com"
                target="_blank"
                rel="noreferrer"
                className="text-xs font-code text-cyan-400 hover:text-cyan-300 flex items-center gap-1 hover:underline"
              >
                Open Porkbun Control Panel <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

        </div>

        {/* Bottom Credits & Terminal Branding */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-code text-slate-500">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>GERONIMO HQ &copy; {new Date().getFullYear()} // ALL SYSTEMS NOMINAL</span>
          </div>
          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-slate-400">DESIGN: RETRO-CYBERPUNK HUD</span>
            <span>MEMES: PEPE TRIPTYCH</span>
            <span className="text-cyan-400">v1.0.0-PROD</span>
          </div>
        </div>

      </div>
    </footer>
  );
};
