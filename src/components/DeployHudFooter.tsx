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
              To point your domain <strong className="text-cyan-300">geronimohq.com</strong> from Porkbun to GitHub Pages, use these records:
            </p>

            <div className="space-y-2 text-xs font-code">
              {/* Record 1: A Record */}
              <div className="p-3 bg-slate-900/90 border border-cyan-500/30 rounded-lg flex items-center justify-between">
                <div>
                  <div className="text-[10px] text-slate-500">ROOT DOMAIN (A RECORD)</div>
                  <div className="text-cyan-300 font-bold">@ &rarr; 185.199.108.153</div>
                </div>
                <button
                  onClick={() => copyToClipboard('185.199.108.153', 'a-record')}
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
                  <div className="text-fuchsia-300 font-bold">www &rarr; geronimohq.github.io</div>
                </div>
                <button
                  onClick={() => copyToClipboard('geronimohq.github.io', 'cname-record')}
                  className="px-2.5 py-1 bg-fuchsia-950/80 hover:bg-fuchsia-900 text-fuchsia-300 rounded text-[11px] border border-fuchsia-500/50 flex items-center gap-1 transition-colors cursor-pointer"
                >
                  <Copy className="w-3 h-3" />
                  {copiedType === 'cname-record' ? 'COPIED' : 'COPY'}
                </button>
              </div>
            </div>

            <div className="text-[11px] font-code text-slate-500 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Automated Free SSL / HTTPS certificate provided natively by GitHub Pages.
            </div>
          </div>

          {/* Col 2: Architecture & Deployment Status */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-fuchsia-400" />
              <h3 className="font-cyber font-bold text-white text-base tracking-wider">
                GITHUB PAGES CI/CD PIPELINE
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-tech leading-relaxed">
              Automated build & deploy workflow via GitHub Actions. Push code to main and it builds and deploys automatically.
            </p>

            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2 text-xs font-code">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">HOSTING</span>
                <span className="text-cyan-300 font-bold">GitHub Pages</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">CI/CD ENGINE</span>
                <span className="text-fuchsia-300 font-bold">GitHub Actions</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">FRAMEWORK</span>
                <span className="text-lime-300 font-bold">Vite 6 + React 19</span>
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
