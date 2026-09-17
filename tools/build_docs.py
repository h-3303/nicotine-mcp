"""Generate docs/index.html (run from the repo root: python3 tools/build_docs.py) for nicotine-mcp from the Claude Design artboard
"Nicotine MCP Docs.dc.html" (project f45581b6-ceae-4ffc-a24b-6f544a05b33d).

Each <x-import> of the artboard is written out as the markup its Death to the
World component emits (see ~/dev/dttw/src/components); inline styles are kept
verbatim so the page stays diffable against the canvas."""
from html import escape as e
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/index.html"
SITE = "https://h-3303.github.io/nicotine-mcp/"
REPO = "https://github.com/h-3303/nicotine-mcp"

req = "required"
statuses = ("statuses: Queued · Getting status · Transferring · Paused · Cancelled · Filtered · Finished · "
            "User logged off · Connection closed · Connection timeout · Download folder error · Local file error")
search_filters = [("lossless_only", "bool", "false"), ("extensions", "list[str]", "—"),
                  ("min_bitrate", "int (kbps)", "—"), ("free_slot_only", "bool", "false")]
paging = [("max_folders", "int", "15"), ("files_per_folder", "int", "25")]

tools = [
    dict(name="nicotine_status", tag="READ-ONLY", rot=-0.6, params=[],
         doc="Connection state, logged-in username, download folder, download counts by status, tracked searches, and recent folder-download requests.",
         example="nicotine_status()"),
    dict(name="search", tag="READ-ONLY", rot=0.4,
         doc='Search Soulseek and return results grouped by (user, folder), best candidates first. Soulseek matches every word against the full file path; use artist + album words, avoid punctuation. Results keep arriving after this returns; call get_search_results later with the same search_id for more. mode="user" needs usernames; mode="rooms" needs room. Filters (lossless_only, extensions like ["flac"], min_bitrate in kbps for lossy files, free_slot_only) only affect what is returned, not what is collected.',
         params=[("query", "str", req), ("wait_seconds", "int", "12"), ("mode", "global | buddies | rooms | user", '"global"'),
                 ("usernames", "list[str]", "—"), ("room", "str", "—"), *search_filters, *paging],
         example='search(query="mingus ah um", lossless_only=true)'),
    dict(name="get_search_results", tag="READ-ONLY", rot=-0.4,
         doc="Re-read (and re-filter) an existing search. path_contains = space-separated words that must all appear in the path (case-insensitive); username restricts to one peer, handy for seeing a full folder.",
         params=[("search_id", "int", req), *search_filters, ("username", "str", "—"), ("path_contains", "str", "—"), *paging],
         example='get_search_results(search_id=41, username="vinylrip")'),
    dict(name="list_searches", tag="READ-ONLY", rot=0.5, params=[],
         doc="Searches currently tracked by the bridge (id, query, age, file/user counts). The oldest are dropped past the configured limit.",
         example="list_searches()"),
    dict(name="stop_search", tag="DESTRUCTIVE", rot=-0.5,
         doc="Stop collecting results for a search and discard them (also closes its tab in Nicotine+).",
         params=[("search_id", "int", req)], example="stop_search(search_id=41)"),
    dict(name="download_files", tag="WRITE", rot=0.6,
         doc="Queue specific files from a search by their result ids. With keep_folder_structure, files land in <download folder>/<remote parent folder name>/, which keeps album tracks together.",
         params=[("search_id", "int", req), ("result_ids", "list[int]", req), ("keep_folder_structure", "bool", "true")],
         example="download_files(search_id=41, result_ids=[3, 4, 5])"),
    dict(name="download_folder", tag="WRITE", rot=-0.7,
         doc="Queue an entire remote folder (e.g. an album) from a user. folder_path is the ‘folder’ value from search results. The peer is asked for the folder listing first, so files appear in list_downloads a few seconds later. include_subfolders also grabs e.g. CD1/CD2 or Scans subfolders.",
         params=[("username", "str", req), ("folder_path", "str", req), ("include_subfolders", "bool", "false")],
         example='download_folder(username="vinylrip", folder_path="Music\\\\Mingus Ah Um (1959) [FLAC]")'),
    dict(name="list_downloads", tag="READ-ONLY", rot=0.4,
         doc="List downloads with status, progress (0–1), speed and queue position, each with a download_id. Most recent last.",
         params=[("statuses", "list[status]", "—"), ("username", "str", "—"), ("limit", "int", "50")],
         note=statuses, example='list_downloads(statuses=["Transferring"])'),
    dict(name="cancel_downloads", tag="DESTRUCTIVE", rot=-0.4,
         doc="Cancel downloads by download_id (from list_downloads). Partial files stay in the incomplete folder.",
         params=[("download_ids", "list[str]", req)], example='cancel_downloads(download_ids=["9f2c01ab34de"])'),
    dict(name="retry_downloads", tag="WRITE", rot=0.5,
         doc="Retry failed, paused or cancelled downloads by download_id.",
         params=[("download_ids", "list[str]", req)], example='retry_downloads(download_ids=["9f2c01ab34de"])'),
    dict(name="clear_downloads", tag="DESTRUCTIVE", rot=-0.6,
         doc='Remove entries from the download list (does not delete finished files from disk). Give download_ids, statuses (e.g. ["Finished"]), or both — it refuses to clear everything.',
         params=[("download_ids", "list[str]", "—"), ("statuses", "list[status]", "—")],
         example='clear_downloads(statuses=["Finished"])'),
]

