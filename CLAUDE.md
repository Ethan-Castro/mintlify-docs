# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a Mintlify documentation site being built out as the documentation and educational site for the **College of Staten Island (CSI) High Performance Computing Center (HPCC)**. Audience: CSI HPCC researchers, students, and staff.

The repo has been converted from the Mintlify starter into CSI HPCC documentation. The public navigation in [docs.json](docs.json) points to HPCC, Empire AI, and support pages. Some legacy Mintlify starter examples remain under [essentials/](essentials/) and [api-reference/](api-reference/); treat those as unpublished examples unless they are explicitly added to navigation.

Content is authored as MDX files with YAML frontmatter; site configuration (theme, navigation, navbar, footer) lives in [docs.json](docs.json). There is no build step or package.json; Mintlify consumes the MDX + `docs.json` directly via its CLI/hosted renderer.

## Commands

Prereqs: Node.js 19+. The Mintlify CLI is installed globally: `npm i -g mint`.

- `mint dev`: local preview at http://localhost:3000. Must be run from the directory containing `docs.json`.
- `mint dev --port 3333`: use a custom port.
- `mint broken-links`: validate internal links across all MDX pages.
- `mint update`: upgrade the CLI when the local preview drifts from production.

Troubleshooting: if `mint dev` fails with a `sharp` module error, reinstall the CLI on Node 19+. For unknown errors, delete `~/.mintlify` and retry.

## Architecture

- **Navigation is explicit, not filesystem-based.** Adding a new MDX file does *not* make it appear in the site. You must also register it under `navigation.tabs[].groups[].pages` in [docs.json](docs.json). Pages are referenced by path without the `.mdx` extension (e.g. `essentials/settings`).
- **Content lives at the repo root by topic directory**: [empire-ai/](empire-ai/) (Empire AI context), [ai-tools/](ai-tools/) (per-tool setup guides), [snippets/](snippets/) (reusable MDX fragments), plus top-level pages like [index.mdx](index.mdx), [quickstart.mdx](quickstart.mdx), [systems.mdx](systems.mdx), and [job-submission.mdx](job-submission.mdx). Legacy starter examples remain under [essentials/](essentials/) and [api-reference/](api-reference/) but are not part of the current public navigation.
- **[.mintignore](.mintignore)** excludes drafts from the build (`drafts/`, `*.draft.mdx`) on top of Mintlify's implicit ignores (`.git`, `.github`, `.claude`, `node_modules`, `README.md`, `LICENSE.md`, `CHANGELOG.md`, `CONTRIBUTING.md`).
- **Deployment** is automatic: pushes to the default branch propagate to production via the Mintlify GitHub app. There is no CI config in this repo.

## Mintlify component reference

This repo uses Mintlify MDX components (`<Steps>`, `<Accordion>`, `<Frame>`, `<Info>`, `<Card>`, etc.) that are not standard MDX. Before authoring non-trivial content, install the Mintlify skill for complete component and frontmatter reference:

```bash
npx skills add https://mintlify.com/docs
```

## Writing conventions

From [AGENTS.md](AGENTS.md) and `CONTRIBUTING.md`:

- Active voice, second person ("you"), one idea per sentence.
- Sentence case for headings.
- Bold for UI elements (`Click **Settings**`); code formatting for file names, commands, and paths.
- Lead instructions with the goal; keep terminology consistent across pages.
