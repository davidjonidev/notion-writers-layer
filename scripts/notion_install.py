#!/usr/bin/env python3
"""
Ultimate Writer Planner — Notion API auto-installer.

Builds the ENTIRE template directly inside a Notion account: every database
with correct property types, cross-database relations to Book Projects, the
"smart" formulas (words remaining, % complete, auto daily word goal), and all
the seed rows fully linked. Also creates the four text pages (Dashboard,
How-to, Story Structure, Daily Ritual) from the Markdown sources.

This does what the Markdown/CSV import CANNOT: live relations, formulas and
typed properties — not just plain-text columns.

-------------------------------------------------------------------------------
SETUP (one time, ~3 minutes)
-------------------------------------------------------------------------------
1. Go to https://www.notion.so/my-integrations  ->  "New integration".
   - Name it "Writer Planner Installer", pick her workspace, submit.
   - Copy the "Internal Integration Secret" (starts with `ntn_` or `secret_`).
2. In Notion, create (or pick) an EMPTY page that will hold the planner.
   Open it -> top-right "..." menu -> "Connections" -> add your integration.
   (This is what grants the script permission to write into that page.)
3. Copy that page's URL (the "Copy link" button works).

-------------------------------------------------------------------------------
RUN
-------------------------------------------------------------------------------
    export NOTION_TOKEN="ntn_xxx"
    python3 scripts/notion_install.py --parent "<paste the page URL>"

  Or pass the token inline:
    python3 scripts/notion_install.py --token ntn_xxx --parent "<page URL>"

  Preview without touching Notion (validates the data + schema):
    python3 scripts/notion_install.py --dry-run

No third-party packages required — standard library only.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "template"
)
PLANNER_SUBDIR = os.path.join(TEMPLATE_DIR, "Ultimate Writer Planner")
RATE_LIMIT_SLEEP = 0.34  # ~3 requests/sec, Notion's documented limit


# ---------------------------------------------------------------------------
# Database schemas. Order matters: "📚 Book Projects" must be first so its id
# is available for every relation that points back to it.
# Column types default to rich_text unless listed in "types".
# ---------------------------------------------------------------------------
SCHEMAS = [
    {
        "name": "📚 Book Projects",
        "csv": "📚 Book Projects.csv",
        "title": "Title",
        "types": {
            "Status": "select", "Genre": "select", "Format": "select",
            "Target Word Count": "number", "Current Word Count": "number",
            "Deadline": "date", "Logline": "rich_text", "Notes": "rich_text",
        },
        "formulas": {
            "Words Remaining":
                'prop("Target Word Count") - prop("Current Word Count")',
            "% Complete":
                'if(prop("Target Word Count") == 0, 0, '
                'prop("Current Word Count") / prop("Target Word Count"))',
            "Daily Word Goal":
                'if(empty(prop("Deadline")), 0, round('
                '(prop("Target Word Count") - prop("Current Word Count")) / '
                'max(dateBetween(prop("Deadline"), now(), "days"), 1)))',
            "Health":
                'if(prop("Target Word Count") == 0, "—", '
                'if(prop("Current Word Count") >= prop("Target Word Count"), '
                '"✅ Done", if(prop("Current Word Count") / '
                'prop("Target Word Count") > 0.5, "🟢 On track", '
                '"🟡 Keep going")))',
        },
    },
    {
        "name": "📕 Series & Saga",
        "csv": "📕 Series & Saga.csv",
        "title": "Series",
        "types": {
            "Book in Series": "relation", "Reading Order": "number",
            "Status": "select", "Planned Books": "number",
        },
    },
    {
        "name": "📖 Chapters & Scenes",
        "csv": "📖 Chapters & Scenes.csv",
        "title": "Title",
        "types": {
            "Book": "relation", "Order": "number", "Status": "select",
            "Word Count": "number",
        },
    },
    {
        "name": "🧵 Plot & Beats",
        "csv": "🧵 Plot & Beats.csv",
        "title": "Beat",
        "types": {
            "Book": "relation", "Act": "select", "Order": "number",
            "Status": "select", "Tension (1-10)": "number",
        },
    },
    {
        "name": "👤 Characters",
        "csv": "👤 Characters.csv",
        "title": "Name",
        "types": {
            "Book": "relation", "Role": "select", "Status": "select",
            "Age": "number",
        },
    },
    {
        "name": "🌍 World Building",
        "csv": "🌍 World Building.csv",
        "title": "Name",
        "types": {"Book": "relation", "Type": "select"},
    },
    {
        "name": "🔬 Research & Notes",
        "csv": "🔬 Research & Notes.csv",
        "title": "Title",
        "types": {
            "Book": "relation", "Source Type": "select", "Status": "select",
            "Link": "url",
        },
    },
    {
        "name": "💡 Idea Inbox",
        "csv": "💡 Idea Inbox.csv",
        "title": "Idea",
        "types": {
            "Type": "select", "Related Book": "relation",
            "Excitement (1-5)": "number", "Status": "select",
        },
    },
    {
        "name": "📈 Word Count Log",
        "csv": "📈 Word Count Log.csv",
        "title_template": "{Date} · {Book}",
        "types": {
            "Date": "date", "Book": "relation", "Words Written": "number",
            "Minutes": "number", "Session Type": "select", "Mood": "select",
        },
    },
    {
        "name": "🎯 Writing Goals",
        "csv": "🎯 Writing Goals.csv",
        "title": "Goal",
        "types": {
            "Book": "relation", "Type": "select", "Target": "number",
            "Progress": "number", "Unit": "select", "Deadline": "date",
            "Status": "select",
        },
        "formulas": {
            "% to Goal":
                'if(prop("Target") == 0, 0, prop("Progress") / prop("Target"))',
        },
    },
    {
        "name": "📅 Writing Schedule",
        "csv": "📅 Writing Schedule.csv",
        "title": "Session",
        "types": {
            "Date": "date", "Book": "relation", "Word Target": "number",
            "Done?": "checkbox",
        },
    },
    {
        "name": "🔁 Revision & Editing Log",
        "csv": "🔁 Revision & Editing Log.csv",
        "title": "Pass",
        "types": {
            "Book": "relation", "Pass Type": "select", "Status": "select",
            "Started": "date", "Finished": "date",
            "Word Count Before": "number", "Word Count After": "number",
        },
    },
    {
        "name": "📊 Comp Titles & Market",
        "csv": "📊 Comp Titles & Market.csv",
        "title": "Title",
        "types": {"For Book": "relation", "Year": "number"},
    },
    {
        "name": "📇 Contacts & Network",
        "csv": "📇 Contacts & Network.csv",
        "title": "Name",
        "types": {
            "Role": "select", "Status": "select", "Email": "email",
            "Related Book": "relation", "Last Contact": "date",
        },
    },
    {
        "name": "📮 Submission Tracker",
        "csv": "📮 Submission Tracker.csv",
        "title": "Submission",
        "types": {
            "Book": "relation", "Type": "select", "Status": "select",
            "Date Sent": "date", "Response Date": "date",
        },
    },
    {
        "name": "✅ Publishing Checklist",
        "csv": "✅ Publishing Checklist.csv",
        "title": "Task",
        "types": {
            "Phase": "select", "Book": "relation", "Owner": "select",
            "Due": "date", "Done?": "checkbox",
        },
    },
]

CONTENT_PAGES = [
    "Ultimate Writer Planner.md",  # handled specially as the home page body
    "📊 Writing Dashboard.md",
    "📐 Story Structure Guide.md",
    "✍️ Daily Writing Ritual.md",
    "❓ How to Use This Template.md",
]


# ---------------------------------------------------------------------------
# Notion REST helpers
# ---------------------------------------------------------------------------
class Notion:
    def __init__(self, token):
        self.token = token

    def _request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(API + path, data=data, method=method)
        req.add_header("Authorization", "Bearer " + self.token)
        req.add_header("Notion-Version", NOTION_VERSION)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                time.sleep(RATE_LIMIT_SLEEP)
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise SystemExit(
                "\nNotion API error (%s) on %s %s:\n%s\n" %
                (e.code, method, path, detail)
            )

    def create_page(self, parent_page_id, title, icon=None, children=None):
        body = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "properties": {"title": [text(title)]},
        }
        if icon:
            body["icon"] = {"type": "emoji", "emoji": icon}
        if children:
            body["children"] = children[:100]
        page = self._request("POST", "/pages", body)
        if children and len(children) > 100:
            self.append_blocks(page["id"], children[100:])
        return page

    def append_blocks(self, block_id, children):
        for i in range(0, len(children), 100):
            self._request(
                "PATCH", "/blocks/%s/children" % block_id,
                {"children": children[i:i + 100]},
            )

    def create_database(self, parent_page_id, title, icon, properties):
        body = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [text(title)],
            "icon": {"type": "emoji", "emoji": icon},
            "properties": properties,
        }
        return self._request("POST", "/databases", body)

    def create_row(self, database_id, properties):
        return self._request(
            "POST", "/pages",
            {"parent": {"database_id": database_id}, "properties": properties},
        )


# ---------------------------------------------------------------------------
# Value + rich-text builders
# ---------------------------------------------------------------------------
def text(content, bold=False, code=False, link=None):
    obj = {"type": "text", "text": {"content": content[:2000]}}
    if link:
        obj["text"]["link"] = {"url": link}
    ann = {}
    if bold:
        ann["bold"] = True
    if code:
        ann["code"] = True
    if ann:
        obj["annotations"] = ann
    return obj


INLINE_RE = re.compile(
    r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)"
)


def parse_inline(s):
    out, pos = [], 0
    for m in INLINE_RE.finditer(s):
        if m.start() > pos:
            out.append(text(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append(text(m.group(1), bold=True))
        elif m.group(2) is not None:
            out.append(text(m.group(2), code=True))
        else:
            out.append(text(m.group(3), link=m.group(4)))
        pos = m.end()
    if pos < len(s):
        out.append(text(s[pos:]))
    return out or [text("")]


def prop_value(ptype, raw):
    """Build a Notion property value, or None to skip (empty/blank)."""
    v = (raw or "").strip()
    if ptype == "checkbox":
        return {"checkbox": v.lower() in ("yes", "true", "done", "x", "✓")}
    if v == "":
        return None
    if ptype == "number":
        try:
            num = float(v)
            return {"number": int(num) if num.is_integer() else num}
        except ValueError:
            return None
    if ptype == "select":
        return {"select": {"name": v[:100]}}
    if ptype == "date":
        return {"date": {"start": v}}
    if ptype == "email":
        return {"email": v}
    if ptype == "url":
        return {"url": v}
    # default
    return {"rich_text": parse_inline(v)}


# ---------------------------------------------------------------------------
# Markdown -> Notion blocks (lightweight, covers what the template uses)
# ---------------------------------------------------------------------------
CODE_LANGS = {"bash": "bash", "sh": "shell", "shell": "shell",
              "python": "python", "py": "python", "js": "javascript"}


def block(btype, **payload):
    return {"object": "block", "type": btype, btype: payload}


def md_to_blocks(md):
    lines = md.split("\n")
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            lang = CODE_LANGS.get(line[3:].strip().lower(), "plain text")
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            blocks.append(block("code",
                                 rich_text=[text("\n".join(buf))],
                                 language=lang))
            continue
        s = line.strip()
        i += 1
        if not s:
            continue
        if s == "---":
            blocks.append(block("divider"))
        elif s.startswith("### "):
            blocks.append(block("heading_3", rich_text=parse_inline(s[4:])))
        elif s.startswith("## "):
            blocks.append(block("heading_2", rich_text=parse_inline(s[3:])))
        elif s.startswith("# "):
            blocks.append(block("heading_1", rich_text=parse_inline(s[2:])))
        elif s.startswith("> "):
            body = s[2:]
            if body[:1] and ord(body[0]) > 0x2000:  # leads with an emoji
                blocks.append(block("callout", rich_text=parse_inline(body),
                                    icon={"type": "emoji", "emoji": body[0]}))
            else:
                blocks.append(block("quote", rich_text=parse_inline(body)))
        elif re.match(r"- \[[ xX]\] ", s):
            checked = s[3].lower() == "x"
            blocks.append(block("to_do", rich_text=parse_inline(s[6:]),
                                checked=checked))
        elif s[:2] in ("- ", "* "):
            blocks.append(block("bulleted_list_item",
                                rich_text=parse_inline(s[2:])))
        elif re.match(r"\d+\. ", s):
            blocks.append(block("numbered_list_item",
                                rich_text=parse_inline(re.sub(r"^\d+\. ", "", s))))
        elif s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue  # table separator row
            joined = "  —  ".join(c for c in cells if c)
            blocks.append(block("bulleted_list_item",
                                rich_text=parse_inline(joined)))
        else:
            blocks.append(block("paragraph", rich_text=parse_inline(s)))
    return blocks


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------
def load_csv(filename):
    path = os.path.join(PLANNER_SUBDIR, filename)
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def parse_page_id(value):
    """Accept a raw id or a Notion URL; return a dashed UUID."""
    m = re.findall(r"[0-9a-fA-F]{32}", value.replace("-", ""))
    if not m:
        raise SystemExit("Could not find a Notion page id in: %s" % value)
    h = m[-1].lower()
    return "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_db_properties(schema, book_db_id):
    props = {}
    title_col = schema.get("title")
    if "title_template" in schema:
        props["Name"] = {"title": {}}
    for col, ptype in schema.get("types", {}).items():
        if ptype == "relation":
            props[col] = {"relation": {"database_id": book_db_id,
                                       "single_property": {}}}
        elif ptype == "select":
            props[col] = {"select": {}}
        elif ptype == "number":
            props[col] = {"number": {"format": "number"}}
        else:
            props[col] = {ptype: {}}
    # any column not typed and not the title becomes rich_text
    sample = load_csv(schema["csv"])
    if sample:
        for col in sample[0].keys():
            if col == title_col:
                props[col] = {"title": {}}
            elif col not in props and "title_template" not in schema:
                props[col] = {"rich_text": {}}
            elif col not in props:
                props[col] = {"rich_text": {}}
    for fname, expr in schema.get("formulas", {}).items():
        props[fname] = {"formula": {"expression": expr}}
    return props


def build_row_properties(schema, row, book_ids):
    props = {}
    title_col = schema.get("title")
    types = schema.get("types", {})
    if "title_template" in schema:
        title = schema["title_template"].format(**row).strip(" ·-")
        props["Name"] = {"title": [text(title or "Untitled")]}
    for col, val in row.items():
        ptype = types.get(col, "rich_text")
        if col == title_col:
            props[col] = {"title": [text((val or "Untitled").strip()
                                         or "Untitled")]}
            continue
        if ptype == "relation":
            page_id = book_ids.get((val or "").strip())
            if page_id:
                props[col] = {"relation": [{"id": page_id}]}
            continue
        value = prop_value(ptype, val)
        if value is not None:
            props[col] = value
    return props


def run(token, parent_id, dry_run):
    home_md = open(os.path.join(TEMPLATE_DIR, "Ultimate Writer Planner.md"),
                   encoding="utf-8").read()

    if dry_run:
        print("DRY RUN — validating data and schema, no API calls.\n")
        total = 0
        for s in SCHEMAS:
            rows = load_csv(s["csv"])
            props = list(build_db_properties(s, "DRY-BOOK-ID").keys())
            rels = [c for c, t in s.get("types", {}).items()
                    if t == "relation"]
            fms = list(s.get("formulas", {}).keys())
            total += len(rows)
            print("  %-26s %2d rows | %2d props%s%s"
                  % (s["name"], len(rows), len(props),
                     "  rel:" + ",".join(rels) if rels else "",
                     "  fx:" + ",".join(fms) if fms else ""))
        blocks = md_to_blocks(home_md)
        print("\n  Home page: %d blocks" % len(blocks))
        for f in CONTENT_PAGES[1:]:
            md = open(os.path.join(PLANNER_SUBDIR, f), encoding="utf-8").read()
            print("  %-26s %d blocks" % (f, len(md_to_blocks(md))))
        print("\nTotal seed rows: %d across %d databases."
              % (total, len(SCHEMAS)))
        print("Looks good. Re-run with --token and --parent to install.")
        return

    nx = Notion(token)
    print("Creating home page …")
    home = nx.create_page(parent_id, "Ultimate Writer Planner", icon="✍️",
                          children=md_to_blocks(home_md))
    planner_id = home["id"]

    print("Creating databases …")
    db_ids = {}
    book_db_id = None
    for s in SCHEMAS:
        props = build_db_properties(s, book_db_id)
        db = nx.create_database(planner_id, s["name"], s["name"][0], props)
        db_ids[s["name"]] = db["id"]
        if s["name"] == "📚 Book Projects":
            book_db_id = db["id"]
        print("   ✓ %s" % s["name"])

    print("Seeding rows (Book Projects first for relations) …")
    book_ids = {}
    # Seed Book Projects first to capture title -> page id for relations.
    book_schema = SCHEMAS[0]
    for row in load_csv(book_schema["csv"]):
        page = nx.create_row(book_db_id,
                             build_row_properties(book_schema, row, {}))
        book_ids[row[book_schema["title"]].strip()] = page["id"]
    print("   ✓ 📚 Book Projects (%d rows)" % len(book_ids))

    for s in SCHEMAS[1:]:
        rows = load_csv(s["csv"])
        for row in rows:
            nx.create_row(db_ids[s["name"]],
                          build_row_properties(s, row, book_ids))
        print("   ✓ %s (%d rows)" % (s["name"], len(rows)))

    print("Creating reference pages …")
    for f in CONTENT_PAGES[1:]:
        md = open(os.path.join(PLANNER_SUBDIR, f), encoding="utf-8").read()
        title = os.path.splitext(f)[0]
        nx.create_page(planner_id, title, icon=title[0],
                       children=md_to_blocks(md))
        print("   ✓ %s" % title)

    print("\n✅ Done! Open Notion — 'Ultimate Writer Planner' is ready.")
    print("Remaining 1-minute touches (the API can't create these):")
    print("  • Add Board/Calendar/Chart views (see the How-to page).")
    print("  • Add database templates for one-click new entries.")
    print("  • Set the % formulas' display to 'Bar' for progress bars.")


def main():
    ap = argparse.ArgumentParser(description="Install Ultimate Writer Planner "
                                             "into a Notion account.")
    ap.add_argument("--token", default=os.environ.get("NOTION_TOKEN"),
                    help="Notion integration secret (or set NOTION_TOKEN).")
    ap.add_argument("--parent",
                    help="URL or id of the Notion page to install into "
                         "(must be shared with the integration).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate data/schema without calling Notion.")
    args = ap.parse_args()

    if args.dry_run:
        run(None, None, dry_run=True)
        return
    if not args.token:
        sys.exit("Missing token. Set NOTION_TOKEN or pass --token.")
    if not args.parent:
        sys.exit("Missing --parent (the Notion page URL to install into).")
    run(args.token, parse_page_id(args.parent), dry_run=False)


if __name__ == "__main__":
    main()