install_steps = [
    "copies plugin/mcp_bridge into ~/.local/share/nicotine/plugins/ (or the Flatpak data directory, if that’s your install);",
    "installs the server as ~/.local/bin/nicotine-mcp;",
    "pre-fetches its dependencies;",
    "runs claude mcp add --scope user nicotine -- uv run --script ~/.local/bin/nicotine-mcp.",
]
settings = [
    ("Socket path", "Leave empty for $XDG_RUNTIME_DIR/nicotine-mcp.sock. Flatpak installs automatically use $XDG_RUNTIME_DIR/app/org.nicotine_plus.Nicotine/nicotine-mcp.sock. If you set a custom path, export the same path as NICOTINE_MCP_SOCKET for the server, for example with claude mcp add --env NICOTINE_MCP_SOCKET=…"),
    ("Allow downloads", "Switch this off for search-only access."),
    ("Max results / max searches", "Max results per search and max searches kept are memory caps; the oldest searches are removed first."),
]
notes = [
    "Search results: they trickle in from peers for a minute or more. Call get_search_results again for a fuller picture.",
    "Folder downloads: these ask the peer for the folder listing first, so the files appear in list_downloads a few seconds later. Requests that get no answer are reported as timed out in nicotine_status after 3 minutes.",
    "Nicotine+ 3.3 large folders: for folders over 100 files, Nicotine+ also shows its own confirmation dialog. The bridge queues the files regardless, and duplicate queue entries are ignored.",
    "Headless use: nicotine --headless runs Nicotine+ without a GUI. Enable the plugin once from the GUI first, since the setting persists.",
    'Protocol: one JSON request per connection, of the form {"method": ..., "params": {...}}. See the HANDLERS table in the plugin to add methods.',
]
transcript = [
    ("→", 'search(query="mingus ah um", lossless_only=true)'),
    ("←", "214 files from 37 users · best folder: “vinylrip” — 12 files matched, flac 16bit 44.1kHz, free slot, queue 0"),
    ("→", 'download_folder(username="vinylrip", folder_path="Music\\\\Jazz\\\\Mingus Ah Um (1959) [FLAC]")'),
    ("←", "requested — files are queued once the user replies; check status or list_downloads"),
    ("→", 'list_downloads(statuses=["Transferring"])'),
    ("←", "12 downloads · 3 transferring at 1,240 kbps · 9 queued"),
]

TW = "font-family:var(--dtw-font-typewriter)"

def rot(deg):
    return f"transform:rotate({deg}deg)"

def bar_heading(text, deg, voice="serif"):
    return f'<div class="dtw-bar-heading dtw-bar-heading--{voice}" style="{rot(deg)}">{e(text)}</div>'

def body(text, size, italic=False):
    cls = "dtw-body dtw-body--italic" if italic else "dtw-body"
    return f'<div class="{cls}" style="font-size:{size}px;text-align:left">{e(text)}</div>'

def typewriter(text, size, muted=False, tracked=False, caps=False):
    cls = "dtw-typewriter" + (" dtw-typewriter--tracked" if tracked else "") + (" dtw-typewriter--caps" if caps else "") + (" dtw-typewriter--muted" if muted else "")
    return f'<div class="{cls}" style="font-size:{size}px">{e(text)}</div>'

