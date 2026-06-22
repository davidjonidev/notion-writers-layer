# ❓ How to Use This Template

Welcome! This page explains how everything fits together so you can be writing in five minutes.

---

## 📥 Installing (you may already be done)

If you're reading this inside Notion, the import worked. 🎉

If not, here's how to import:

1. In Notion, click **Settings** (or the **⚙️** in the sidebar) → **Import**.
2. Choose **Markdown & CSV**.
3. Select the downloaded `Ultimate-Writer-Planner.zip` (or the unzipped folder).
4. Wait a moment — Notion rebuilds the full page tree.
5. Drag **Ultimate Writer Planner** anywhere in your sidebar.

> 💡 Tip: After import, open each CSV-based database and confirm the property types (a few are explained below). Notion imports most columns as text; switching them to the right type unlocks filters and rollups.

---

## 🗂️ How the pieces connect

| Page | What it's for | Open it when… |
| --- | --- | --- |
| 📊 Writing Dashboard | Daily command center | Every writing session |
| 📚 Book Projects | One row per manuscript | Starting or reviewing a book |
| 📕 Series & Saga | Multi-book series & arcs | Planning a series |
| 📖 Chapters & Scenes | Outline + draft tracking | Planning or drafting |
| 🧵 Plot & Beats | Fillable beat board | Outlining structure |
| 👤 Characters | Profiles, arcs, relationships | Developing cast |
| 🌍 World Building | Places, lore, rules | Building your setting |
| 🔬 Research & Notes | Sources and facts | Researching |
| 💡 Idea Inbox | Quick capture | A new idea strikes |
| 📈 Word Count Log | Per-session word counts | After you write |
| 🎯 Writing Goals | Targets and deadlines | Planning the quarter |
| 📅 Writing Schedule | Calendar of sessions | Weekly planning |
| 🔁 Revision & Editing Log | Every editing pass | Revising a draft |
| 📊 Comp Titles & Market | Comparable books | Building a pitch/query |
| 📇 Contacts & Network | Agents, editors, readers | Networking & hiring |
| 📮 Submission Tracker | Queries & submissions | Querying agents/markets |
| ✅ Publishing Checklist | Launch tasks | Finishing a book |

---

## 🔧 Recommended property types to set after import

Notion imports CSV columns as **Text** by default. For the best experience, change these:

- **📚 Book Projects** → `Status` to *Select*, `Genre` to *Select*, `Target Word Count` and `Current Word Count` to *Number*, `Deadline` to *Date*.
- **📖 Chapters & Scenes** → `Status` to *Select*, `Word Count` to *Number*, `Order` to *Number*, `POV Character` to *Text or Relation*.
- **👤 Characters** → `Role` to *Select*, `Status` to *Select*.
- **📈 Word Count Log** → `Date` to *Date*, `Words Written` to *Number*, `Minutes` to *Number*.
- **🎯 Writing Goals** → `Target` and `Progress` to *Number*, `Deadline` to *Date*, `Status` to *Select*.
- **📮 Submission Tracker** → `Date Sent` and `Response Date` to *Date*, `Status` to *Select*.
- **🧵 Plot & Beats** → `Act` and `Status` to *Select*, `Order` and `Tension (1-10)` to *Number*, `Linked Scene` to *Relation* (→ Chapters & Scenes).
- **🔁 Revision & Editing Log** → `Pass Type` and `Status` to *Select*, `Started`/`Finished` to *Date*, word counts to *Number*.
- **📇 Contacts & Network** → `Role` and `Status` to *Select*, `Email` to *Email*, `Last Contact` to *Date*.
- **📕 Series & Saga** → `Reading Order` and `Planned Books` to *Number*, `Status` to *Select*.

> 💡 Want to link a scene to its book? Add a **Relation** property in *Chapters & Scenes* pointing to *Book Projects*. Then add a **Rollup** in *Book Projects* to sum scene word counts automatically.

---

## ⚡ Power-ups (optional)

- **Streak tracking:** In *Word Count Log*, group by week and add a sum on `Words Written`.
- **Daily total:** Add a *Rollup* from *Word Count Log* into *Book Projects* to auto-update `Current Word Count`.
- **Kanban drafting:** Open *Chapters & Scenes* (or *Plot & Beats*), add a **Board** view grouped by `Status`.
- **Calendar:** Add a **Calendar** view to *Writing Schedule* on the `Date` property.
- **Editing pipeline:** In *Revision & Editing Log*, add a **Board** view grouped by `Pass Type` or `Status`.

---

## 🧮 Smart formulas (copy-paste)

These turn the static databases into a "living" planner. In **📚 Book Projects**, set `Target Word Count`, `Current Word Count`, and `Deadline` to the right types first, then add **Formula** properties:

**Words remaining**
```
prop("Target Word Count") - prop("Current Word Count")
```

**% complete** (shows as a progress bar — set the formula property's display to *Bar* / *Percent*)
```
prop("Current Word Count") / prop("Target Word Count")
```

**Auto daily word goal** — how many words/day to finish on time (the premium "smart goal" feature):
```
if(
  empty(prop("Deadline")),
  0,
  round(
    (prop("Target Word Count") - prop("Current Word Count")) /
    max(dateBetween(prop("Deadline"), now(), "days"), 1)
  )
)
```

**Status emoji** — at-a-glance health:
```
if(prop("Current Word Count") >= prop("Target Word Count"), "✅ Done",
  if(prop("Current Word Count") / prop("Target Word Count") > 0.5, "🟢 On track", "🟡 Keep going"))
```

> 💡 In *Word Count Log*, add a formula `prop("Words Written") / (prop("Minutes") / 60)` to see your **words-per-hour** pace.

---

## 📈 Charts (visualize your progress)

Notion has a built-in **Chart** view. Two worth adding:

- **Word Count Log → Chart:** X-axis = `Date`, Y-axis = sum of `Words Written`. Instant progress-over-time graph.
- **Book Projects → Chart:** a bar chart of `Current Word Count` per book to compare projects at a glance.

---

## 🧩 Database templates (one-click new entries)

Open any database → click the **▾** next to the blue **New** button → **+ New template**. Build a reusable skeleton so every new entry starts pre-filled. Great ones to make:

- *Characters:* a blank profile with all your sections (Backstory, Voice, Arc).
- *Chapters & Scenes:* a scene page pre-loaded with the **Scene Checklist** (goal, conflict, turn, hook).
- *Book Projects:* a new-book page with the beat sheet from **📐 Story Structure Guide** already inside.

---

## 🆓 License

Free to use, copy, modify, and share. No attribution required — though a kind word is always welcome. Happy writing!
