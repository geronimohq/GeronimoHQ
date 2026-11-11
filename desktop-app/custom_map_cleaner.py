"""
CS2 Zombie Escape & Custom Map Cleaner
Scans community workshop content and downloaded .vpk maps, calculates storage,
and safely purges selected unused maps to reclaim gigabytes of SSD space without
ever touching official Valve competitive maps.
"""

import os
import glob
import re
import shutil
import datetime
from typing import List, Dict, Any, Tuple, Set
from collections import Counter

# Official Valve CS2 maps that must NEVER be deleted
OFFICIAL_MAPS = {
    "ar_baggage", "ar_baggage_vanity", "ar_pool_day", "ar_shoots", "ar_shoots_night",
    "cs_italy", "cs_italy_vanity", "cs_office", "cs_office_vanity", "cs_shelter",
    "de_ancient", "de_ancient_night", "de_ancient_night_vanity", "de_ancient_vanity",
    "de_anubis", "de_anubis_vanity", "de_boulder", "de_cache", "de_cache_vanity",
    "de_debris", "de_dust2", "de_dust2_vanity", "de_eldorado", "de_fachwerk",
    "de_inferno", "de_inferno_vanity", "de_mirage", "de_mirage_vanity",
    "de_nuke", "de_nuke_vanity", "de_overpass", "de_overpass_vanity",
    "de_train", "de_vertigo", "de_vertigo_vanity",
    "workshop_preview_inferno", "workshop_preview_ancient", "workshop_preview_dust2",
    "lobby_mapveto", "warehouse_vanity", "de_train_vanity", "graphics_settings", "de_poseidon"
}

# Known community server asset / content packs that must NEVER be deleted
# (Prevents giant red ERROR models, missing textures, and missing player skins)
KNOWN_SERVER_ASSETS = {
    "3793587501": "GFL Clan ZE - Server Assets & Content Pack",
    "3160448201": "GFL Clan ZE - Content Pack",
    "3535955403": "Possession ZE (PSE) - General Contents Pack (Tokyo)",
    "3157469866": "Mapeadores ZE - Asset Pack (EU)",
    "3304608958": "cOLa-TeaM ZE - Asset Pack Part 1 (EU)",
    "3333820862": "cOLa-TeaM ZE - Server Content Pack Part 2 (EU)",
}