def xlist(items, size):
    rows = "".join(f'\n        <div class="dtw-x-list__item" style="font-size:{size}px"><span class="dtw-x-list__x">X</span><span>{e(i)}</span></div>' for i in items)
    return f'<div class="dtw-x-list">{rows}\n      </div>'

DIAMOND = '<div style="margin-top:40px"><div class="dtw-ornament dtw-ornament--diamond"><div class="dtw-ornament__line"></div><div class="dtw-ornament__diamond"></div><div class="dtw-ornament__line"></div></div></div>'

def tool_box(t):
    grid = "display:grid;grid-template-columns:minmax(130px, 200px) 1fr minmax(64px, 100px);gap:0 12px"
    out = [f'<div class="dtw-pasted-box" style="{rot(t["rot"])}">',
           f'  <div id="{t["name"]}" style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">',
           f'    <span style="{TW};font-size:15px;letter-spacing:.06em">{t["name"]}</span>',
           f'    <span style="border:1px solid var(--dtw-ink);{TW};font-size:9px;letter-spacing:.16em;padding:3px 7px">{t["tag"]}</span>',
           '  </div>',
           f'  <div style="margin-top:12px">{body(t["doc"], 13.5)}</div>']
    if t["params"]:
        out.append(f'  <div style="margin-top:14px;{TW};font-size:11.5px">')
        out.append(f'    <div style="{grid};border-bottom:1px solid var(--dtw-ink);padding-bottom:4px;font-size:9px;letter-spacing:.14em;color:var(--dtw-label)"><span>PARAM</span><span>TYPE</span><span>DEFAULT</span></div>')
        for n, ty, d in t["params"]:
            out.append(f'    <div style="{grid};border-bottom:1px solid var(--dtw-grey-2);padding:5px 0"><span style="overflow-wrap:anywhere">{e(n)}</span><span style="overflow-wrap:anywhere">{e(ty)}</span><span>{e(d)}</span></div>')
        out.append('  </div>')
    if t.get("note"):
        out.append(f'  <div style="{TW};font-size:10px;color:var(--dtw-label);margin-top:10px;line-height:1.6">{e(t["note"])}</div>')
    out.append(f'  <div style="{TW};font-size:11px;color:var(--dtw-label);margin-top:12px;overflow-wrap:anywhere">e.g.&nbsp; {e(t["example"])}</div>')
    out.append('</div>')
    return "\n      ".join(out)

def arrow(text):
    return f'<span style="{TW};font-size:10px;letter-spacing:.08em;white-space:nowrap">{text}</span>'

