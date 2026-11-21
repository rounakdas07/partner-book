# Partner Book for WombWise

[Open the tool](https://rounakdas07.github.io/partner-book/)

A prepared UK clinical-partner prospect book: choose a team, see the relevant study evidence and a public research enquiry route, save notes, then export the shortlist to a spreadsheet or copy a partner brief.

WombWise [publicly says it is building a clinical partners programme](https://www.wombwise.co.uk/contact). Its [careers page](https://www.wombwise.co.uk/careers) also describes NHS/university validation work and a January 2027 pilot. This project supports the founder's partnership research task. It does not claim these organisations have expressed interest or are new to WombWise.

## What is in this snapshot

Retrieved 21 November 2026 from the ClinicalTrials.gov API:

| Screening step | Result | Audit file |
| --- | ---: | --- |
| Entire condition query, all pages | 2,042 studies | [Full screening log](data/screening.csv) |
| Studies with an explicitly listed UK location | 49 | [Derived records](data/partners.json) |
| UK location rows | 73 | [Derived records](data/partners.json) |
| Anonymous / unnamed location rows excluded | 11 | [Exclusions](data/partners.json) |
| Named leads after explicit alias consolidation | 32 | [Alias table](data/aliases.json) |
| Leads with records updated within two years | 15 | [Derived records](data/partners.json) |
| Manually checked institutional enquiry routes | 4 | [Enrichment and sources](data/enrichment.json) |

The full registry pull contains real public study records, not generated sample data. The UI loads a small derived dataset; it does not fetch thousands of records on every visit. This is a dated snapshot, not a live feed. The retrieval manifest records each request, page count and SHA-256 hash. The CSV lists every screened study with its source URL and country classification.

The opening lead is Edinburgh's ENDO1000 work, which combines smartwatch and repeated symptom measures. The suggested conversation is a separately agreed validation collaboration; ENDO1000 already has an app. No participant access or research-data access is promised.

## Contact provenance

- Edinburgh: [EXPPECT research team](https://reproductive-health.ed.ac.uk/pelvic-pain/our-research), published academic contact for its digital health lead.
- Oxford: [EndoCaRe enquiries](https://www.wrh.ox.ac.uk/research/endocare-get-involved), a general research centre enquiry desk.
- Birmingham: [collaboration contacts](https://www.birmingham.ac.uk/collaborate/contact), the university business engagement team for collaborative research.
- Chelsea and Westminster: [researcher support](https://www.chelwest.nhs.uk/about-us/research-innovation-and-quality-improvement-riqi/research-development/researchers), NHS research operations for external researchers and sponsors.

These routes were checked against the official published pages on 21 November 2026. No outreach has been sent. A published route does not verify a monitored inbox, interest, funding or capacity. Unverified routes are left unverified rather than filling the gaps with invented contacts or participant-recruitment addresses.

## Ordering and interpretation

The default view includes leads with at least one registry record updated on or after 21 November 2024. An administrative update to a completed study qualifies; it is not a claim of ongoing recruitment.

Priority is the sum of: an explicitly active UK site in a recently updated study (+40); any recent record (+20); a wearable term in the study description/outcomes (+20); a checked institutional enquiry route (+15); a symptom diary/app term (+10); and observational study experience (+10). Ties use latest update, then name. Points organise the list; they are not a probability, a clinical assessment or a claimed buying signal.

Overall trial status is kept separate from local site status. Missing site status is not inferred. Unknown statuses stay unknown. Study counts are deduplicated by NCT ID. Trial-wide enrollment is never presented as locally available patients. Experience signals can come from historical studies, and link to those records. Exact word boundaries avoid false matches such as `Oura` inside `behavioural`.

Only explicitly named aliases are consolidated. Edinburgh and Oxford entries are descriptive research clusters across connected university/hospital sites, not legal-entity mergers. Accellacare is consolidated as a network. All original facility names remain in the dataset and CSV site-status field.

The search covers one registry and two condition concepts. It misses studies registered only elsewhere and studies without a UK location field. Conditions are classified using recorded condition names, not inferred from participant traits. Suggested first conversations and fit explanations are editorial interpretations and visibly labelled as suggestions.

## Existing tools

[SiteFinder](https://sitefinder.tghn.org/about/) already provides site search, maps, contact routes and CSV downloads. Partner Book does not claim to invent that category. Its added work is a completed WombWise-specific registry screen, consolidation, transparent prioritisation, checked institutional routes and a prepared briefing/export workflow. It is a tailored research deliverable, not a replacement for a trial feasibility platform.

## Use

No login or API key. Select a team to inspect its evidence and enquiry route. Save leads with the star, record a stage and notes, then choose **My shortlist** and **Export**. CSV files include sources, contact-check dates, study status, the snapshot date and your own notes. Spreadsheet formula cells are escaped.

Shortlists and notes stay in the browser's local storage. They are not synced or sent to a server. Clearing browser data removes them; export to preserve them. Clipboard fallback displays a selectable brief if clipboard access is unavailable. No analytics, external fonts, patient data or automatic messages are used.

## Refresh and develop

Python 3.10+ and a current Node.js; no package dependencies.

```bash
python scripts/fetch_registry.py
python scripts/prepare_data.py
npm test
npm run build
```

The first command follows every registry page for `Endometriosis OR "Polycystic Ovary Syndrome"`. The second rebuilds the screening log, lead data and alias table. Recheck `data/enrichment.json` contact routes and dates manually before republishing; registry refresh does not reverify those pages. A refreshed dataset can differ from this snapshot.

Serve `dist/` with a static host. In the managed development environment, use `sites-preview start <absolute-checkout>`. The GitHub Pages version serves this folder directly from the repository; its source files are also the deployable static assets.

The large raw registry and UK extracts are generated locally and excluded from Git. Run the refresh commands before raw-data validation tests. The committed screening log, manifest and derived records preserve the shipped snapshot's lineage.

## Validation

- Data reconciliation: all screened IDs accounted for; UK locations verified against the raw records; excluded rows reconciled; dates/counts checked; site activity never inferred from overall status.
- Application checks: composed filters, saved-only view, validation of stored state, CSV source fields/formula escaping, brief provenance.
- Browser QA: desktop and narrow-screen layout, opening/back navigation, shortlist save, notes/stage after reload, condition/contact filters, clipboard brief and CSV download.

Built by [Rounak Das](https://github.com/rounakdas07). Independent project for WombWise; not an official WombWise product.