# Community Server Pack & Rotation Definitions
COMMUNITY_SERVER_ROSTERS = {
    "gfl": {
        "id": "gfl",
        "name": "GFL Clan ZE (NA)",
        "badge": "⭐ Subscribed (GFL Server Pack)",
        "keywords": ["gfl", "gflclan", "gfl clan"],
        "asset_ids": {"3793587501", "3160448201"},
        "signature_maps": {
            "ze_lotr_helms_deep_p", "ze_deadcore_s7", "ze_dark_souls_ptd_v0_4",
            "ze_shroomforest3_p", "ze_pirates_port_royal_v5_6", "ze_paramount",
            "ze_tilex_escape_v2_1", "ze_ffvii_mako_reactor_v5_3", "ze_ffxii_westersand_v8zeta1",
            "ze_slender_escape_p", "ze_resident_evil_3", "ze_predator_ultimate_p"
        }
    },
    "possession": {
        "id": "possession",
        "name": "Possession ZE (PSE Tokyo)",
        "badge": "🛡️ Possession Rotation (PROTECTED)",
        "keywords": ["possession", "pse", "possession-jp"],
        "asset_ids": {"3535955403", "3075687337", "3076940469", "3103181471"},
        "signature_maps": {
            "ze_colorlicouspilar_p", "ze_colorlicouspilar", "ze_colors_p", "ze_biohazard2_sewer_v4c", "ze_boatescape",
            "ze_frostdrake", "ze_sandstorm_cs2", "ze_predator_ultimate_p",
            "ze_fapescape_p", "ze_gris_f1", "ze_escape_horizon", "ze_slender_escape_p",
            "ze_surf_danger", "ze_castlevania_64", "ze_forsaken_temple"
        }
    },
    "rss": {
        "id": "rss",
        "name": "RSS Zombie Escape (EU/Global)",
        "badge": "🛡️ RSS Rotation (PROTECTED)",
        "keywords": ["rss", "revenant", "rss-ze"],
        "asset_ids": {"3716633440"},
        "signature_maps": {
            "ze_obff_npst_v24", "ze_santassination_v3", "ze_lila_panic_escape_v2",
            "ze_serpentis_temple_cs2", "ze_ffvii_mako_reactor_v6", "ze_potc_p",
            "ze_stalker_ultimate_v2_3", "ze_gris_f1", "ze_elevator_escape_p"
        }
    },
    "mapeadores_cola": {
        "id": "mapeadores_cola",
        "name": "Mapeadores & cOLa (EU)",
        "badge": "🛡️ Mapeadores/cOLa (PROTECTED)",
        "keywords": ["mapeadores", "cola", "cola-team"],
        "asset_ids": {"3157469866", "3304608958", "3333820862"},
        "signature_maps": {
            "ze_castlevania_64", "ze_ancient_wrath_v2", "ze_voodoo_islands_p"
        }
    },
    "net4all": {
        "id": "net4all",
        "name": "Net4All ZE (Russia)",
        "badge": "🛡️ Net4All Rotation (PROTECTED)",
        "keywords": ["net4all"],
        "asset_ids": set(),
        "signature_maps": set()
    },
    "exg": {
        "id": "exg",
        "name": "EXG Community (China)",
        "badge": "🛡️ EXG Community (PROTECTED)",
        "keywords": ["exg", "93x", "fys", "ub"],
        "asset_ids": set(),
        "signature_maps": {
            "ze_pkmn_adventure_v9_3", "ze_minimal_cs2", "ze_sky_athletic_adv_v2"
        }
    }
}

def identify_community_for_map(clean_name: str, workshop_id: str, title: str = "") -> Tuple[str, str]:
    """
    Identifies which community server pack / rotation a map belongs to.
    Returns: (community_key, community_badge) or ("", "")
    """
    clean_low = clean_name.lower().strip()
    title_low = title.lower().strip()

    for key, comm in COMMUNITY_SERVER_ROSTERS.items():
        if workshop_id in comm["asset_ids"]:
            return key, comm["badge"]
        if key == "gfl":
            continue            # GFL re-uploads every map it runs: only the ids in GFL's own collection make a map GFL's (a same-named map is another item)
        if clean_low in comm["signature_maps"]:
            return key, comm["badge"]
        if any(k in title_low for k in comm["keywords"]):
            return key, comm["badge"]

    return "", ""

MAP_PREFIXES = ("ze_", "zm_", "de_", "cs_", "ar_", "surf_", "bhop_", "mg_", "jb_")