description = ("An MCP server and Nicotine+ plugin that let Claude (Claude Code or Claude Desktop) drive your running "
               "Soulseek client: search, inspect results, queue files or whole folders, and manage downloads. "
               "Local Unix socket, no TCP listener, GPL-3.0.")

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>nicotine-mcp — Soulseek for Claude</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}">
<meta name="theme-color" content="#141412">
<meta name="keywords" content="MCP, Model Context Protocol, MCP server, Claude, Claude Code, Claude Desktop, Soulseek, Nicotine+, music, downloads, plugin">
<meta property="og:type" content="website">
<meta property="og:site_name" content="nicotine-mcp">
<meta property="og:title" content="nicotine-mcp — Soulseek for Claude">
<meta property="og:description" content="Search Soulseek. Queue albums. Manage downloads. An MCP server over a running Nicotine+ client, for Claude Code and Claude Desktop.">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="nicotine-mcp: Search Soulseek. Queue albums. Manage downloads.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="nicotine-mcp — Soulseek for Claude">
<meta name="twitter:description" content="Search Soulseek. Queue albums. Manage downloads. An MCP server over a running Nicotine+ client.">
<meta name="twitter:image" content="{SITE}og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23141412'/%3E%3Ctext x='16' y='24' text-anchor='middle' font-family='serif' font-weight='700' font-size='22' fill='%23e8e5dc'%3En%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="dtw.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "SoftwareSourceCode",
  "name": "nicotine-mcp",
  "description": "{e(description)}",
  "url": "{SITE}",
  "codeRepository": "{REPO}",
  "programmingLanguage": "Python",
  "runtimePlatform": "Nicotine+ 3.3+",
  "license": "https://www.gnu.org/licenses/gpl-3.0.html",
  "keywords": "MCP, Model Context Protocol, Claude, Soulseek, Nicotine+",
  "author": {{ "@type": "Person", "name": "h-3303", "url": "https://github.com/h-3303" }}
}}
</script>
<style>
  /* Page furniture only, copied from the artboard: the system's tokens and classes do the rest. */
  body {{ margin: 0; background: #141412; }}
  a {{ color: inherit; text-decoration: none; border-bottom: 1px solid #1a1a18; }}
  a:hover {{ background: #d9d4c6; }}
  .dtw-reversed-panel a {{ border-bottom-color: #e8e5dc; }}
  .dtw-reversed-panel a:hover {{ background: transparent; }}
  :target {{ scroll-margin-top: 24px; }}
  @media (max-width: 560px) {{
    .dtw-masthead__title {{ font-size: 32px !important; }}
    .arch > span {{ display: none; }}
    .arch > .node {{ display: inline-block; }}
  }}
</style>
</head>
<body>
<div style="width:min(880px, 94vw); margin:28px auto">
<div class="dtw-sheet dtw-sheet--paper dtw-xerox">
  <div style="padding:clamp(22px, 5vw, 52px)">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap">
      <span style="white-space:nowrap"><div class="dtw-masthead dtw-masthead--bar" style="{rot(-0.6)}"><div class="dtw-masthead__title" style="font-size:40px">nicotine-mcp</div><div class="dtw-masthead__tagline">SOULSEEK · FOR CLAUDE · GPL-3.0</div></div></span>
      <span style="white-space:nowrap"><span class="dtw-folio" style="{rot(-4)};font-size:18px">№ 01</span></span>
    </div>
    <div style="margin-top:34px">
      <h2 class="dtw-headline" style="font-size:27px;text-align:left">SEARCH SOULSEEK. QUEUE ALBUMS. MANAGE DOWNLOADS.</h2>
    </div>
    <div style="margin-top:14px">
      {body("Lets Claude (Claude Code, or Claude Desktop) drive a running Nicotine+ client: search Soulseek, inspect results, queue files or whole folders, and manage downloads.", 15)}
    </div>
    <div style="margin-top:12px">
      {typewriter("Tested against Nicotine+ 3.3.10, 3.3.11 and 3.4.0.dev2, with MCP Python SDK 2.x.", 11.5, muted=True)}
    </div>
    <nav style="display:flex; gap:18px; flex-wrap:wrap; margin-top:24px; {TW}; font-size:11px; letter-spacing:.16em; text-transform:uppercase">
      <a href="#install">Install</a><a href="#tools">Tools</a><a href="#settings">Settings</a><a href="#security">Security</a><a href="#notes">Notes</a><a href="#transcript">Transcript</a><a href="{REPO}">GitHub ↗</a>
    </nav>

    <div class="arch" style="display:flex; align-items:center; justify-content:center; gap:14px 12px; flex-wrap:wrap; margin-top:38px">
      <span class="node" style="white-space:nowrap">{bar_heading("CLAUDE CODE / DESKTOP", -0.8, "typewriter")}</span>
      {arrow("──stdio──▶")}
      <span class="node" style="white-space:nowrap"><div class="dtw-pasted-slip dtw-pasted-slip--typewriter" style="{rot(0.7)}">nicotine-mcp · uv script</div></span>
      {arrow("──unix socket──▶")}
      <span class="node" style="white-space:nowrap"><div class="dtw-pasted-slip dtw-pasted-slip--typewriter" style="{rot(-1.1)}">MCP Bridge plugin</div></span>
      <span class="node" style="display:inline-flex; align-items:center; gap:12px; white-space:nowrap">
        <span style="{TW}; font-size:10px; letter-spacing:.08em">──▶</span>
        {bar_heading("NICOTINE+ CORE", 0.6, "typewriter")}
      </span>
    </div>

    {DIAMOND}

    <div id="install" style="margin-top:40px">
      {bar_heading("INSTALL.", -0.5)}
      <div style="margin-top:20px">
        <div class="dtw-reversed-panel" style="{rot(0.4)}">
          <div style="{TW}; font-size:13px; line-height:1.7; white-space:pre-line">$ sudo pacman -S --needed nicotine+ uv
$ git clone {REPO} &amp;&amp; cd nicotine-mcp
$ ./install.sh</div>
        </div>
      </div>
      <div style="margin-top:20px">{body("The installer does four things:", 14.5)}</div>
      <div style="margin-top:14px">{xlist(install_steps, 13.5)}</div>
      <div style="margin-top:18px">{body("After that, open Nicotine+ → Preferences → Plugins, enable plugins, and tick MCP Bridge. The Nicotine+ log should show “MCP bridge listening on …”. Then claude mcp list should report nicotine as connected.", 14.5)}</div>
      <div style="margin-top:12px">{typewriter("For Claude Desktop or any other MCP client, register the command  uv run --script ~/.local/bin/nicotine-mcp  as a stdio server.", 11.5, muted=True)}</div>
    </div>

    {DIAMOND}

    <div id="tools" style="margin-top:40px">
      <div style="display:flex; align-items:baseline; gap:16px; flex-wrap:wrap">
        {bar_heading("THE TOOLS.", 0.4)}
        <span style="{TW}; font-size:10px; letter-spacing:.16em; color:var(--dtw-label)">ELEVEN · READ-ONLY / WRITE / DESTRUCTIVE</span>
      </div>
      <div style="display:flex; flex-direction:column; gap:30px; margin-top:28px">
      {chr(10).join("      " + tool_box(t) for t in tools)}
      </div>
    </div>

    {DIAMOND}

    <div id="settings" style="margin-top:40px">
      {bar_heading("PLUGIN SETTINGS.", -0.4)}
      <div style="margin-top:14px">{typewriter("Preferences → Plugins → MCP Bridge", 10, muted=True, tracked=True, caps=True)}</div>
      <div style="display:flex; flex-direction:column; gap:18px; margin-top:20px">
{chr(10).join(f'        <div style="display:grid; grid-template-columns:minmax(120px, 190px) 1fr; gap:14px"><span style="{TW}; font-size:11px; letter-spacing:.1em; text-transform:uppercase; padding-top:2px">{e(n)}</span>{body(d, 13.5)}</div>' for n, d in settings)}
      </div>
    </div>

    {DIAMOND}

    <div id="security" style="margin-top:40px">
      {bar_heading("SECURITY MODEL.", 0.5)}
      <div style="display:flex; gap:28px; align-items:flex-start; flex-wrap:wrap; margin-top:20px">
        <div style="flex:1 1 380px; display:flex; flex-direction:column; gap:14px">
          {body("Access control: the socket file is 0600, and the plugin also rejects any peer whose UID (from SO_PEERCRED) doesn’t match its own. There is no TCP listener, so browsers and other local users can’t reach it.", 14)}
          {body("Stability: all requests are run on Nicotine+’s main loop. Errors are caught before they reach Nicotine+’s event bus, because an uncaught exception in a main-thread callback makes Nicotine+ quit.", 14)}
        </div>
        <div style="white-space:nowrap; margin-top:6px">
          <div class="dtw-stamp" style="{rot(-3)}">0600 · SAME UID · NO TCP</div>
        </div>
      </div>
    </div>

    {DIAMOND}

    <div id="notes" style="margin-top:40px">
      {bar_heading("NOTES.", -0.6)}
      <div style="margin-top:20px">{xlist(notes, 13)}</div>
    </div>

    {DIAMOND}
    <div id="transcript" style="margin-top:40px">
      {bar_heading("A TRANSCRIPT.", 0.4)}
      <div style="margin-top:22px"><div class="dtw-hand" style="font-size:21.5px">find me Mingus — Ah Um, lossless if you can…</div></div>
      <div style="margin-top:18px">
        <div class="dtw-pasted-box" style="{rot(-0.5)}">
          <div style="display:flex; flex-direction:column; gap:9px; {TW}; font-size:11.5px; line-height:1.55">
{chr(10).join(f'            <div style="display:grid; grid-template-columns:20px 1fr; gap:8px"><span>{d}</span><span style="overflow-wrap:anywhere">{e(t)}</span></div>' for d, t in transcript)}
          </div>
        </div>
      </div>
      <div style="margin-top:16px">{body("“Queued the 1959 album in FLAC — twelve tracks on their way to your download folder. I’ll check list_downloads again in a minute.”", 14, italic=True)}</div>
    </div>

    <div style="margin-top:48px"><div class="dtw-ornament dtw-ornament--stars">{" ".join(["✦"] * 9)}</div></div>
    <div style="margin-top:18px; text-align:center; {TW}; font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:var(--dtw-label)">
      GPL-3.0 · <a href="{REPO}">github.com/h-3303/nicotine-mcp</a> · One socket · Pass it on
    </div>
  </div>
</div>
</div>
</body>
</html>
'''

with open(OUT, "w") as f:
    f.write(html)
print(OUT, len(html), "bytes")
