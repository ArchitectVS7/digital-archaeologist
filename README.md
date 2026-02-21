# Digital Archaeologist

**AI-Powered Project Resurrection Engine**

Scans your project graveyard, analyzes why projects stalled, and scores which ones are ready to come back to life.

## Quick Start

```bash
pip install -r requirements.txt
python archaeologist.py scan ~/projects
python archaeologist.py resurrect --top 5
```

## What It Does

1. **Excavation:** Scans git repos, extracts intent from READMEs/commits
2. **Stall Analysis:** Detects why each project stopped (tech obsolete, scope creep, dependency issues)
3. **Resurrection Scoring:** Rates 0-100 based on current viability
4. **Trend Mapping:** Cross-references with HN/GitHub trends (Phase 2)
5. **Remix Engine:** Finds complementary project pairs (Phase 3)

## Phase 1 Implementation

Currently implemented:
- ✅ Git repo scanning
- ✅ Stall analysis (last commit, dependency age)
- ✅ Basic resurrection scoring
- ⏸️ Trend mapping (Phase 2)
- ⏸️ Remix engine (Phase 3)

## Example Output

```
Scanned: 47 repos, 23 stalled projects identified

Top Resurrection Candidates:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [92/100] voice-notes-cli (2019)
   Stalled: 1847 days ago
   Dependencies: 3/5 outdated
   Action: Speech-to-text is now local/free (Whisper)

2. [87/100] markdown-cms (2021)
   Stalled: 1095 days ago
   Dependencies: 2/8 outdated
   Action: Static site generators solved deployment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## License

MIT