def is_asset_pack_or_custom(folder: str, workshop_id: str, title: str = "") -> Tuple[bool, str, bool]:
    """
    Checks if a workshop directory contains a Server Asset Pack (models, skins, sounds).
    Ensures playable custom maps (ze_, surf_, etc.) where users perform modifications are never falsely locked.
    Returns: (is_asset_pack, descriptive_name, is_custom_modified)
    """
    # 0. If title starts with a map prefix (ze_, zm_, surf_, etc.), it is a MAP, not an asset pack!
    tl = title.lower().strip()
    if any(tl.startswith(p) for p in MAP_PREFIXES):
        return False, "", False

    # 1. Known Server Asset ID (e.g. GFL, Possession PSE, Mapeadores, cOLa-TeaM)
    if workshop_id in KNOWN_SERVER_ASSETS:
        name = KNOWN_SERVER_ASSETS[workshop_id]
        return True, name, False

    # 1b. Anything in the servers' asset collections (models, sounds and skins the servers need), by exact id
    try:
        import workshop_collections
        if workshop_id in workshop_collections.asset_ids():
            return True, workshop_collections.asset_title(workshop_id) or f"Server Asset Pack (#{workshop_id})", False
    except Exception:
        pass

    # 2. Check title keywords to identify server communities
    if any(k in tl for k in ["server asset", "content pack", "server pack", "model pack", "asset pack", "general contents", "playermodels"]):
        if "pse" in tl or "possession" in tl:
            name = "Possession ZE (PSE) - Content Pack (Tokyo)"
        elif "cola" in tl:
            name = "cOLa-TeaM ZE - Asset Pack (EU)"
        elif "mapea" in tl:
            name = "Mapeadores ZE - Asset Pack (EU)"
        elif "rss" in tl:
            name = "RSS Zombie Escape - Content Pack"
        elif "gfl" in tl:
            name = "GFL Clan ZE - Content Pack"
        elif "playermodel" in tl:
            name = "Community Server Player Models Pack"
        else:
            name = f"Server Asset Pack ({title})"
        return True, name, False

    # 3. Binary inspection of VPKs: contains models/materials/sounds, but NO maps or world geometry
    try:
        vpks = [f for f in os.listdir(folder) if f.endswith(".vpk")]
        has_models_or_materials = False
        has_maps = False
        sample_chunk = b""
        for v in vpks:
            vp = os.path.join(folder, v)
            if os.path.getsize(vp) < 1000:
                continue
            with open(vp, "rb") as f:
                chunk = f.read(512 * 1024)
                sample_chunk += chunk[:4096]
                if b"models/" in chunk or b"materials/" in chunk or b"particles/" in chunk or b"sounds/" in chunk:
                    has_models_or_materials = True
                if b"maps/" in chunk or b".vmap" in chunk or b"world.vwrld" in chunk:
                    has_maps = True
        
        if has_models_or_materials and not has_maps:
            chunk_l = sample_chunk.lower()
            if b"possession" in chunk_l or b"pse" in chunk_l:
                name = "Possession ZE (PSE) - Content Pack (Tokyo)"
            elif b"cola" in chunk_l:
                name = "cOLa-TeaM ZE - Asset Pack (EU)"
            elif b"mapeadores" in chunk_l:
                name = "Mapeadores ZE - Asset Pack (EU)"
            elif b"rss" in chunk_l:
                name = "RSS Zombie Escape - Content Pack"
            elif b"gfl" in chunk_l:
                name = "GFL Clan ZE - Content Pack"
            else:
                name = f"Server Asset Pack (#{workshop_id})"
            return True, name, False
    except Exception:
        pass

    return False, "", False

