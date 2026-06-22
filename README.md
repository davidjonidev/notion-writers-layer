# ✍️ Ultimate Writer Planner — Free Notion Template

A complete, **100% free** writing command center for Notion — inspired by premium
"ultimate writer planner" templates, but with no paywall and no duplication link
required. Just **import and write**.

Plan books, track word counts, build characters and worlds, manage research,
query agents, and run your publishing pipeline — all in one Notion space.

---

## 📦 What's inside

| Page | Type | Purpose |
| --- | --- | --- |
| 📊 Writing Dashboard | Page | Daily command center |
| 📚 Book Projects | Database | One row per manuscript, with status & word goals |
| 📕 Series & Saga | Database | Multi-book series, reading order & overarching arcs |
| 📖 Chapters & Scenes | Database | Outline and draft scene by scene |
| 🧵 Plot & Beats | Database | A fillable beat board (3-act / Save the Cat! mapped) |
| 👤 Characters | Database | Profiles, arcs, wants/needs, relationships |
| 🌍 World Building | Database | Places, factions, lore, magic/tech rules |
| 🔬 Research & Notes | Database | Sources, facts, reference material |
| 💡 Idea Inbox | Database | Capture sparks before they fade |
| 📈 Word Count Log | Database | Per-session word counts & streaks |
| 🎯 Writing Goals | Database | Quarterly and project targets |
| 📅 Writing Schedule | Database | When and what you'll write |
| 🔁 Revision & Editing Log | Database | Track every editing pass (dev/line/copy/proof) |
| 📊 Comp Titles & Market | Database | Comparable books to power your pitch/query |
| 📇 Contacts & Network | Database | Agents, editors, beta readers, designers |
| 📮 Submission Tracker | Database | Queries, agents, contests, publishers |
| ✅ Publishing Checklist | Database | From final draft to launch day |
| 📐 Story Structure Guide | Page | Three-Act, Save the Cat!, Hero's Journey, 7-point |
| ✍️ Daily Writing Ritual | Page | Beat the blank page |
| ❓ How to Use This Template | Page | Setup, smart formulas, charts & power-ups |

Every database ships with **realistic example rows** so nothing looks empty —
delete them once you've seen how it works.

### Beyond a static export

The **❓ How to Use** page includes copy-paste **formulas** (words remaining,
% complete progress bars, and an auto-calculated *daily word goal* based on your
deadline), plus how to add **chart views** and **one-click database templates** —
the "smart" touches usually reserved for paid templates.

---

## 🚀 Option A — Quick install via import (60 seconds)

1. **Download** the package: [`dist/Ultimate-Writer-Planner.zip`](dist/Ultimate-Writer-Planner.zip)
   (or build it yourself — see below).
2. In Notion, go to **Settings → Import** (or the **⚙️** / **Import** button in the sidebar).
3. Choose **Markdown & CSV**.
4. Select the `Ultimate-Writer-Planner.zip` file.
5. Notion rebuilds the full page tree. Drag **Ultimate Writer Planner** into your sidebar. Done!

> 💡 After importing, open the **❓ How to Use This Template** page. It lists the
> few CSV columns worth switching from *Text* to *Select / Number / Date* to unlock
> filters, boards, and rollups.

---

## 🤖 Option B — Fully-loaded install via the Notion API (recommended)

The import above brings columns in as plain text. If you want the **complete**
workspace — typed properties, live cross-database **relations**, the **formulas**
(words remaining, % complete, auto daily word goal), and all seed rows
**pre-linked** — use the auto-installer. It builds everything directly in a
Notion account.

```bash
# 1. Create an integration at https://www.notion.so/my-integrations and copy the secret.
# 2. Create/pick a Notion page, and via "..." -> Connections, add your integration.
# 3. Run:
export NOTION_TOKEN="ntn_your_secret_here"
python3 scripts/notion_install.py --parent "https://www.notion.so/your-page-url"

# Preview first without touching Notion:
python3 scripts/notion_install.py --dry-run
```

No third-party packages — standard library only. Full step-by-step is in the
header of [`scripts/notion_install.py`](scripts/notion_install.py).

> 🔒 **This repo is public.** Your integration token is a password. Never paste
> it into a commit, an issue, or any file in this repo. Pass it via the
> `NOTION_TOKEN` environment variable (already covered by `.gitignore`) and
> run the script on your own machine.

The only things the Notion API cannot create are **views** (board/calendar/chart)
and **database templates** — the installer prints the 1-minute manual steps for
those when it finishes, and they're detailed in the **❓ How to Use** page.

## 🛠️ Build the zip yourself

The source lives as plain Markdown + CSV in [`template/`](template/) so it's easy
to read, diff, and customize. To (re)build the importable zip:

```bash
./scripts/build.sh
```

This produces `dist/Ultimate-Writer-Planner.zip`.

You can also import **without** zipping: in Notion's Markdown & CSV importer,
select all the files inside `template/` directly.

---

## ✏️ Customize it

- Edit any `.md` file to change page copy.
- Edit any `.csv` file to change database columns or starter rows
  (first row = property names, first column = the title property).
- Add your own pages/databases by dropping new `.md` / `.csv` files into
  `template/Ultimate Writer Planner/`, then rebuild.

---

## 📁 Repository layout

```
.
├── README.md
├── scripts/
│   └── build.sh                     # zips template/ into dist/
├── template/
│   ├── Ultimate Writer Planner.md   # home page
│   └── Ultimate Writer Planner/     # all sub-pages & databases
└── dist/
    └── Ultimate-Writer-Planner.zip  # importable package
```

> In Notion's importer, a folder named exactly like a `.md` file becomes that
> page's children — which is why `Ultimate Writer Planner.md` and the
> `Ultimate Writer Planner/` folder sit side by side.

---

## 🆓 License

Released under the MIT License — free to use, copy, modify, and share, for any
purpose, including commercially. No attribution required. See [`LICENSE`](LICENSE).

Happy writing. ✍️
