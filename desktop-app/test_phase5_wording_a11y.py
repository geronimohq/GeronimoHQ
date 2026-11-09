"""AUDIT Phase 5 - wording matches the code, and basic accessibility guards. Source checks only."""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


# Parody components ("PARODY MEME", "Download RAM", Chaos button) are intentionally absurd.
FEATURE_FILES = [("desktop-app", "app.py"), ("desktop-app", "core_logic.py"), ("src", "App.tsx"),
                 ("src", "components", "CS2CommandCenterPreview.tsx"), ("src", "components", "CS2AutoexecGeneratorSection.tsx"),
                 ("src", "components", "ServerRadarPreview.tsx"), ("src", "components", "DeployHudFooter.tsx")]


class Wording(unittest.TestCase):
    def test_no_claims_about_features_that_do_not_exist(self):
        bad = [r"cl_interp 0\.015625", r"core affinity", r"Core Affinity", r"Vulkan backend selector",
               r"binds Jumpthrow", r"quick drop C4", r"\b1 Mbps", r"128[- ]TICK", r"Sub-Tick (Performance )?Tweaks",
               r"sub-tick network rates"]
        hits = []
        for p in FEATURE_FILES:
            for n, line in enumerate(read(*p).splitlines(), 1):
                for pat in bad:
                    if re.search(pat, line) and "AUDIT" not in line:
                        hits.append(f"{'/'.join(p)}:{n}: {line.strip()[:80]}")
        self.assertEqual(hits, [], "\n".join(hits))

    def test_app_does_not_write_what_it_no_longer_claims(self):
        src = read("desktop-app", "core_logic.py")
        for absent in ("cl_interp", "SetProcessAffinityMask"):
            self.assertNotIn(absent, src)


class ClaimsSweep(unittest.TestCase):
    """Superprompt Phase 5 word list: no unprovable '100% ...' claims left in UI text."""
    def test_no_hundred_percent_claims(self):
        pat = re.compile(r"100% (safe|healthy|read-only|automatic|passive|protected|intact|stable|reversible|"
                         r"pre-configured|transparent|valve safe|offline|system safety|cleared|preserved|non-invasive|verified)"
                         r"|never be banned|work 100%", re.I)
        hits = []
        for p in FEATURE_FILES + [("desktop-app", "server_browser.py"), ("desktop-app", "updater.py")]:
            for n, line in enumerate(read(*p).splitlines(), 1):
                if pat.search(line) and "AUDIT" not in line:
                    hits.append(f"{'/'.join(p)}:{n}: {line.strip()[:80]}")
        self.assertEqual(hits, [], "\n".join(hits))


class Accessibility(unittest.TestCase):
    def test_every_app_dialog_closes_with_escape(self):
        src = read("desktop-app", "app.py")
        dialogs = src.count("dlg = tk.Toplevel(self)")
        self.assertEqual(src.count("bind_escape_to_close(dlg)"), dialogs)

    def test_website_mobile_menu_closes_with_escape(self):
        self.assertIn("e.key === 'Escape'", read("src", "components", "CyberNavbar.tsx"))

    def test_desktop_labels_use_readable_muted_colour(self):
        src = read("desktop-app", "app.py")
        self.assertNotRegex(src, r'tk\.(Label|Button)\([^)]*fg="#(64748b|4b5563)"')

    def test_website_focus_and_skip_link(self):
        css = read("src", "index.css")
        self.assertIn(":focus-visible", css)
        self.assertIn(".skip-link:focus", css)
        app = read("src", "App.tsx")
        self.assertIn('href="#main-content"', app)
        self.assertIn('id="main-content"', app)

    def test_website_no_low_contrast_slate_text(self):
        for f in ("CS2CommandCenterPreview.tsx", "ServerRadarPreview.tsx", "ServerGeoDemographics.tsx",
                  "GeronimoDiscordPresence.tsx", "DownloadRamSection.tsx", "PepeHeroStage.tsx"):
            self.assertIsNone(re.search(r"\btext-slate-(500|600)\b", read("src", "components", f)), f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