def get_subscribed_workshop_ids(library_folders: List[str]) -> Set[str]:
    """
    Parses appworkshop_730.acf across all Steam library folders to identify
    every workshop item the player is officially subscribed to (e.g. via Server Map Collections like GFL ZE).
    """
    subscribed_ids = set()
    for lib in library_folders:
        acf_path = os.path.join(lib, "steamapps", "workshop", "appworkshop_730.acf")
        if os.path.exists(acf_path):
            try:
                with open(acf_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Parse WorkshopItemDetails blocks with subscribedby
                for match in re.finditer(r'"(\d{8,12})"\s*\{([^}]+)\}', content):
                    item_id = match.group(1)
                    props = match.group(2)
                    if "subscribedby" in props:
                        subscribed_ids.add(item_id)
            except Exception:
                pass
    return subscribed_ids

def scan_custom_maps(steam_path: str, cs2_dir: str = None, protected_communities: Set[str] = None, protect_recent: bool = True) -> List[Dict[str, Any]]:
    """
    Scans workshop directory (steamapps/workshop/content/730) and game/csgo/maps
    for custom downloaded community maps.
    Identifies whether each map is part of a Subscribed Server Collection, Protected Community Roster, or Temporary Download.
    Returns a sorted list of map objects with human-readable titles, file sizes, and dates.
    """
    import time
    now_ts = time.time()
    if protected_communities is None:
        protected_communities = {"gfl", "possession", "rss", "mapeadores_cola", "exg"}

    maps_list = []
    seen_ids = set()

    # 1. Search Steam Workshop content (AppID 730 = CS2)
    # Search all Steam library folders
    import steam_paths
    library_folders = steam_paths.steam_libraries(steam_path)
    cs2_lib = steam_paths.library_of(cs2_dir)
    if cs2_lib and os.path.normcase(os.path.abspath(cs2_lib)) not in {os.path.normcase(os.path.abspath(l)) for l in library_folders}:
        library_folders.append(cs2_lib)

    subscribed_ids = get_subscribed_workshop_ids(library_folders)

    for lib in library_folders:
        workshop_dir = os.path.join(lib, "steamapps", "workshop", "content", "730")
        if not os.path.exists(workshop_dir):
            continue

        for folder in glob.glob(os.path.join(workshop_dir, "*")):
            if not os.path.isdir(folder):
                continue
            workshop_id = os.path.basename(folder)
            if workshop_id in seen_ids:
                continue
            seen_ids.add(workshop_id)

            # Read human readable title from publish_data.txt if present
            title = f"Workshop Item #{workshop_id}"
            pub_file = os.path.join(folder, "publish_data.txt")
            if os.path.exists(pub_file):
                try:
                    with open(pub_file, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                        m = re.search(r'"title"\s+"([^"]+)"', c)
                        if m:
                            title = m.group(1)
                except Exception:
                    pass

            # Calculate total directory size and latest modified time
            total_sz = 0
            latest_mtime = 0
            for root, dirs, files in os.walk(folder):
                for fl in files:
                    fp = os.path.join(root, fl)
                    try:
                        st = os.stat(fp)
                        total_sz += st.st_size
                        if st.st_mtime > latest_mtime:
                            latest_mtime = st.st_mtime
                    except Exception:
                        pass

            if total_sz == 0:
                continue

            mtime_str = datetime.datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M") if latest_mtime > 0 else "Unknown"
            
            # Format size
            if total_sz >= 1024 ** 3:
                size_str = f"{total_sz / (1024 ** 3):.2f} GB"
            else:
                size_str = f"{total_sz / (1024 ** 2):.1f} MB"

            # Check if this workshop folder is a Server Asset Pack or custom user VPK
            is_asset, asset_name, is_custom = is_asset_pack_or_custom(folder, workshop_id, title)
            is_official_gfl = (workshop_id in subscribed_ids)      # defined for every folder, not only for maps
            if is_asset:
                title = asset_name
                map_type = "Custom Asset VPK" if is_custom else "Server Asset Pack"
                status_label = "🎨 Custom Modified VPK (PROTECTED)" if is_custom else "🛡️ Server Asset Pack (PROTECTED)"
                status_type = "server_asset"
                is_sub = True  # treat as protected
                is_protected = True
                comm_key = ""
            else:
                map_type = "Workshop Map"
                # Check if map matches any protected community roster (Possession, RSS, GFL, Mapeadores, EXG)
                comm_key, comm_badge = identify_community_for_map(title, workshop_id, title)
                if not comm_key:
                    try:
                        for vf in os.listdir(folder):
                            if vf.endswith(".vpk"):
                                k, b = identify_community_for_map(vf.replace(".vpk", ""), workshop_id, title)
                                if k:
                                    comm_key, comm_badge = k, b
                                    break
                    except Exception:
                        pass

                member_keys: List[str] = []
                try:
                    import workshop_collections
                    member_keys = workshop_collections.communities_of(workshop_id)
                except Exception:
                    pass
                if member_keys:                                   # exact: this id is in the server's own collection
                    comm_key = next((k for k in member_keys if k in protected_communities), member_keys[0])
                    comm_badge = COMMUNITY_SERVER_ROSTERS.get(comm_key, {}).get("badge", comm_badge)
                is_official_gfl = (workshop_id in subscribed_ids)
                if is_official_gfl:
                    owner = comm_key if member_keys else "gfl"
                    pretty = COMMUNITY_SERVER_ROSTERS.get(owner, {}).get("name", "GFL Server Pack")
                    comm_key = owner
                    is_sub = (owner in protected_communities)
                    status_label = f"⭐ Subscribed ({pretty})" if is_sub else f"📁 {pretty} (Protection Disabled)"
                    status_type = "subscribed" if is_sub else "temp"
                    is_protected = is_sub
                elif comm_key and comm_key in protected_communities:
                    is_sub = True
                    status_label = comm_badge
                    status_type = "community_protected"
                    is_protected = True
                elif protect_recent and latest_mtime > 0 and (now_ts - latest_mtime <= 14 * 86400):
                    is_sub = True
                    status_label = "🕒 Active Rotation (Last 14d)"
                    status_type = "recent_rotation"
                    is_protected = True
                else:
                    is_sub = False
                    status_label = "📁 Temp Download (Safe Clean)"
                    status_type = "temp"
                    is_protected = False

            maps_list.append({
                "id": workshop_id,
                "name": title,
                "type": map_type,
                "status_label": status_label,
                "status_type": status_type,
                "community_key": comm_key,
                "is_subscribed": is_sub,
                "is_officially_subscribed": is_official_gfl,
                "is_server_asset": is_asset,
                "is_custom_modified": is_custom,
                "is_protected": is_protected,
                "path": folder,
                "size_bytes": total_sz,
                "size_mb": total_sz / (1024 * 1024),
                "size_str": size_str,
                "mtime": latest_mtime,
                "mtime_str": mtime_str,
                "is_workshop": True
            })

    # 2. Check game/csgo/maps folder for non-official custom .vpk files
    if cs2_dir:
        csgo_maps = os.path.join(cs2_dir, "game", "csgo", "maps")
        if os.path.exists(csgo_maps):
            for vpk_path in glob.glob(os.path.join(csgo_maps, "*.vpk")):
                fname = os.path.basename(vpk_path)
                base_name = fname.replace(".vpk", "").lower()

                # NEVER include official Valve maps
                if base_name in OFFICIAL_MAPS:
                    continue

                try:
                    st = os.stat(vpk_path)
                    sz = st.st_size
                    mtime_str = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                    if sz >= 1024 ** 3:
                        size_str = f"{sz / (1024 ** 3):.2f} GB"
                    else:
                        size_str = f"{sz / (1024 ** 2):.1f} MB"

                    comm_key, comm_badge = identify_community_for_map(base_name, "", base_name)
                    if comm_key and comm_key in protected_communities:
                        is_sub = True
                        status_label = comm_badge
                        status_type = "community_protected"
                        is_protected = True
                    elif protect_recent and (now_ts - st.st_mtime <= 14 * 86400):
                        is_sub = True
                        status_label = "🕒 Active Rotation (Last 14d)"
                        status_type = "recent_rotation"
                        is_protected = True
                    else:
                        is_sub = False
                        status_label = "📦 Custom Map (.vpk)"
                        status_type = "vpk"
                        is_protected = False

                    maps_list.append({
                        "id": fname,
                        "name": fname.replace(".vpk", ""),
                        "type": "Custom .vpk",
                        "status_label": status_label,
                        "status_type": status_type,
                        "community_key": comm_key,
                        "is_subscribed": is_sub,
                        "is_protected": is_protected,
                        "path": vpk_path,
                        "size_bytes": sz,
                        "size_mb": sz / (1024 * 1024),
                        "size_str": size_str,
                        "mtime": st.st_mtime,
                        "mtime_str": mtime_str,
                        "is_workshop": False
                    })
                except Exception:
                    pass

    # Flag duplicate map names across entries (excluding protected server asset packs)
    name_counts = Counter(m["name"].lower().strip() for m in maps_list if not m.get("is_server_asset"))
    for m in maps_list:
        if m.get("is_server_asset") or m.get("is_protected"):
            m["has_duplicate"] = False
        else:
            clean_name = m["name"].lower().strip()
            m["has_duplicate"] = (name_counts[clean_name] > 1)

    # Sort largest to smallest by default
    maps_list.sort(key=lambda x: x["size_bytes"], reverse=True)
    return maps_list

def _is_link_or_junction(p: str) -> bool:
    """True for symlinks and Windows junctions / reparse points."""
    try:
        if os.path.islink(p):
            return True
        st = os.lstat(p)
        return bool(getattr(st, "st_file_attributes", 0) & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    except OSError:
        return True


def is_deletable_map_path(p: str) -> bool:
    """AUDIT 1c-D3: only two shapes of path may ever be deleted:
       <library>/steamapps/workshop/content/730/<digits>      (a Workshop item folder)
       <cs2>/game/csgo/maps/<name>.vpk                         (a loose custom map file)
    The path itself and its parent must not be a symlink/junction, and the real
    path must still have that shape (no '..' tricks)."""
    if not p or not isinstance(p, str):
        return False
    if _is_link_or_junction(p) or _is_link_or_junction(os.path.dirname(os.path.abspath(p))):
        return False
    real = os.path.realpath(p)
    if os.path.normcase(real) != os.path.normcase(os.path.abspath(p)):
        return False
    parts = [x.lower() for x in real.replace("\\", "/").split("/") if x]
    if len(parts) >= 5 and parts[-5:-1] == ["steamapps", "workshop", "content", "730"] and parts[-1].isdigit():
        return os.path.isdir(real)
    if len(parts) >= 4 and parts[-4:-1] == ["game", "csgo", "maps"] and parts[-1].endswith(".vpk"):
        return os.path.isfile(real)
    return False


def delete_custom_maps(map_items: List[Dict[str, Any]], allow_assets: bool = False) -> Tuple[int, int, List[str]]:
    """
    Safely deletes selected custom map folders or .vpk files.
    Returns (deleted_count, freed_bytes, logs).
    """
    deleted_count = 0
    freed_bytes = 0
    logs = []

    for item in map_items:
        p = item.get("path")
        if not p or not os.path.exists(p):
            continue

        # Extra safety check: NEVER delete official map names or server asset packs
        base_name = os.path.basename(p).lower().replace(".vpk", "")
        if base_name in OFFICIAL_MAPS:
            logs.append(f"[SKIPPED] Protected official map: {base_name}")
            continue

        wid = item.get("id", "")
        name = item.get("name", os.path.basename(p))

        asset_ok = allow_assets and item.get("is_server_asset")          # the user explicitly chose to delete this server asset pack
        if not asset_ok and (item.get("is_server_asset") or item.get("is_protected") or wid in KNOWN_SERVER_ASSETS):
            logs.append(f"[BLOCKED] Refused deletion of protected Server Asset Pack / Community Map: {name} (#{wid})")
            continue

        if not is_deletable_map_path(p):
            logs.append(f"[BLOCKED] Refused deletion outside the Workshop/maps folders or through a link: {name}")
            continue

        sz = item.get("size_bytes", 0)
        name = item.get("name", os.path.basename(p))
        wid = item.get("id", "")
        is_sub = item.get("is_subscribed", False)
        sub_tag = " [SERVER ASSET PACK]" if asset_ok else " [SUBSCRIBED SERVER PACK]" if is_sub else " [TEMP]"

        try:
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=False)
            else:
                os.remove(p)
            if not os.path.exists(p):
                deleted_count += 1
                freed_bytes += sz
                size_display = item.get("size_str") or (f"{sz / (1024*1024):.1f} MB" if sz >= 1048576 else f"{sz / 1024:.1f} KB" if sz >= 1024 else f"{sz} B")
                logs.append(f"[CLEANED]{sub_tag} Deleted map: {name} (#{wid}) ({size_display})")
            else:
                logs.append(f"[LOCKED/SKIPPED] Incomplete deletion for {name} (#{wid}): some files remain locked")
        except (OSError, PermissionError) as e:
            logs.append(f"[LOCKED/SKIPPED] Could not delete {name} (#{wid}): {e}")
        except Exception as e:
            logs.append(f"[ERROR] Unexpected error deleting {name} (#{wid}): {e}")

    return deleted_count, freed_bytes, logs
