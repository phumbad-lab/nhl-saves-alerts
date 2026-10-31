# Daily reviews and patterns

Written by the daily review (Claude) each morning after results are graded, plus the owner's own reads.
Purpose: spot repeatable reasons the model misses, so they can be **tested** and maybe built in later.
Nothing here changes the model by itself (owner's rule: no rules on hunches; test against results first).

## Read accuracy (season to date, from Oct 12)
Judges the read on shot volume, not just the bet result.
- **Through Oct 30:** Right reads ✅ 38 · Lucky wins 🍀 3 · Unlucky losses 😬 3 · Wrong reads ❌ 45 (volume read right ✅+😬 = 41/89 = 46%)
- Oct 30: ❌2 (3 games, 2 tagged goalies, both road OVERs).
- Oct 29: ✅3 😬1 ❌7 (11 games, 11 tagged goalies by first line; Knight's FD LEAN OVER came after a DK NO EDGE line, not counted — it lost).
- Oct 28: 😬1 ❌3 (4 games, 4 tagged goalies by first line; Thompson's FD LEAN UNDER came with a DK NO EDGE line, not counted — it lost on save%, volume on target).
- Oct 27: 🍀1 ❌2 (11 games, 3 tagged goalies by first line; Merilainen's FD LEAN OVER came after a DK NO EDGE line, not counted — it was also wrong).
- Oct 26: ✅1 (3 games, 1 tagged goalie).
- Oct 25: ✅1 (5 games, 1 tagged goalie by first line; Schmid's DK LEAN UNDER came after an FD NO EDGE line, not counted — it was also right).
- Oct 24: ✅6 ❌5 (12 games, 11 tagged goalies).
- Oct 23: ❌1 (2 games, 1 tagged goalie).
- Oct 22: ✅3 ❌3 (12 games, 6 tagged goalies).
- Oct 21: ✅1 ❌2 (2 games, 3 tagged goalies).
- Oct 20: ✅3 ❌2 (11 games, 5 tagged goalies).
- Oct 19: ✅2 ❌3 (4 games).
- Oct 18: ✅1 (only one tagged goalie on a 2-game night).
- Oct 17: ✅6 ❌6 (14 games, 12 tagged goalies).
- Oct 16: 😬1 (only one tagged goalie on a 2-game night).
- Oct 15: ✅6 🍀1 ❌1.
- Oct 14: ✅1 (only one tagged goalie on a 2-game night).
- Oct 12 is partial (only Markstrom 🍀 and Wallstedt ❌ were reviewed); full nightly counting starts Oct 13 (✅4 ❌7).

## 🎯 and ⚠️ markers (started Oct 24; each goalie once, first line)
Backtest baseline Oct 7–23: 🎯 unders 14-6, 🎯 overs 12-14; model tags with a conflicting top/bottom-10 rank 7-2; owner's bets with a conflicting rank 2-8.
- **Running (live, from Oct 24):** 🎯 under → under 4-3 · 🎯 over → over 4-7 · model tag with ⚠️ 0-2 · without ⚠️ 12-20.
- Oct 24: 🎯 under Wallstedt DK u22.5 ❌ (23; FD 25.5 would have won). 🎯 over Cooley ✅ (28 vs 26.5), Daccord ✅ (31 vs 26.5), Forsberg ❌ (23 vs 28.5). ⚠️ Vejmelka UNDER (TBL 5th most for) ❌ — warning was right (TBL 32 shots).
- Oct 25: 🎯 under Schmid FD u20.5 ✅ (19), Pickard DK u20.5 ✅ (15). 🎯 over Merilainen FD o25.5 ✅ (30), Annunen FD o29.5 ❌ (19; COL shot 21), Skinner DK o25.5 ❌ (19; MTL shot 21). All five were NO EDGE goalies. No ⚠️. Oettinger UNDER (no ⚠️) ✅.
- Oct 26: 🎯 over Bobrovsky DK o26.5 ✅ (29; CGY 34 shots). 🎯 under Postava u25.5 ✅ (25, by half a save; EDM 28 ≈ 27.7 exp; NO EDGE goalie). No ⚠️.
- Oct 27: 🎯 under Hill FD u20.5 ❌ (25; OTT 26 vs 24.7 exp; NO EDGE goalie). ⚠️ Merilainen FD LEAN OVER (ANA 4th least for) ❌ — warning right (ANA 23 shots; his DK first line was NO EDGE 28.5, owner took the under ✅). Tags without ⚠️ 1-2.
- Oct 28: 🎯 over Grubauer o25.5 ❌ (17; TOR 21 vs 28.6 exp; NO EDGE goalie; owner bet it). No ⚠️. Tags without ⚠️ 0-4.
- Oct 29: 🎯 under Gibson u21.5 ✅ (18; CHI 19), Kochetkov u20.5 ❌ (24; CBJ 26 vs 22.4 exp). 🎯 over Skinner o25.5 ❌ (16; pulled, TBL 31), Knight DK o28.5 ❌ (27; DET 31; NO EDGE goalie, owner took the under ✅). No ⚠️. Tags without ⚠️ 3-8.
- Oct 30: 🎯 over Grubauer o26.5 ❌ (10 saves; CGY 27 vs 31.4 exp — short even before he left early). No ⚠️. Tags without ⚠️ 0-2.

## Patterns to watch (update as evidence builds; note game count)
- **H2H low-volume matchups vs. an OVER/LEAN OVER read** (1 game). Owner faded Wallstedt o26.5 (Oct 12) because VGK had shot little on MIN in H2H (avg 24.0) — model said 25.7 expected. Went under (21). Test idea: does H2H avg below line predict unders when the model leans over?
  - Oct 13: no new case. Caution on H2H generally: in 6 of the 7 wrong reads Oct 13 the H2H L4 *agreed* with the tag (Skinner 29.5, Allen 30, Stolarz 31 shots for overs; Hill 21.3, Blackwood 19.5, Luukkonen 26 for unders) — H2H did not save any of them. Only Dostal's H2H (26.8 on ANA) pointed against the lean under, and it was right (CGY 36).
  - Oct 14: H2H right on COL-DAL (DAL on COL avg 20.5 → 22 shots, Wedgewood under won; COL on DAL 27.5 → 27). Wrong on MTL-WSH (WSH on MTL avg 33.8 → only 23; MTL on WSH 26.8 → 30). Mixed — no edge from H2H alone yet.
  - Oct 15: H2H pointed against the model on 4 tagged reads — right on Woll (DET on PHI avg 26.0 → 26 vs 33.2 exp) and Levi (UTA on EDM 25.5 → 24 vs 29.7), wrong on Varlamov (OTT on NYI 25.5 → 19) and Merilainen (FLA on VAN 27.5 → 39). Owner's H2H reads: Skinner (CHI on WPG avg 22 → 28) wrong; Bobrovsky H2H (BUF on TOR avg 30) warned against his under and was right (34). Running tally when H2H disagrees with the model: 3 right / 3 wrong (Dostal, Woll, Levi vs Varlamov, Merilainen, + Oct 14 WSH). Still a coin flip; test once ~15–20 disagreements.
  - Oct 16: H2H wrong twice. COL on PIT avg 27.3 vs model 31.6 exp → COL shot 32 (model right). Owner's "H2H looks good" on Dostal (BOS on ANA avg 34.0) → BOS shot 22. Running when H2H disagrees with the model: 3 right / 4 wrong.
  - Oct 17: H2H on the other side of league avg (27.0) from the tag 4 times — **right all 4**: Greaves UNDER (NYR on CBJ avg 28.0 → 29), Swayman OVER (LAK on BOS 26.3 → 26), Nedeljkovic OVER (DET on SJS 26.3 → 27), Murashov OVER (VGK on PIT 25.8 → 19). All three losing OVERs had H2H below league avg. Borderline, not counted: Daccord (FLA on SEA 27.3 → 37, over won). **Running: 7 right / 4 wrong (11).** Test once ~15–20: OVER tags where H2H avg < league avg.
  - Oct 18: no disagreement case (Cooley OVER, H2H CAR on CGY 30.5 agreed → CAR 36). On NO EDGE goalies H2H was 2 right (MIN on CBJ 35.0 → 34; CAR on CGY) / 2 wrong (CBJ on MIN 29.5 → 14; CGY on CAR 22.3 → 34). Owner's bets/fades leaning on H2H: Wallstedt fade Oct 12 ✅, Daws ✅ vs Skinner ❌, Dostal ❌, Wallstedt o23.5 Oct 18 ❌ → **2 right / 3 wrong**.
  - Oct 19: H2H disagreed with two UNDER tags in ANA@NYR — **right both**: Garand (ANA on NYR avg 29.5 → 31) and Husso (NYR on ANA avg 27.8 → 30). Woll's H2H (COL on PHI 31.0) agreed with his 🔥 OVER and was wrong (26). **Running when H2H disagrees: 9 right / 4 wrong (13).** Since Oct 17: 6-0. Close to a testable sample (~15–20).
  - Oct 20: one disagreement, **wrong**: Wedgewood LEAN OVER (NJD on COL avg 25.5) → NJD shot 41. H2H agreed and was wrong on Grubauer OVER (DET on SEA 33.0 → 25); agreed and right on Oettinger UNDER (BOS on DAL 23.5 → 20) and Nedeljkovic (MTL on SJS 29.0 → 34). **Running when H2H disagrees: 9 right / 5 wrong (14).** Owner's H2H-based calls: Allen u27.5 ("H2H in NJ mid 20s" — true for the 2 games at NJ, 24 and 24, but full L4 avg was 31.8) → COL shot 34, ❌ → **2 right / 4 wrong**.
  - Oct 21: one disagreement, **wrong**: Vladar OVER (BUF on PHI avg 25.8, below league 27.2) → BUF shot 28, over won. Agreed and wrong: Schmid UNDER (OTT on FLA 24.8 → 30). Borderline, not counted: Luukkonen (PHI on BUF 27.0 ≈ league → 26). **Running when H2H disagrees: 9 right / 6 wrong (15)** — now at testable size; 6-0 run since Oct 17 has cooled to 6-2. Worth a proper look in the Oct 28 review.
  - Oct 22: three disagreements — right on DiPietro UNDER (NSH on BOS avg 32.8 → 28 vs 24.2 exp); wrong on Daws UNDER (ANA on NJD 28.0 → 17) and Bobrovsky UNDER (NYR on TOR 31.5 → 25). Agreed and wrong: Wallstedt 🔥 OVER (CGY on MIN 32.3 → 22), Husso OVER (NJD on ANA 30.8 → 29 vs 32.8). **Running when H2H disagrees: 10 right / 8 wrong (18)** — 6-0 run is now 7-4 since Oct 17; looks like a coin flip. Owner's H2H call on Grubauer ✅ (UTA on SEA avg 34.0 → 36) → owner's H2H calls **3 right / 4 wrong**.
  - Oct 23: no disagreement case. Agreed and wrong: Vasilevskiy LEAN OVER (COL on TBL avg 31.5 → only 24). Running stays **10 right / 8 wrong (18)**.
  - Oct 24: three disagreements — right on Hart OVER (CBJ on VGK avg 26.5 → 20); wrong on Lindgren UNDER (BUF on WSH 29.0 → 21) and Saros OVER (PIT on NSH 23.8 → 37). Agreed and wrong: Jarry UNDER (26.2 → TOR 31), Silovs UNDER (25.5 → 26), Vejmelka UNDER (26.0 → 32). Borderline, not counted: Woll (27.2), Forsberg (27.2). **Running when H2H disagrees: 11 right / 10 wrong (21)** — a coin flip at testable size. Owner's H2H call on Hofer ✅ (CAR on STL avg 32.2 → 39) → owner's H2H calls **4 right / 4 wrong**.
  - Oct 25: one disagreement, **wrong**: Oettinger UNDER (NYI on DAL avg 29.5) → NYI shot 20. On NO EDGE goalies H2H badly missed COL on NSH (avg 38.0 → 21). **Running when H2H disagrees: 11 right / 11 wrong (22).**
  - Oct 26: no disagreement case (Bobrovsky OVER, CGY on TOR avg 27.8 ≈ league — borderline, CGY shot 34). On NO EDGE goalies: DET on EDM 28.5 → 29 (right), EDM on DET 32.0 → 28 (miss), LAK on NYR 29.5 → 26 (miss; owner went against it and was right). Running stays **11 / 11 (22)**.
  - Oct 27: two disagreements — **right both**: Saros UNDER (NYI on NSH avg 29.5 → 28) and Ellis OVER (SJS on BUF 26.0 → 23). Borderline, not counted: Dostal LEAN UNDER (VAN on ANA 27.5 ≈ league → 33). Agreed and wrong: Merilainen FD LEAN OVER (ANA on VAN 33.8 → 23). **Running when H2H disagrees: 13 right / 11 wrong (24).**
  - Oct 28: two disagreements — **right both**: Woll OVER (WSH on PHI avg 24.5 → 30, under the ~31 the line needed) and Bobrovsky OVER (SEA on TOR 25.5 → 17). Agreed and wrong: Blackwood OVER (NJD on COL 29.5 → 22). Agreed and right on volume: Cooley LEAN OVER (EDM on CGY 36.0 → 32). On NO EDGE Grubauer, TOR on SEA avg 30.3 → 21 (miss; owner bet the over). **Running when H2H disagrees: 15 right / 11 wrong (26)** — 4-0 the last two nights.
  - Oct 29: one disagreement, **right**: Wallstedt UNDER (NYI on MIN avg 29.0) → NYI shot 26 vs 23.8 exp, under lost. H2H **agreed and was wrong on six**: Kochetkov UNDER (CBJ on CAR 22.3 → 26), and five road OVERs — Sorokin (MIN on NYI 30.8 → 25), Swayman (STL on BOS 29.5 → 18), Greaves (CAR on CBJ 28.8 → 27), Merilainen (SJS on VAN 31.5 → 24), Dobes (DAL on MTL 28.8 → 19). **Running when H2H disagrees: 16 right / 11 wrong (27).** H2H agreeing with a tag isn't protecting it.
  - Oct 30: no disagreement case. Agreed and wrong on both road OVERs again: Hellebuyck (VGK on NJD avg 31.5 → 21) and Grubauer (CGY on SEA 31.8 → 27). H2H that agrees with an OVER tag is now 0-7 over the last two nights. Running stays **16 / 11 (27)**.
- **Home team "tight at home" in L5 shots against** (3 games, 3 support; Oct 15: owner took Daws u21.5 because NJD tight at home → NYR shot 19). Owner noted MIN allowing mid-20s at home in L5 (Oct 12, Wallstedt). Oct 13: owner faded Skinner (WPG) OVER 25.5 because WPG played tight at home last game → MIN shot 21. Test idea: home/road split of the last 5 vs. the season blend.
  - Oct 18 (support): MIN at home again held a visitor low — CBJ shot 14 (exp 27.1). Owner bet the over this time. Running: 4 support.
  - Oct 20 (against): owner took Allen u27.5 partly because "home in NJ" → COL shot 34 (exp 28.0). Running: 4 support, 1 against.
  - Oct 22 (against): owner's Lankinen u27.5 partly on "VAN at home" → DET shot 31 (exp 28.3), its most in 6 games; under won only on 5 goals. Running: 4 support, 2 against.
  - Oct 23 (against, road-side version): owner's Blackwood u24.5 on "TBL on road" — TBL's road games in L5 were low (26, 26, 21) but TBL shot 34 (exp 25.4) while trailing all game. Running: 4 support, 3 against. His last two "low on the road" calls (Lankinen, Blackwood) both saw the road team beat expected.
  - Oct 24 (related, not counted — a "high on the road" call): owner's Hofer o26.5 on "CAR has been shooting on the road except EDM" (CAR road L5: 37, 36, 44, 27 at EDM) → CAR shot 39. His road-volume calls: high ✅1, low ❌2.
  - Oct 26 (slight support): owner's Reimer u25.5 on "home and Kings shooting less" → LAK shot 26 at NYR (exp 26.3; LAK L5 for 26.4 incl. 13 at NJD; Fiala out). Running: 4 support + 1 slight, 3 against.
  - Oct 27 (support, road-low version): owner's Vladar u25.5 on "CBJ doesn't shoot on the road" (CBJ road games 23 @STL, 14 @MIN) + "PHI allowing mid 20s" (PHI L5 against 26.4) → CBJ shot 15 (exp 27.6). Running: 5 support + 1 slight, 3 against. His road-volume calls: high ✅1, low ✅1 ❌2.
- **Unders outperforming overs early** (season to Oct 12: OVER 6-6, UNDER 12-5; NO EDGE 62% under). Covered by the Oct 14 accuracy analysis.
  - Oct 13 mixed: OVER 2-3, UNDER 2-2, LEAN UNDER 0-2; NO EDGE 5 over / 12 under (71% under) — the under lean on lines keeps showing up even when the model's tags miss.
  - Oct 14: UNDER 1-0; NO EDGE 1 over / 2 under (Dobes 18 vs 25.5, DeSmith 25 vs 26.5; Lindgren 26 vs 23.5 over).
  - Oct 15 (contradicts): NO EDGE went 8 over / 4 under (one of the unders, Garand, was likely a pull). OVER 4-1, UNDER 3-0.
  - Oct 16: NO EDGE 1 over / 2 under (Blackwood 29 vs 23.5; Dostal 18 vs 21.5; DiPietro 25 vs 27.5). LEAN OVER 0-1.
  - Oct 17 (contradicts strongly): NO EDGE **12 over / 3 under** (unders: Allen, Bobrovsky, Binnington). OVER 3-3, UNDER 2-3, LEAN UNDER 1-0. Two straight big nights (Oct 15, 17) leaning over on NO EDGE — the early under lean may have been small-sample.
  - Oct 18: NO EDGE 2 over / 1 under (Talbot 32 vs 27.5, Bussi 31 vs 21.5; Wallstedt 13 vs 23.5). OVER 1-0.
  - Oct 19: NO EDGE 1 over / 2 under (Bobrovsky 30 vs 24.5/25.5; Silovs 24 vs 25.5, Cossa 15 vs 22.5/23.5). OVER 1-1, UNDER 1-2.
  - Oct 21: OVER 1-0, UNDER 0-2 (both 🔥, both lost by half a save on volume above expected). NO EDGE 0 over / 1 under (Ullmark 17 vs 23.5/24.5). Model UNDER tags since Oct 17: 4-7.
  - Oct 22: OVER 0-2 (one 🔥), UNDER 2-1, LEAN UNDER 1-0. NO EDGE **11 over / 5 under** (Askarov 41 vs 25.5, Kuemper 41 vs 23.5, Skinner 35 vs 23.5, Cooley 36 vs 26.5 way over). Model UNDER tags since Oct 17: 6-8. All four UNDER tags were home goalies (the new ±1.5 nudge favors those): 3-1.
  - Oct 23: LEAN OVER 0-1. NO EDGE 1 over / 2 under (Blackwood 31 vs 24.5 DK / 23.5 FD over; Fowler 20 vs 21.5, Knight 24 vs 26.5 under).
  - Oct 24 (contradicts): OVER 2-2, LEAN OVER 2-0, UNDER 2-3. NO EDGE 6 over / 4 under (Hofer 35 vs 26.5, Daccord 31 vs 26.5 over; Allen 12 vs 23.5, Garand 17 vs 25.5 under). Model UNDER tags since Oct 17: **8-11**. 4 of the 5 UNDER tags were home goalies (2-2).
  - Oct 25: UNDER 1-0 (Oettinger). NO EDGE 5 over / 4 under (Sorokin 32 vs 22.5, Wedgewood 29 vs 20.5, Fowler 33 vs 23.5 way over; Annunen 19 vs 29.5, Skinner 19 vs 25.5 way under). Model UNDER tags since Oct 17: **9-11**.
  - Oct 27 (11 games): UNDER 1-0 (Saros DK, lucky; FD 24.5 lost), LEAN UNDER 0-1, OVER 0-1. NO EDGE **6 over / 10 under** by first line (Fowler 46 vs 26.5, Askarov 38 vs 26.5 way over; Vladar 11 vs 25.5, Binnington 18 vs 24.5, Kochetkov 14 vs 19.5, Merilainen 18 vs 28.5 way under). Model UNDER tags since Oct 17: **10-11**.
- Oct 26 (3 games): OVER 1-0 (Bobrovsky). NO EDGE 1 over / 4 under by first line (Kuemper 23 vs 21.5 over; Cooley 26 vs 26.5, Jarry 26 vs 26.5, Postava 25 vs 25.5 under by half a save, Reimer 5 vs 25.5 — left early). Three of the four unders were half-save finishes; FD's line was a save lower on Cooley and Jarry and went over at FD.
- Oct 28 (4 games): OVER 0-3, LEAN OVER 0-1 (model 0-4). NO EDGE 3 over / 1 under by first line (Allen 39 vs 26.5 way over; Grubauer 17 vs 25.5 way under). Model OVER tags this week: 0-4 (Ellis Oct 27 + Blackwood, Woll, Bobrovsky).
- Oct 29 (11 games): OVER 1-6, UNDER 1-2, LEAN UNDER 1-0 (model 3-8). NO EDGE 5 over / 5 under by first line (Hofer 31 vs 23.5, Cossa 31 vs 23.5, Ellis 29 vs 24.5 way over; Kuemper 17 vs 24.5, Vasilevskiy 17 vs 22.5 way under). Model UNDER tags since Oct 17: **11-13**. Model OVER tags since Oct 27: **1-10**.
- Oct 30 (3 games): OVER 0-2 (both road, both wrong on volume). NO EDGE 1 over / 2 under by first line (Wolf 20 vs 26.5 way under). Model OVER tags since Oct 27: **1-12**.
- **Thin cushion (line within ~1 save of expected)** (from the Oct 13 takeaway; Oct 14 analysis had gap <1 save at 2-5 for Oct 7–13). Since then: Oct 15 Daws ✅, Grubauer ✅, Wolf ✅; Oct 16 Silovs 😬 (28.0 vs 28.5, volume on target, lost on save%). Oct 17: Markstrom 21.5 vs 21.8 ✅, Oettinger 20.5 vs 20.2 ✅, Ullmark 21.5 vs 20.6 ❌, Forsberg 22.5 vs 22.1 ❌. Running since Oct 15: 5-3. Oct 18: Cooley 27.5 vs 27.7 ✅ (CAR 36 shots). **Running: 6-3.** Oct 19: Askarov 25.5 vs 25.9 ✅ (TOR 32 shots). **Running: 7-3.** Oct 20: Wedgewood 27.5 vs 26.9 ✅ (NJD 41), Nedeljkovic 27.5 vs 26.9 ✅ (MTL 34). **Running: 9-3.** Oct 22: Oettinger 20.5 vs 21.0 ✅ (WPG 19). **Running: 10-3.** Oct 23: Vasilevskiy LEAN OVER 27.5 vs 27.0 ❌ (COL 24). **Running: 10-4.** Oct 24: Luukkonen LEAN OVER 26.5 vs 26.0 ✅ (WSH 34), Stolarz LEAN OVER 27.5 vs 26.8 ✅ (EDM 32); borderline not counted: Silovs UNDER 22.5 vs 21.4 ❌. **Running: 12-4.** Oct 27: Dostal LEAN UNDER 21.5 vs 21.5 ❌ (VAN 33). **Running: 12-5.** Oct 28: Woll OVER 27.5 vs 27.6 ❌ (WSH 30, ~31 needed), Cooley LEAN OVER 27.5 vs 26.8 😬 (EDM 32 — volume right, he left early with 8 saves). **Running: 12-7** (last four 0-4). Test: record by gap bucket once ~15–20 thin-gap tags. Oct 29: Kochetkov UNDER 20.5 vs 19.8 ❌ (CBJ 26), Wallstedt UNDER 21.5 vs 21.1 ❌ (NYI 26, lost by half a save), Gibson LEAN UNDER 21.5 vs 21.9 ✅ (CHI 19). **Running: 13-9** (6 losses in the last 8).
- **Key defenseman out → more shots against** (new, from owner's notes Oct 13; 4 games: 2 support, 1 slight, 1 against). Dahlin out (BUF): MTL shot 38 vs 24.1 expected — owner faded the 🔥 UNDER for this reason. Roy out (WSH): CAR shot 35 vs 27.6. Makar out (COL, late): DAL 26 vs 24.6. Against: Matheson out (MTL): BUF shot only 17 vs 27.3. Oct 14 (5th game, support): Roy still out (WSH) → MTL shot 30 vs 27.3 expected. Oct 15 (5 more: 2 support, 3 against): Morrissey out (WPG) → CHI 28 vs 25.7; Byram out (CHI) → WPG 34 vs 27.7; against: Sanderson out (OTT) → NYI 21 vs 25.8; York out (PHI) → DET 26 vs 33.2; Faber out (MIN) → STL 25 vs 26.2 (slight). **Running: 10 games, 5 support, 1 slight support, 4 against (1 slight)** — weaker than it looked. Oct 17 (6 more: 4 support, 2 slight against): Morrissey out (WPG) → CAR 37 vs 28.9 exp; Dahlin out (BUF) → MTL 34 vs 28.3; Sanderson out (OTT) → PHI 28 vs 23.3; Byram (CHI, listed out/DTD) → DAL 32 vs 26.8; slight against: York out (PHI) → OTT 26 vs 27.1; Roy out (WSH) → NJD 31 vs 32.6. **Running: 16 games, 9 support, 1 slight support, 6 against (3 slight)** — near the ~15–20 needed; worth a proper test soon. Oct 18 (against): Faber out (MIN) → CBJ shot only 14 vs 27.1 exp. **Running: 17 games, 9 support, 1 slight support, 7 against (3 slight).** Oct 19 (against): York out (PHI) → COL shot 26 vs 31.6 exp. **Running: 18 games, 9 support, 1 slight support, 8 against (3 slight)** — at the size to test properly. Oct 20 (3 more): Faber out (MIN) → EDM 32 vs 25.1 exp (support); Morrissey out (WPG) → STL 28 vs 28.0 (neutral); Roy out (WSH) → LAK 26 vs 29.2 (against). **Running: 21 games, 10 support, 1 slight support, 1 neutral, 9 against (3 slight).** Oct 21 (2 against): Chabot out (OTT) → FLA shot only 19 vs 27.6 exp; York out (PHI) → BUF 28 vs 30.3 (slight). **Running: 23 games, 10 support, 1 slight support, 1 neutral, 11 against (4 slight)** — now a coin flip; no sign of an edge yet. Oct 22: Morrissey out (WPG) → DAL shot 38 vs 29.0 exp (support); Faber out (MIN) → CGY only 22 vs 30.2 (against). **Running: 25 games, 11 support, 1 slight support, 1 neutral, 12 against (4 slight).** Oct 24: York out (PHI) → ANA 26 vs 24.6 exp (slight support); Faber out (MIN) → SEA only 24 vs 28.2 (against; Faber now 1 support / 3 against). (Chabot out for OTT — no OTT goalie alerted, no expected to compare.) **Running: 27 games, 11 support, 2 slight support, 1 neutral, 13 against (4 slight).** Oct 25: Byram out (CHI) → FLA 33 vs 26.6 exp (support); Morrissey out (WPG) → MTL only 21 vs 26.3 (against); Faber out (MIN) → VAN 17 vs 25.2 (against; Faber now 1 support / 4 against). **Running: 30 games, 12 support, 2 slight support, 1 neutral, 15 against (4 slight)** — leaning against. Oct 27 (2 against): Morrissey out (WPG) → FLA 24 vs 26.7 exp; Faber out (MIN) → UTA 27 vs 29.2 (Faber now 1 support / 5 against). (York back for PHI; Chabot out for OTT — no OTT goalie alerted.) **Running: 32 games, 12 support, 2 slight support, 1 neutral, 17 against (5 slight).** Test: picks.csv `key_out` already logs this (injury stage 2) — compare team shots against vs expected with/without a key D out once ~15–20 games have one. Oct 29 (3): Faber out (MIN) → NYI 26 vs 23.8 exp (support; Faber now 2 support / 5 against); Morrissey out (WPG) → TBL 31 vs 32.6 (slight against; Skinner pulled); Byram out (CHI) → DET 31 vs 30.4 (neutral). **Running: 35 games, 13 support, 2 slight support, 2 neutral, 18 against (6 slight).**
- **Key shooter out → fewer shots for** (new, 1 game; this is injury stage 3's idea). Oct 14: Johnston out (DAL) → DAL shot 22 on COL vs 24.9 expected (H2H also low, so not clean evidence). Oct 15: Sanderson out (OTT) → OTT shot 19 on NYI vs 22.9 exp (support); Hyman out (EDM) → EDM 24 vs 23.1 (neutral); Marchand out (FLA) → FLA 39 vs 30.7 (against). Running 4 games: 2 support, 1 neutral, 1 against. Oct 17: Konecny out (PHI) → PHI 28 vs 23.3 (against); Marchand out (FLA) → FLA 37 vs 30.8 (against); Sanderson out (OTT) → OTT 26 vs 27.1 (slight support). **Running 7: 2 support + 1 slight, 1 neutral, 3 against.** Oct 19: Konecny out + Tippett (PHI) → PHI 24 vs 23.2 exp (neutral). **Running 8: 2 support + 1 slight, 2 neutral, 3 against.** Oct 20: Fiala out (LAK) → LAK 26 on WSH vs 29.2 exp (support). **Running 9: 3 support + 1 slight, 2 neutral, 3 against.** Oct 21: Konecny + Tippett out (PHI) → PHI shot 26 on BUF vs 22.0 exp (against). **Running 10: 3 support + 1 slight, 2 neutral, 4 against.** Oct 22: Backlund out (CGY) → CGY shot 22 on MIN vs 30.2 exp (support — the only thing in our data that warned on Wallstedt's 🔥 OVER); Fiala out (LAK) → LAK 27 vs 26.5 (neutral); Marchand out (FLA) → FLA 26 vs 25.9 (neutral). **Running 13: 4 support + 1 slight, 4 neutral, 4 against.** Oct 23: Suzuki out (MTL) → MTL shot 28 on CHI vs 28.0 exp (neutral). **Running 14: 4 support + 1 slight, 5 neutral, 4 against.** (Dahlin was listed DTD but played — hat trick — so BUF isn't a case.) Oct 24 (5 more: 3 support, 2 against): Fiala out (LAK) → LAK shot only 13 on NJD vs 26.2 exp; Backlund out (CGY) → CGY 25 vs 28.8; McCann out (SEA) → SEA 24 vs 28.2; against: Konecny + Tippett out (PHI) → PHI 32 vs 25.7; Malkin + Rust out (PIT) → PIT 37 vs 29.9. **Running 19: 7 support + 1 slight, 5 neutral, 6 against** — now at testable size; leaning slightly toward support. Oct 25: Suzuki out (MTL) → MTL shot 21 on WPG vs 26.3 exp (support); Marchand out (FLA) → FLA 33 on CHI vs 26.6 (against; Marchand now 0 support / 3 against + 1 neutral). **Running 21: 8 support + 1 slight, 5 neutral, 7 against.** Oct 26: Fiala out (LAK) → LAK shot 26 on NYR vs 26.3 exp (neutral; Fiala now 2 support / 2 neutral). **Running 22: 8 support + 1 slight, 6 neutral, 7 against.** Oct 27 (2 support): Fiala out (LAK) → LAK shot 26 on CHI vs 28.5 exp; Suzuki out (MTL) → MTL shot 20 on STL vs 27.2. (Konecny + Tippett out for PHI — CBJ goalie not alerted, no expected.) **Running 24: 10 support + 1 slight, 6 neutral, 7 against.** Oct 28 (3): McCann out (SEA) → SEA shot 17 on TOR vs 31.1 exp (support); Konecny + Tippett out (PHI) → PHI 25 on WSH vs 24.8 (neutral); Hyman out (EDM) → EDM 32 on CGY vs 30.2 (against; owner's under reason). **Running 27: 11 support + 1 slight, 7 neutral, 8 against.** Test with picks.csv `key_out` (forwards) once ~15–20 games. Oct 29 (4): Rust out (PIT, Malkin DTD) → PIT shot 34 on UTA vs 27.7 exp (against); Terry out (ANA) → ANA 35 on BUF vs 27.4 (against; owner's under reason); Suzuki out (MTL) → MTL 21 on DAL vs 22.9 (slight support); Larkin out (DET) → DET 31 on CHI vs 30.4 (neutral). **Running 31: 11 support + 2 slight, 8 neutral, 10 against.** Oct 30: McCann out (SEA) → SEA shot 22 on CGY vs 28.2 exp (support; owner's under reason; McCann now 3 support / 0 against: 24, 17, 22). **Running 32: 12 support + 2 slight, 8 neutral, 10 against.**

- **Score effects / underdog chasing in the 3rd** (new, from owner's note Oct 20; 1 game). Owner was winning Allen u27.5 until COL shot ~20 in the 3rd (his count); NJD won the game (4 goals on Wedgewood vs COL's 3 on Allen), so COL was likely trailing late (guess — period shots and moneyline not confirmed). Test idea: do road underdogs / teams that trail after 2 beat their expected shots? Needs pregame moneylines, which the bot doesn't log yet (ties to the "game script/moneyline" idea). Don't judge before ~15–20 games with odds logged.
  - Oct 22 (guess, the mirror case): NJD beat ANA comfortably (Daws 16 saves on 17, Husso 4 GA) and shot only 29 vs 32.8 exp — a leading team easing off may have sunk Husso's OVER. Score by period not checked.
  - Oct 23 (support, both sides, confirmed by recap): COL led TBL the whole game (won 6-3, empty-netter). Trailing TBL shot 34 vs 25.4 exp (sank owner's Blackwood under); leading COL shot only 24 vs 30.5 (sank Vasilevskiy LEAN OVER). Running: 3 games pointing the same way (Oct 20, Oct 22 guess, Oct 23). Still needs pregame moneylines logged to test.
  - Oct 24 (mixed, from goals against in our data; score not confirmed): NJD led LAK (3 goals on Forsberg vs 1 on Allen) and shot only 26 vs 34.4 exp (leader eased — sank 🎯 Forsberg OVER), but trailing LAK shot just 13 vs 26.2 (no chase; Fiala out). Running: 3 support, 1 mixed.
  - Oct 25 (mostly against; goals from our data, ENGs included, score not confirmed): MTL led WPG 2-1 and shot 21 vs 26.3 exp while WPG shot 34 vs 27.3 (support). But trailing teams didn't chase in three games: COL down 2-6 at NSH shot 21 (exp 28.0); VAN down 2-4 to MIN shot 17 (exp 25.2); CHI down 2-3 to FLA shot 21 (exp 25.3); and leading DAL (6-3) still shot 38. **Running: 4 support, 3 against, 2 mixed** — not holding up without moneylines.
  - Oct 27 (from goals in our data, score not confirmed): MTL won at STL with Fowler stopping all 46 — trailing STL shot 46 (exp 28.7) and leading MTL only 20 (support). But BUF beat SJS (Ellis shutout) and the trailing Sharks shot just 23 vs 30.6 exp while leading BUF shot 40 (against). **Running: 5 support, 4 against, 2 mixed.**
  - Oct 28 (goals from our data, score not confirmed): no chasing anywhere. COL beat NJD (5 on Allen, 2 on Blackwood) and outshot them 44-22; EDM shut out CGY and outshot them 32-24; SEA beat TOR (5 GA on Bobrovsky vs 4) and trailing TOR shot only 21 vs 28.6 exp. PHI–WSH neutral. **Running: 5 support, 7 against, 2 mixed.**
  - Oct 29 (goals from our data, score not confirmed): STL led BOS (4 GA on Swayman vs 1) and shot only 18 while BOS shot 32 (support). Against: MTL beat DAL (5 GA on Oettinger) and shot 21, trailing DAL only 19; DET led CHI and outshot them 31-19; trailing WPG (Skinner pulled) shot 21 vs TBL's 31. **Running: 6 support, 10 against, 2 mixed.**
  - Oct 30 (goals from our data, score not confirmed): no chasing. NJD led VGK (5 GA on Hill vs 2 on Hellebuyck) and still shot 32, trailing VGK only 21; CGY led SEA (Grubauer left after 10 saves, Wolf allowed 2) and trailing SEA shot 22 vs 28.2 exp. **Running: 6 support, 12 against, 2 mixed.**

- **NO EDGE with a big gap (line 3+ saves from expected, lean just under the 2-shot bar)** (owner asked Oct 21 about Wallstedt: line 27.5 vs 22.3 exp, delta −1.87 shots → NO EDGE; EDM shot 32, 28 saves, so an under would have lost — owner glad it didn't tag). Line 3+ above expected so far: 3 under / 2 over (Garand, Wolf, Dostal under; Merilainen Oct 13, Wallstedt over). Oct 22: Hofer 25.5 vs 22.5 → 27 (over). **Running 3 under / 3 over.** Oct 25: Knight 27.5 vs 23.6 → 30 (over); Annunen 29.5 vs 24.8 → 19 (under). **Running 4 under / 4 over.** Oct 26: Jarry 26.5 DK vs 23.3 → 26 (under by half a save; DET 29 shots, above exp 26.3; FD 25.5 went over). **Running 5 under / 4 over.** Mirror (line 3+ *below* expected, NO EDGE): Wedgewood 20.5 FD vs 25.0 → 29 (over); Oct 26 Kuemper 21.5 FD / 22.5 DK vs 25.2 → 23 (over). **Mirror 2 over / 0 under.** Oct 27: Forsberg 21.5 FD vs 24.5 → 25 (over; owner took the DK u22.5 and lost). **Mirror 3 over / 0 under.** No line 3+ above expected. Covered by shadow A (bar 1.5) in the Oct 28 review; no change proposed.

- **Road-goalie OVER tags losing on volume** (new Oct 29; 10 games, all against the tag). Since Oct 27 every OVER/LEAN OVER on a road goalie lost: Ellis Oct 27; Woll, Bobrovsky, Cooley (😬) Oct 28; Skinner (😬 pull), Sorokin, Swayman, Greaves, Merilainen, Dobes Oct 29 → **0-10** (8 wrong on volume). Oct 29 road goalies faced −3.1 shots vs the live number (−1.6 vs the old model), home goalies +0.1 — so the +1.5 road nudge was wrong-way on this night. Oct 14–27 the road surplus was +1.5 (n=88). Could be a cold spell after a hot one; test at the mid-Nov home/road re-check: road surplus by week, and road-goalie OVER tags vs the old model's tags on the same games. Not enough to change anything (owner's rule).
  - Oct 30: two more, both wrong on volume — Hellebuyck 🔥 OVER (VGK 21 vs 30.3 exp; nudge-made, A and B NO EDGE) and Grubauer 🎯 OVER (CGY 27 vs 31.4; left early). **0-12** (10 wrong on volume). Road goalies faced −6.9 shots vs live on average (n=2), home −2.0 (n=3) — a low-volume night overall. Ties to the owner's Oct 30 theory (OVER tags run ~2 saves too high): both lines went under.

## Owner's reads (his reasoning on bets/fades)
- 2026-10-12 · Wallstedt (MIN) vs VGK · model LEAN OVER o26.5 · **owner faded**: H2H VGK shots on MIN low; MIN tighter at home in L5 (mid-20s). Result 21 saves → fade correct.

- 2026-10-13 · Vladar (PHI) vs SEA · model OVER o23.5 · **owner faded**: SEA on the road shoots mid-20s. SEA shot 31, 29 saves → fade wrong, model right.
- 2026-10-13 · Skinner (WPG) vs MIN · model OVER o25.5 · **owner faded**: WPG played tight at home last game. MIN shot 21, 19 saves → fade right.
- 2026-10-13 · Oettinger (DAL) vs COL · NO EDGE 24.5 · **owner took o24.5**: COL shoots, DAL faced weaker teams. COL shot 25, 22 saves → lost, read wrong (volume ~average).
- 2026-10-13 · Thompson (WSH) @ CAR · NO EDGE 26.5 · **owner took o26.5**: CAR shoots, WSH allowed less vs weak teams, top D (Roy) out. CAR shot 35, 31 saves → won, read right; all three reasons showed up.
- 2026-10-13 · Luukkonen (BUF) @ MTL · model 🔥 UNDER u24.5 · **owner faded**: Dahlin out. MTL shot 38, 35 saves → fade right; beat the model's 🔥.

- 2026-10-14 · Wedgewood (COL) vs DAL · model UNDER u22.5 · **owner took u22.5** (no note). DAL shot 22, 20 saves → won, read right on volume.
- 2026-10-14 · DeSmith (DAL) @ COL · NO EDGE 26.5 · **owner took o26.5** (no note). COL shot 27 (≈ expected 27.9; line needed ~30), 25 saves → lost, read wrong on volume. Shadow B also leaned over (25.6) and missed.

- 2026-10-15 · Skinner (WPG) @ CHI · NO EDGE 23.5 · **owner took u23.5**: "CHI doesn't shoot at all and good H2H" (CHI on WPG avg 22). CHI shot 28 (exp 25.7), 24 saves → lost, read wrong on volume. Morrissey (WPG D) went OUT after he bet (DTD at the time; the ⚠️ alert came later) — so not a judgment miss; guess: it helped CHI. Led to the "your bet" line on injury alerts (Oct 16).
- 2026-10-15 · Bobrovsky (TOR) vs BUF · NO EDGE 25.5 DK / 26.5 FD · **owner took u26.5**: "Dahlin out so less BUF SOG". Dahlin played (hat trick, BUF won 7-4); BUF shot 34, 29 saves → lost, the reason didn't happen. H2H (BUF on TOR avg 30) pointed over.
- 2026-10-15 · Daws (NJD) vs NYR · model UNDER u21.5 FD (LEAN UNDER 20.5 DK) · **owner took u21.5**: "NJ tight at home, H2H good" (NYR on NJD avg 21.8). NYR shot 19, 18 saves → won, read right; both reasons showed up.
- Also followed the model (no note): Merilainen o26.5 W, Varlamov u25.5 W, Wolf o26.5 W, Grubauer o26.5 W, Levi o23.5 L, Woll o24.5 L (DK alerted 23.5, moved to 24.5 by the time he bet; 24 saves).

- 2026-10-16 · Dostal (ANA) vs BOS · NO EDGE 21.5 DK / 23.5 FD · **owner took o21.5**: "h2h history looks good and BOS taking shots" (told in chat; the bot dropped it, fixed Oct 16). BOS shot 22 (exp 26.3), 18 saves → lost, read wrong on volume. H2H (BOS on ANA avg 34.0) didn't show; BOS L5 for was only 25.2 (about average).

- 2026-10-17 · Markstrom (FLA) vs SEA · model LEAN UNDER 21.5 DK / UNDER 22.5 FD · note "this and FD 22u" (bet, no reasoning). SEA shot 23, 20 saves → won, right on volume. Only FD u22.5 is logged; the DK u21.5 he seems to have meant wasn't picked up.
- Also took (no note): Allen u25.5 NO EDGE W (WSH 25 shots — right), Thompson o25.5 W, Oettinger u20.5 W, Vejmelka u24.5 W, Greaves u22.5 L, Nedeljkovic o25.5 L, Ullmark u21.5 L, Murashov o26.5 L, Demko o25.5 void (Lankinen started). 5-4.

- 2026-10-18 · Wallstedt (MIN) vs CBJ · NO EDGE 23.5 DK / 22.5 FD · **owner took o23.5**: "High shots in Min from h2h history" (CBJ on MIN avg 29.5). CBJ shot 14 (exp 27.1), 13 saves → lost, read wrong on volume; the H2H didn't show. Model's NO EDGE was the better call.

- 2026-10-19 · no notes. Followed the model on Woll 🔥 o25.5 L (COL 26 shots vs 31.6 exp), Garand u24.5 L (ANA 31 vs 22.4), Husso u24.5 FD L (NYR 30 vs 24.4); took NO EDGE Cossa u24.5 W (PIT 19 vs 25.1 — right on volume). 1-3; his only off-model bet was the winner.

- 2026-10-20 · Allen (NJD) vs COL · NO EDGE 27.5 FD / 26.5 DK · **owner took u27.5**: "home in NJ, Col lately lower on shots and h2h in NJ shows mid 20s". COL shot 34 (exp 28.0), 31 saves → lost, read wrong on volume. COL's L5 for was 28.6 (about average, not low); H2H at NJ was 24/24 but full L4 31.8. After: "was tracking then Col shot 20 times in the 3rd. See if they were underdogs to be down" — NJD won (4 goals to COL's 3), so COL likely chased late (guess; moneyline not in our data). Note: his first note ("note on Allen …") was saved with no goalie attached.
- Also (no note): followed the model on Thompson OVER o24.5 L (LAK 26 vs 29.2 exp — wrong), Oettinger 🔥 UNDER u22.5 W (BOS 20 — right), Merilainen LEAN OVER o28.5 W (CAR 44 — right); took NO EDGE Kochetkov u19.5 W (VAN 17 vs 23.3 exp — right). 3-2; right on volume 3 of 5. His 🔥 bets now 9-2.

- 2026-10-21 · no notes. Followed the model on Schmid 🔥 UNDER u24.5 DK (taken ~3h before puck drop) → OTT shot 30 (exp 21.4), 25 saves → lost by half a save, wrong on volume. 0-1; his 🔥 bets now 9-3.

- 2026-10-22 · Lankinen (VAN) vs DET · NO EDGE 27.5 DK / 25.5 FD · **owner took u27.5 DK**: "Van at home and that's a big number for DET on the road". DET shot 31 (exp 28.3; DET L5 for was 27.0), 26 saves → won, but 🍀: volume came in right at what the line needed (~31); won on 5 goals against. He did grab the high number (FD was 25.5).
- 2026-10-22 · Grubauer (SEA) vs UTA · NO EDGE 27.5 DK / 24.5 FD · **owner took o24.5 FD**: "h2h looks good" (UTA on SEA avg 34.0). UTA shot 36 (exp 28.3), 33 saves → won, read right; the H2H showed up. Again took the better book (3 saves lower than DK).
- Also (no note): followed the model on Daws u23.5 W (ANA 17 — right), Oettinger u21.5 W (WPG 19 — right; took it after the line moved up from 20.5), Husso o27.5 L (NJD 29 vs 32.8 — wrong), Wallstedt 🔥 o22.5 L (CGY 22 vs 30.2 — wrong); took NO EDGE Bussi u24.5 FD W (EDM 21 vs 26.7 — right). 5-2; right on volume 4 of 7 (+ Lankinen borderline). His 🔥 bets now 9-4; NO EDGE bets 3-0 tonight.

- 2026-10-23 · Blackwood (COL) vs TBL · NO EDGE 24.5 DK / 23.5 FD · **owner took u24.5 DK**: "Tbl on road and they have had an easy schedule". TBL shot 34 (exp 25.4), 31 saves → lost, read wrong on volume. TBL's recent road games were low (26, 26, 21), so the reason was real, but TBL trailed all game and chased. "Easy schedule" not checked (no opponent-strength data in the review). He took the higher DK number (FD 23.5).
- Also (no note): followed the model on Vasilevskiy LEAN OVER o27.5 DK → COL shot 24 (exp 30.5), 18 saves (5 GA + empty-netter) → lost, wrong on volume. 0-2 on the night.

- 2026-10-24 · Hofer (STL) vs CAR · NO EDGE 26.5 DK · **owner took o26.5**: "car shoots a lot on stl h2h. Car has been shooting on the road except for EDM". CAR shot 39 (exp 28.7), 35 saves → won, read right; both reasons showed (H2H CAR on STL avg 32.2; CAR road L5 37/36/44, 27 at EDM). Shadows A and B both had this as an over.
- Also (no note): Daccord o26.5 DK NO EDGE (🎯 over) W — MIN shot 36 vs 28.3, right. Kochetkov u21.5 DK NO EDGE L — STL shot 24 (exp 27.2), right at what the line needed (~24); lost on a 24-save shutout. Followed the model on Hart OVER o23.5 FD L — CBJ shot 20 vs 30.2, wrong. 2-2; right on volume 2 of 4 (+ Kochetkov a toss-up). All three of his CAR–STL / MIN–SEA reads came from the same idea (big-volume teams), and the over sides won.

- 2026-10-25 · no notes. 4-0, right on volume all 4: Schmid u21.5 DK (model LEAN UNDER at DK, NO EDGE at FD 20.5; CHI 21 shots vs 25.3 exp, 19 saves); Oettinger u21.5 DK with the model UNDER (NYI 20, 17 saves); and two NO EDGE goalies both marked 🎯 — Merilainen o25.5 FD (MIN 34, 30 saves; shadows A and B had it OVER) and Pickard u21.5 DK (alert line 20.5; VAN 15 saves on 17 shots, VAN L5 for 17.4). He picked the two 🎯 that won and skipped the two 🎯 overs that lost (Annunen, Skinner).

- 2026-10-26 · Reimer (NYR) vs LAK · NO EDGE 25.5 DK · **owner took u25.5**: "home and Kings shooting less". LAK shot 26 (exp 26.3; ~29 needed to beat the line), Reimer 5 saves — left early (pull or injury, not confirmed) → won. Right on volume; the pull made it a lock. LAK L5 for 26.4 (13 at NJD last game, Fiala out), so "shooting less" was about average, not low, but volume stayed under the number.
- Also (no note): Bobrovsky 🔥 o25.5 FD with the model OVER → CGY 34, 29 saves, right. Cooley o25.5 FD (NO EDGE; DK 26.5) → TOR 28 (exp 29.2; ~29 needed), 26 saves → won by half a save on a .929 save% — a toss-up, and the FD number was the difference (DK under won). 3-0; both overs on FD's lower line. His 🔥 bets now 10-4.

- 2026-10-27 · Vladar (PHI) vs CBJ · NO EDGE 25.5 DK / 23.5 FD · **owner took u25.5 DK**: "CBJ doesn't shoot on the road and last five phi is allowing mid 20s plus D back". CBJ shot 15 (exp 27.6), 11 saves → won, read right; all three reasons showed (CBJ road games 23 and 14; PHI L5 against 26.4; York came off the injury list between the DK and FD alerts). He took the high DK number.
- 2026-10-27 · Kochetkov (CAR) vs BOS · NO EDGE 19.5 DK/FD (exp 22.0) · **owner took u20.5 FD**: "line moved". BOS shot 15 (exp 24.8), 14 saves → won, right on volume; waiting for the line to move up got him a better number.
- Also (no note): Merilainen u28.5 DK (NO EDGE at DK; FD later LEAN OVER 27.5 with ⚠️ ANA 4th least for) → ANA 23 vs 30.2 exp, 18 saves, won, right — he went against the FD tag and the ⚠️ backed him. DeSmith u24.5 DK (NO EDGE) → NJD 27 vs 27.7 exp (~27.6 needed), 22 saves → won, a toss-up helped by 5 GA. Dostal u21.5 DK with the model LEAN UNDER → VAN 33 (exp 24.2), lost, wrong. Forsberg u22.5 DK (NO EDGE; FD 21.5 was 3 below expected) → CHI 27 (~25.4 needed), 25 saves, lost, wrong. 4-2; right on volume 3 of 6 + DeSmith a toss-up. NO EDGE unders 4-1.

- 2026-10-28 · Woll (PHI) @ WSH · model OVER 27.5 DK/FD (exp 27.6) · **owner took u27.5 DK**: "Philly has been tighter. Plus goals I think it's an under play". WSH shot 30 (exp 31.1; ~31 needed), 25 saves (5 GA) → won. Right on volume, narrowly; "goals" showed. "Tighter" was a bit strong — PHI's L5 against was 24.2 and WSH beat it by ~6. Beat the model's OVER. (The same note was also saved on Cooley.)
- 2026-10-28 · Cooley (CGY) @ EDM · model LEAN OVER 27.5 DK/FD (exp 26.8) · **owner took u27.5 DK**: "Taking the 27u under. Hyman out." (saved as a general note). EDM shot 32 (exp 30.2) without Hyman — the reason didn't show; Cooley left early with 8 saves → won, 🍀.
- Also (no note): Jarry o22.5 DK (NO EDGE, exp 24.1) → CGY 24 shots (exp 27.2; ~25.4 needed), 24-save shutout → won, 🍀 toss-up. Grubauer o25.5 DK (NO EDGE, 🎯 over) → TOR 21 (exp 28.6), 17 saves → lost, wrong. 3-1; right on volume 1 of 4 (Woll, narrow) + two lucky wins.

- 2026-10-29 · Askarov (SJS) vs VAN · NO EDGE 22.5 DK / 21.5 FD (exp 23.9) · **owner took o21.5 FD**: "Coming off good shots against anh and SJ gives up a ton". VAN shot 25 (exp 27.0; ~24.3 needed), 23 saves → won, right on volume (narrowly). Both reasons were real (VAN shot 33 at ANA last game; SJS L5 against 36.8), though VAN landed in the mid-20s, not high. Took the lower FD number (DK 22.5 also went over).
- 2026-10-29 · Ellis (BUF) @ ANA · NO EDGE 24.5 DK/FD (exp 24.3) · **owner took u24.5**: "terry injured". ANA shot 35 (exp 27.4), 29 saves → lost, wrong on volume; the reason didn't show (ANA beat its L5 for of 22.8 by 12 without Terry). Bet 1.5h before puck drop.
- Also (no note): followed the model on Silovs 🔥 o23.5 FD W (UTA 34 — right), Skinner 🔥 o25.5 DK L (TBL 31 — volume right, pulled with 16 saves), Kochetkov u20.5 L (CBJ 26 vs 22.4 — wrong), Greaves o26.5 L (CAR 27 vs 31.3 — wrong). Knight u28.5 DK (NO EDGE at DK, 🎯 over; FD LEAN OVER 27.5) → DET 31 (~32 needed), 27 saves → won, right narrowly — he went against the 🎯 and the FD tag and was right. 3-4; right on volume 3 of 7 + Skinner. His 🔥 bets now 11-5.

- 2026-10-30 · Wolf (CGY) vs SEA · NO EDGE 26.5 DK / 25.5 FD (exp 25.0) · **owner took u26.5 DK**: "McCann injury". SEA shot 22 (exp 28.2), 20 saves → won, read right; the reason showed (SEA without McCann has shot 24, 17, 22). Took the higher DK number (FD 25.5 also went under).
- Also (no note): followed the model on Hellebuyck 🔥 OVER o22.5 FD (bet ~5h before puck drop; FD moved to 23.5 later) → VGK shot 21 vs 30.3 exp, 19 saves → lost, wrong on volume. 1-1; right on volume 1 of 2. His 🔥 bets now 11-6; his off-model NO EDGE read beat the model's tag again.

## Weekly: where your losses are
### 2026-10-25 (61 goalies logged Oct 10–24, each once; week Oct 19–24 alone 11-12)
- Overs 13-16 (45%) · unders 21-11 (66%). Week: overs 4-6, unders 7-6 — the under edge shrank. With DK slips Sep 30–Oct 8: overs 20-22, unders 31-16.
- By tag: OVER 7-11 (week **0-5**) · UNDER 12-6 · LEAN UNDER 2-0 · LEAN OVER 0-1 · NO EDGE 13-9 (overs 6-4, unders 7-5). NO EDGE overs flipped from 2-4 to 6-4 (4-0 this week).
- 🔥 9-4 (week 1-3) · no 🔥 25-23. 🎯 1-0, ⚠️ none bet (from Oct 24; too small).
- Home goalie 18-13 · road 16-14. Over home 7-8 · over road 6-8 · under home 11-5 · under road 10-6.
- Overs on lines ≤24.5: 4-9 (31%) · ≥25.5: 9-7.
- Model cushion on his side: <0 9-4 · 0–2 13-11 · 2+ 12-12 (week 3-8 — the big-cushion bets cooled hard).
- Timing: >6h before puck drop 13-17 (43%; week 4-9) · 2–6h 8-6 · <2h 13-4 (76%).
- DK 21-20 · FD 13-7.
- **Losses concentrate in:** model OVER tags (0-5 this week), overs on low lines (≤24.5), bets placed >6h out, and 🔥 lately. **Wins:** unders (still), NO EDGE bets of his own (13-9), late bets <2h (13-4), FD.
- vs Oct 19: stronger — overs on low lines (3-6 → 4-9), late bets win (9-3 → 13-4), early bets lose (9-8 → 13-17). Faded — NO EDGE overs as a leak (now 6-4), 🔥 (8-1 → 9-4), big cushion (9-4 → 12-12), home-over weakness (4-6 → 7-8). Every group under ~30 bets; timing and line size are the two worth watching. No rules proposed.

### 2026-10-19 (baseline, 38 goalies logged Oct 10–18, each once)
- Overs 9-10 (47%) · unders 14-5 (74%). DK slips Sep 30–Oct 8: overs 7-6, unders 10-5.
- By tag: OVER 7-6 · UNDER 10-3 · LEAN UNDER 1-0 · NO EDGE 5-6 (overs 2-4, unders 3-2). Never bet against a tag.
- 🔥 8-1 · no 🔥 15-14.
- Home goalie 10-8 · road 13-7. Over home 4-6 · over road 5-4 · under home 6-2 · under road 8-3.
- Overs on lines ≤24.5: 3-6 · ≥25.5: 6-4.
- Model cushion on his side: <0 5-2 · 0–2 9-9 · 2+ 9-4.
- Timing: >6h before puck drop 9-8 · 2–6h 5-4 · <2h 9-3.
- DK 15-10 · FD 8-5.
- Losses concentrate in overs (esp. NO EDGE, home, low lines); several over losses were pulls/blowouts (Murashov 14, Wallstedt 13, Dostal 18). Wins: 🔥 and model unders. All groups < 20 bets — patterns, not rules.

## Daily reviews

### 2026-10-12 (seed entry, written by hand)
- 🍀 **Markstrom (FLA) u23.5 DK / u24.5 FD UNDER — won, but lucky.** Expected 24.6 shots on FLA; Buffalo actually shot 32. He was pulled after one period with 9 saves, which is the only reason the under cashed. The volume read was wrong.
- Wallstedt (MIN) LEAN OVER o26.5 lost (21 saves); Vegas shot only 23 vs 29.0 expected — wrong read on volume, matching the owner's fade.

### 2026-10-13
- **Night:** OVER 2-3, UNDER 2-2, LEAN UNDER 0-2 (model 4-7); 🔥 2-1. Read accuracy ✅4 🍀0 😬0 ❌7. NO EDGE 5 over / 12 under. Owner's bets 5-2 by goalie (6-2, 8 bets); his fades 2-1.
- ✅ Gibson (DET) 🔥 OVER 24.5 — exp 28.1 sv / 31.7 shots; NJD shot 37, 32 saves.
- ✅ Vladar (PHI) OVER 23.5 — exp 26.5 / 29.9; SEA shot 31, 29 saves.
- ✅ Hofer (STL) UNDER 25.5 — exp 20.8 / 23.5; OTT shot 17, 15 saves (Sanderson out for OTT).
- ✅ Vejmelka (UTA) 🔥 UNDER 24.5 DK / 23.5 FD — exp 21.3 / 24.1; TOR shot 26, 22 saves.
- ❌ Luukkonen (BUF) 🔥 UNDER 24.5 DK / 23.5 FD — exp 21.3 / 24.1; MTL shot 38, 35 saves. Dahlin (BUF) out; model has no injury math. H2H (26, playoffs) agreed with the under.
- ❌ Dostal (ANA) LEAN UNDER 21.5 DK / UNDER 22.5 FD — exp 21.6 / 24.4; CGY shot 36, 32 saves. H2H L4 on ANA was 26.8 and CGY shot 28 on ANA just Oct 10 — the H2H was the warning.
- ❌ Skinner (WPG) OVER 25.5 DK / 24.5 FD — exp 26.1 / 29.5; MIN shot 21, 19 saves. H2H (29.5) agreed with the over; MIN's Faber out (guess: less MIN puck movement).
- ❌ Allen (NJD) OVER 27.5 — exp 28.0 / 31.6; DET shot 27, 23 saves. Line sat right at expected (0.5 cushion).
- ❌ Stolarz (TOR) OVER 28.5 — exp 28.8 / 32.5; UTA shot 28, 23 saves. Same thin 0.3 cushion.
- ❌ Hill (VGK) UNDER 22.5 DK / 23.5 FD — exp 21.3 / 24.1; NSH shot 27, 25 saves. H2H 21.3 agreed with the under.
- ❌ Blackwood (COL) LEAN UNDER 21.5 — exp 21.8 / 24.6; DAL shot 26, 24 saves. Makar out for COL by the FD alert (guess: helped DAL volume).
- Saros (NSH): first line DK 28.5 NO EDGE; FD later LEAN OVER 26.5 lost (VGK 25 shots, 20 saves).
- NO EDGE far past the line: Levi (EDM) 39 vs 25.5 (LAK 40 shots, EDM only 17); Merilainen (VAN) 35 vs 27.5 (NYI 38); Swayman (BOS) 35 vs 24.5 (SJS 38); Fowler (MTL) 14 vs 22.5 (BUF 17); Kuemper (LAK) 4 saves on 17 shots — likely left early (not confirmed).
- **Owner's reads:** beat the model on Luukkonen (Dahlin out), Skinner (WPG tight at home) and Thompson (found the over in a NO EDGE: CAR 35 shots). Lost to it on Vladar (SEA shot 31) and Oettinger (COL only 25). His bets right on volume 5 of 7 goalies (Hill and Oettinger wrong).
- **Takeaway:** both thin OVERs (line within 0.5 of expected) missed; worth checking in the accuracy analysis whether OVER tags with < 1 save cushion are coin flips.

### 2026-10-14
- **Night (2 games):** UNDER 1-0 (model 1-0); read accuracy ✅1. NO EDGE 1 over / 2 under. Owner's bets 1-1.
- ✅ Wedgewood (COL) UNDER 22.5 DK/FD — exp 22.0 sv / 24.9 shots; DAL shot 22, 20 saves. H2H (20.5) and Johnston out for DAL both pointed the same way.
- NO EDGE: Dobes (MTL) 25.5 → 18 saves (WSH 23 shots vs 27.6 exp; 5 goals on 23 — possible pull, not confirmed). Lindgren (WSH) 23.5 → 26 (MTL 30 vs 27.3; Roy out for WSH). DeSmith (DAL) 26.5 → 25 (COL 27 vs 27.9; back-to-back after Oct 13).
- Shadows: B matched live on Wedgewood (UNDER ✅) and leaned over on DeSmith (❌); A had no tags.
- **Owner's reads:** followed the model on Wedgewood (right); DeSmith over was a NO EDGE swing that needed ~30 COL shots — COL shot right at expected, so the model's "no edge" was the better call.

### 2026-10-15
- **Night (11 games):** OVER 4-1, UNDER 3-0 (model 7-1); 🔥 1-0. Read accuracy ✅6 🍀1 😬0 ❌1. NO EDGE 8 over / 4 under. Owner's bets 5-4 (9 bets, one per goalie); his notes 1 of 3 right.
- ✅ Merilainen (VAN) OVER 25.5 DK/FD — exp 27.2 sv / 30.7 shots; FLA shot 39, 36 saves.
- ✅ Varlamov (NYI) 🔥 UNDER 25.5 — exp 20.3 / 22.9; OTT shot 19, 18 saves. (Alert went first to Sorokin, who didn't start → void.)
- ✅ Daws (NJD) UNDER 21.5 FD / LEAN UNDER 20.5 DK — exp 21.4 / 24.2; NYR shot 19, 18 saves.
- ✅ Wolf (CGY) OVER 26.5 — exp 27.4 / 31.0; VGK shot 33, 27 saves.
- ✅ Grubauer (SEA) OVER 26.5 — exp 26.9 / 30.4; TBL shot 35, 31 saves.
- ✅ Vejmelka (UTA) UNDER 25.5 DK / 23.5 FD — exp 20.4 / 23.1; EDM shot 24, 22 saves (volume ≈ expected; well under the line).
- 🍀 Woll (PHI) OVER 23.5 DK won (24) / 25.5 FD lost — exp 29.4 / 33.2; DET shot only 26. Won by half a save on low volume. H2H (DET on PHI avg 26.0) was the warning; York (PHI D) out didn't add shots.
- ❌ Levi (EDM) OVER 23.5 DK / 24.5 FD — exp 26.3 / 29.7; UTA shot 24, 20 saves. H2H (UTA on EDM avg 25.5) warned again.
- NO EDGE far past the line: Garand (NYR) 9 vs 28.5 (NJD shot 31 — likely pulled, not confirmed); Hofer (STL) 33 vs 26.5 (MIN 38); Nedeljkovic (SJS) 32 vs 22.5 (NSH 34); Hart (VGK) 28 vs 20.5 (CGY 30); Knight (CHI) 31 vs 24.5 (WPG 34, Byram out for CHI).
- Shadows: B would have passed on Levi (NO EDGE) and added Ullmark UNDER (20 ✅) and Vasilevskiy LEAN UNDER (24 ❌); A had Wolf/Grubauer as LEAN OVER (both ✅).
- **Owner's reads:** Daws (NJD tight at home + H2H) right. Skinner under wrong (CHI shot 28; H2H 22 misled). Bobrovsky under wrong — Dahlin actually played (hat trick); check the final lineup before betting on an injury listed DTD. Model beat him on the night; the two NO EDGE unders he took both lost.

### 2026-10-16
- **Night (2 games):** LEAN OVER 0-1 (model 0-1); read accuracy 😬1. NO EDGE 1 over / 2 under. Owner's bets 0-1.
- 😬 Silovs (PIT) LEAN OVER 28.5 DK/FD — exp 28.0 sv / 31.6 shots; COL shot 32, 27 saves (.844). Volume came in as read; lost on 5 goals against. H2H (COL on PIT avg 27.3) pointed under and was wrong. Pull not confirmed (none likely at 27 saves).
- NO EDGE: Blackwood (COL) 23.5 DK / 22.5 FD → 29 (PIT 31 shots vs ~25.6 exp). Dostal (ANA) 21.5 DK / 23.5 FD → 18 (BOS 22 vs 26.3; 4 GA). DiPietro (BOS) 27.5 DK / 26.5 FD → 25 (ANA 27 vs 28.1).
- Shadows: B went 0-3 (Silovs OVER ❌, Blackwood UNDER ❌, DiPietro LEAN OVER FD ❌); A had no tags. Live model did better by staying NO EDGE.
- **Owner's reads:** Dostal o21.5 lost — BOS shot only 22; neither reason (H2H 34 avg, BOS shooting) showed up. Model's NO EDGE was the better call (though it also leaned slightly over on volume).

### 2026-10-17
- **Night (14 games):** OVER 3-3, UNDER 2-3, LEAN UNDER 1-0 (model 6-6); 🔥 3-0. Read accuracy ✅6 ❌6. NO EDGE 12 over / 3 under. Owner's bets 5-4 (10 bets, 1 void).
- ✅ Thompson (WSH) 🔥 OVER 25.5 — exp 28.9 sv / 32.6 shots; NJD shot 31, 29 saves.
- ✅ Lankinen (VAN) 🔥 OVER 25.5 FD / 26.5 DK — exp 28.4 / 32.1; TBL shot 35, 31 saves. (First alert went to Demko → void.)
- ✅ Daccord (SEA) OVER 25.5 — exp 27.3 / 30.8; FLA shot 37, 29 saves.
- ✅ Markstrom (FLA) LEAN UNDER 21.5 DK / UNDER 22.5 FD — exp 21.8 / 24.6; SEA shot 23, 20 saves.
- ✅ Oettinger (DAL) UNDER 20.5 — exp 20.2 / 22.8; CHI shot 19, 19 saves.
- ✅ Vejmelka (UTA) 🔥 UNDER 24.5 — exp 19.5 / 22.0; EDM shot 21, only 12 saves (likely pulled, not confirmed). Team volume still under — right read.
- ❌ Murashov (PIT) OVER 26.5 — exp 27.8 / 31.4; VGK shot 19, 14 saves. H2H (VGK on PIT 25.8) warned.
- ❌ Swayman (BOS) OVER 25.5 — exp 28.6 / 32.3; LAK shot 26, 25 saves. H2H (LAK on BOS 26.3) warned.
- ❌ Nedeljkovic (SJS) OVER 25.5 — exp 26.7 / 30.1; DET shot 27, 24 saves. H2H (DET on SJS 26.3) warned.
- ❌ Greaves (CBJ) UNDER 22.5 — exp 20.8 / 23.5; NYR shot 29, 29 saves. H2H (NYR on CBJ 28.0) warned.
- ❌ Ullmark (OTT) UNDER 21.5 — exp 20.6 / 23.3; PHI shot 28, 25 saves, even with Konecny and York out. Sanderson out for OTT (fits the D-out pattern).
- ❌ Forsberg (LAK) UNDER 22.5 — exp 22.1 / 24.9; BOS shot 28, 24 saves. Thin 0.4 cushion; shadow A had it NO EDGE.
- NO EDGE far past the line: Stevenson (WPG) 34 vs 26.5 (CAR 37, Morrissey out); Gibson (DET) 31 vs 23.5 (SJS 34); Luukkonen (BUF) 30 vs 25.5 (MTL 34, Dahlin out); Bobrovsky (TOR) 16 vs 25.5 (NYI 20).
- Shadows: B added 3-1 (Luukkonen OVER ✅, Sorokin OVER ✅, Jarry OVER ✅, Fowler UNDER ❌); A dropped Forsberg (avoided a loss), otherwise same as live.
- **Owner's reads:** followed the model except Allen u25.5 (NO EDGE) — right on volume (WSH 25 shots). His bets right on volume 5 of 9. No reasoning notes this night.

### 2026-10-18
- **Night (2 games):** OVER 1-0 (model 1-0); read accuracy ✅1. NO EDGE 2 over / 1 under. Owner's bets 0-1.
- ✅ Cooley (CGY) OVER 27.5 DK/FD — exp 27.7 sv / 31.2 shots; CAR shot 36, 34 saves. Thin 0.2 cushion, but volume came in big; H2H (30.5) and CAR L5 for (35.0) agreed.
- NO EDGE far past the line: Bussi (CAR) 31 vs 21.5 (CGY 34 vs 25.8 exp; H2H 22.3 and CAR L5 against 22.0 both said low). Wallstedt (MIN) 13 vs 23.5 DK / 22.5 FD (CBJ only 14 shots vs 27.1 — full game, no pull; MIN outshot them 34-14). Talbot (CBJ) 32 vs 27.5 (MIN 34 vs 29.1; H2H 35.0 agreed).
- Shadows: A and B both had Cooley LEAN OVER ✅; B also had Talbot LEAN OVER ✅ (live NO EDGE). B 2-0 on the night.
- **Owner's reads:** Wallstedt o23.5 on H2H — CBJ shot 14, wrong on volume. His H2H-based calls are now 2 right / 3 wrong.

### 2026-10-19
- **Night (4 games):** OVER 1-1, UNDER 1-2 (model 2-3); 🔥 0-1. Read accuracy ✅2 ❌3. NO EDGE 1 over / 2 under. Owner's bets 1-3.
- ✅ Askarov (SJS) OVER 25.5 DK/FD — exp 25.9 sv / 29.2 shots; TOR shot 32, 29 saves. Thin 0.4 cushion; H2H (28.0) agreed.
- ✅ Blackwood (COL) UNDER 21.5 DK/FD — exp 20.6 / 23.2; PHI shot 24, 21 saves. PHI without Konecny, York, Tippett; H2H (23.8) agreed.
- ❌ Woll (PHI) 🔥 OVER 25.5 DK / 26.5 FD — exp 28.0 / 31.6; COL shot only 26, 24 saves. H2H (31.0) and York out both pointed over; neither showed. Owner's 🔥 bets now 8-2.
- ❌ Garand (NYR) UNDER 24.5 DK/FD — exp 19.9 / 22.4; ANA shot 31, 29 saves. 4.6-save cushion missed badly. H2H (ANA on NYR avg 29.5) warned.
- ❌ Husso (ANA) UNDER 23.5 DK / 24.5 FD — exp 21.6 / 24.4; NYR shot 30, 25 saves. H2H (27.8, above league 27.1) leaned against; shadow B had it NO EDGE.
- NO EDGE: Bobrovsky (TOR) 30 vs 24.5 FD / 25.5 DK (SJS 31 vs 28.3 exp); Silovs (PIT) 24 vs 25.5 (UTA 29 ≈ 29.0 exp, lost on goals); Cossa (UTA) 15 vs 22.5 DK / 23.5 FD (PIT 19 vs 25.1).
- Shadows: A same tags as live (2-3). B 3-3: dropped Husso (avoided a loss), added Cossa UNDER ✅ and Silovs OVER ❌.
- **Owner's reads:** no notes. Followed the model on Woll, Garand, Husso (all wrong on volume); his NO EDGE Cossa under was right (PIT 19). The ANA@NYR game went over on both sides with both H2Hs above league average — the H2H-disagreement pattern is now 9-4.

### 2026-10-20
- **Night (11 games):** OVER 0-2, LEAN OVER 2-0, UNDER 1-0 (model 3-2); 🔥 1-0. Read accuracy ✅3 ❌2. NO EDGE 10 over / 7 under. Owner's bets 3-2.
- ✅ Oettinger (DAL) 🔥 UNDER 23.5 DK/FD — exp 20.7 sv / 23.4 shots; BOS shot 20, 18 saves. H2H (23.5) agreed.
- ✅ Wedgewood (COL) LEAN OVER 27.5 DK/FD — exp 26.9 / 30.3; NJD shot 41, 37 saves. H2H (25.5) said under and was wrong.
- ✅ Nedeljkovic (SJS) LEAN OVER 27.5 DK/FD — exp 26.9 / 30.3; MTL shot 34, 31 saves. H2H (29.0) agreed.
- ❌ Thompson (WSH) OVER 24.5 DK/FD — exp 25.9 / 29.2; LAK shot 26, 21 saves (5 GA). Fiala out for LAK (fits key-shooter-out); Roy out for WSH didn't add shots. H2H 27.3 ≈ league, no signal.
- ❌ Grubauer (SEA) OVER 25.5 DK/FD — exp 26.8 / 30.2; DET shot 25, 22 saves. H2H (33.0) agreed with the over and missed.
- Stolarz (TOR): first line DK 28.5 NO EDGE; FD later LEAN OVER 27.5 won (CBJ 37, 35 saves). Merilainen (VAN): first DK 29.5 NO EDGE; FD LEAN OVER 28.5 won (CAR 44, 38 saves).
- NO EDGE far past the line: Hofer (STL) 32 vs 20.5 DK / 23.5 FD (WPG 33 vs 27.6 exp); Merilainen 38 vs 29.5; Stolarz 35 vs 28.5; Vasilevskiy (TBL) 32 vs 26.5 (VGK 34 vs 27.7); Greaves (CBJ) 14 vs 24.5 (TOR 22 vs 28.0, 8 GA — likely pulled, not confirmed); Hart (VGK) 15 vs 22.5 (TBL 21, 6 GA); Sorokin (NYI) 15 vs 22.5 (ANA 17).
- Shadows: A 1-2 (Thompson ❌, Oettinger ✅, Grubauer ❌; dropped both LEAN OVER winners). B 4-2 (dropped Thompson; Wedgewood, Sorokin UNDER, Oettinger, Nedeljkovic ✅; Dobes UNDER ❌, Grubauer ❌).
- **Owner's reads:** Allen u27.5 wrong on volume — none of his three reasons showed (COL 34). Beat the model nowhere off-tag except Kochetkov u19.5 (NO EDGE, VAN 17 — right). H2H disagreement finally lost one (Wedgewood); still 9-5.

### 2026-10-21
- **Night (2 games):** OVER 1-0, UNDER 0-2 (model 1-2); 🔥 0-2. Read accuracy ✅1 ❌2. NO EDGE 0 over / 1 under. Owner's bets 0-1. (Alerts went out under the old model; the home/road ±1.5 nudge went live at 10:13 PM. It wouldn't have changed any tag.)
- ✅ Vladar (PHI) OVER 24.5 DK/FD — exp 26.8 sv / 30.3 shots; BUF shot 28, 27 saves. A bit under expected volume but above league avg and enough for the line. H2H (BUF on PHI 25.8) said under and was wrong.
- ❌ Luukkonen (BUF) 🔥 UNDER 22.5 DK/FD — exp 19.5 / 22.0; PHI shot 26, 23 saves (lost by 0.5). PHI was without Konecny, Tippett and York and still beat expected by 4; H2H (27.0) ≈ league, no signal.
- ❌ Schmid (FLA) 🔥 UNDER 24.5 DK/FD — exp 18.9 / 21.4; OTT shot 30, 25 saves (lost by 0.5; 5 GA, full game). OTT had shot only 17–26 in its last 5 (avg 20.4) and H2H (24.8) agreed — nothing in our data warned. OTT won and outshot FLA 30-19, so not a trailing team chasing. Second big-cushion UNDER miss (5.6 saves; Garand Oct 19 was 4.6).
- NO EDGE far past the line: Ullmark (OTT) 17 vs 23.5 FD / 24.5 DK (FLA only 19 shots vs 27.6 exp; Chabot out for OTT didn't add shots).
- Shadows: A and B had the same tags as live (1-2 each).
- **Owner's reads:** no notes. Followed the model on Schmid (🔥 UNDER) — wrong on volume. H2H disagreement pattern took a second straight loss (now 9-6, 15 cases).

### 2026-10-22
- **Night (12 games):** OVER 0-2, UNDER 2-1, LEAN UNDER 1-0 (model 3-3); 🔥 0-1. Read accuracy ✅3 ❌3. NO EDGE 11 over / 5 under. Owner's bets 5-2 (3-0 on NO EDGE goalies).
- ✅ Daws (NJD) UNDER 23.5 DK/FD — exp 20.9 sv / 23.6 shots; ANA shot 17, 16 saves. H2H (ANA on NJD 28.0) said over and was wrong.
- ✅ Bobrovsky (TOR) UNDER 25.5 DK/FD — exp 21.8 / 24.6; NYR shot 25, 21 saves. H2H (31.5) said over and was wrong.
- ✅ Oettinger (DAL) LEAN UNDER 20.5 DK/FD — exp 21.0 / 23.7; WPG shot 19, 17 saves. Thin 0.5 cushion held.
- ❌ Wallstedt (MIN) 🔥 OVER 22.5 DK / 23.5 FD — exp 26.8 / 30.2; CGY shot only 22, 20 saves (full game; MIN outshot them 37-22). CGY L5 for (31.6) and H2H (32.3) both agreed; Backlund out for CGY was the only warning in our data. 🔥 is 0-3 over the last two nights.
- ❌ Husso (ANA) OVER 27.5 DK/FD — exp 29.0 / 32.8; NJD shot 29, 25 saves. NJD L5 for (34.0) and H2H (30.8) agreed. Guess: NJD led most of the way and eased off (score by period not checked).
- ❌ DiPietro (BOS) UNDER 22.5 DK/FD — exp 21.4 / 24.2; NSH shot 28, 28 saves (shutout). H2H (NSH on BOS avg 32.8) warned; NSH L5 for was low (24.6).
- NO EDGE far past the line: Askarov (SJS) 41 vs 25.5 DK / 24.5 FD (OTT 43 vs 27.1 exp; Chabot out for OTT); Kuemper (LAK) 41 vs 23.5 (NYI 43 vs 27.6); Skinner (WPG) 35 vs 23.5 (DAL 38 vs 29.0; Morrissey out); Cooley (CGY) 36 vs 26.5 (MIN 37 vs 28.3); Bussi (CAR) 16 vs 24.5 (EDM 21); Gibson (DET) 4 vs 22.5 DK / 21.5 FD (VAN only 13 shots; 4 saves on 13 means he likely left early — not confirmed).
- Home/road nudge check (shadow B = old model without it): the nudge created 4 tags B didn't have — Bobrovsky ✅, Oettinger ✅, DiPietro ❌, Wallstedt ❌ (2-2).
- Shadows: A 5-2 (Daws ✅, Cooley LEAN OVER ✅, Bussi UNDER ✅, Vejmelka LEAN UNDER ✅, Gibson UNDER ✅; Husso ❌, Levi LEAN OVER ❌). B 4-2 (same minus Bussi). Live 3-3.
- **Owner's reads:** 5-2. Grubauer over on H2H was right on volume (UTA 36); Lankinen under won but DET shot 31 — lucky on goals. Beat the model on the night by finding three NO EDGE winners and taking the better book on two of them; lost with it on Wallstedt and Husso.

### 2026-10-23
- **Night (2 games):** LEAN OVER 0-1 (model 0-1); read accuracy ❌1. NO EDGE 1 over / 2 under. Owner's bets 0-2. (Bot was stuck from ~8:15 PM ET to 7:58 AM — a queued GitHub run blocked all others; cancelled by this review. No live results went out overnight.)
- ❌ Vasilevskiy (TBL) LEAN OVER 27.5 DK/FD — exp 27.0 sv / 30.5 shots; COL shot only 24, 18 saves (5 GA + an empty-netter; full game). COL led wire to wire (6-3) and eased off; H2H (COL on TBL 31.5) agreed with the over and missed. The tag exists only because of the road +1.5 nudge (shadow B had NO EDGE). Nudge-made tags since it went live: 2-3.
- NO EDGE: Blackwood (COL) 31 vs 24.5 DK / 23.5 FD (TBL 34 vs 25.4 exp — trailing all game); Fowler (MTL) 20 vs 21.5 (CHI 21 vs 26.2); Knight (CHI) 24 vs 26.5 (MTL 28 ≈ 28.0 exp; Suzuki out for MTL).
- Shadows: A and B both 1-1 (Fowler LEAN UNDER ✅, Knight LEAN OVER ❌; Vasilevskiy NO EDGE — avoided the loss). Live 0-1.
- **Owner's reads:** Blackwood under on "TBL on the road" — wrong on volume (34), game script beat a reasonable read. Vasilevskiy over with the model — wrong. Second straight night a road team he expected to be quiet shot more than the line needed.

### 2026-10-24
- **Night (12 games):** OVER 2-2, LEAN OVER 2-0, UNDER 2-3 (model 6-5); no 🔥. Read accuracy ✅6 ❌5. NO EDGE 6 over / 4 under. Owner's bets 2-2.
- ✅ Lindgren (WSH) UNDER 25.5 DK / 23.5 FD — exp 22.2 sv / 25.1 shots; BUF shot 21, 18 saves. H2H (29.0) said over and was wrong.
- ✅ Woll (PHI) UNDER 23.5 DK/FD — exp 21.8 / 24.6; ANA shot 26, 21 saves. Thin: 26 shots was just under what the line needed (~26.5); 5 GA helped.
- ✅ Nedeljkovic (SJS) OVER 24.5 FD / 25.5 DK — exp 26.4 / 29.8; BOS shot 35, 29 saves.
- ✅ Saros (NSH) OVER 25.5 — exp 26.5 / 29.9; PIT shot 37, 34 saves, even without Malkin and Rust. H2H (23.8) said under and was wrong.
- ✅ Luukkonen (BUF) LEAN OVER 26.5 DK / OVER 25.5 FD — exp 26.0 / 29.3; WSH shot 34, 30 saves.
- ✅ Stolarz (TOR) LEAN OVER 27.5 DK / OVER 26.5 FD — exp 26.8 / 30.2; EDM shot 32, 30 saves.
- ❌ Jarry (EDM) UNDER 24.5 DK / 23.5 FD — exp 22.0 / 24.8; TOR shot 31, 25 saves. TOR L5 for (avg 29.6) ran hotter than its season number; H2H (26.2) agreed with the under.
- ❌ Hart (VGK) OVER 23.5 DK/FD — exp 26.8 / 30.2; CBJ shot only 20, 18 saves. H2H (26.5) and CBJ L5 for (26.0) both warned; tag exists only because of the road +1.5 nudge (shadows A and B NO EDGE). Owner bet it.
- ❌ Silovs (PIT) UNDER 22.5 — exp 21.4 / 24.2; NSH shot 26, 24 saves. Small 1.1 cushion, volume a bit over.
- ❌ Vejmelka (UTA) UNDER 22.5 ⚠️ (TBL 5th most for) — exp 21.0 / 23.7; TBL shot 32, 29 saves. TBL L5 for 30.2; the ⚠️ warning was right.
- ❌ Forsberg (LAK) 🎯 OVER 28.5 DK/FD — exp 30.5 / 34.4; NJD shot only 26 (L5 for 33.8), 23 saves. NJD led most of the game (3 goals to 1 by our numbers; guess: eased off); LAK, without Fiala, shot just 13.
- NO EDGE far past the line: Hofer (STL) 35 vs 26.5 (CAR 39 vs 28.7 exp); Allen (NJD) 12 vs 23.5 (LAK 13 shots); Garand (NYR) 17 vs 25.5 (OTT 24; 7 goals on 24 by our numbers — possible pull, not confirmed); Daccord (SEA) 31 vs 26.5 DK / 25.5 FD (MIN 36); Dostal (ANA) 28 vs 21.5 FD / 22.5 DK (PHI 32 without Konecny/Tippett).
- Home/road nudge check (shadow B = old model without it): the nudge made 9 of the 11 tags and they went **6-3** (Lindgren, Woll, Nedeljkovic, Saros, Luukkonen, Stolarz ✅; Jarry, Hart, Silovs ❌). Nudge-made tags since it went live: **8-6**.
- Shadows: A 3-3 (Hofer, Cooley, Daccord LEAN OVER ✅; Dostal LEAN UNDER, Vejmelka LEAN UNDER, Forsberg LEAN OVER ❌). B 4-3 (Garand UNDER, Hofer OVER, Cooley, Daccord ✅; Dostal, Vejmelka, Forsberg ❌). Live 6-5.
- 🎯/⚠️ (first night live): 🎯 overs 2-1, 🎯 under 0-1, ⚠️ 1 for 1 as a warning.
- **Owner's reads:** Hofer over on CAR H2H + road volume — right, both reasons showed. Daccord over right. Kochetkov under a toss-up lost to a shutout. Hart over with the model wrong. He beat the model where it had no tag (2-1 on NO EDGE goalies) and lost with it on Hart.

### 2026-10-25
- **Night (5 games):** UNDER 1-0 (model 1-0); no 🔥. Read accuracy ✅1. NO EDGE 5 over / 4 under. Owner's bets 4-0, all right on volume.
- ✅ Oettinger (DAL) UNDER 21.5 DK/FD — exp 18.1 sv / 20.4 shots; NYI shot 20, 17 saves. H2H (NYI on DAL avg 29.5) said over and was wrong.
- Schmid (FLA): first line FD 20.5 NO EDGE; DK later LEAN UNDER 21.5 won — exp 22.4 / 25.3, CHI shot 21, 19 saves (🎯 under; owner bet DK).
- NO EDGE far past the line: Sorokin (NYI) 32 vs 22.5 FD / 24.5 DK (DAL 38 vs 27.2); Wedgewood (COL) 29 vs 20.5 FD / 21.5 DK (NSH 35 vs 28.2 — line was 4.5 below expected); Fowler (MTL) 33 vs 23.5 (WPG 34 vs 27.3); Knight (CHI) 30 vs 27.5 DK / 28.5 FD (FLA 33 vs 26.6, Marchand out); Annunen (NSH) 🎯 over 19 vs 29.5 FD / 28.5 DK (COL only 21 vs 28.0; H2H avg 38 on NSH, COL L5 for 28.6 — nothing warned); Skinner (WPG) 🎯 over 19 vs 25.5 (MTL 21 vs 26.3, Suzuki out); Pickard (MIN) 🎯 under 15 vs 20.5 (VAN 17 vs 25.2).
- Home/road nudge check (shadow B = old model without it): no nudge-made tags tonight; the nudge **removed** three B tags that would have won — Merilainen OVER (home −1.5), Pickard LEAN UNDER and Schmid FD LEAN UNDER (road +1.5). Nudge-made tags since live still 8-6; nudge-removed tags are worth counting in the Oct 28 review.
- Shadows: A 2-0 (Oettinger UNDER, Merilainen OVER). B 4-0 (+ Schmid, Pickard LEAN UNDER). Live 1-0.
- 🎯 (all on NO EDGE goalies): unders 2-0, overs 1-2. No ⚠️.
- **Owner's reads:** no notes; 4-0, right on volume on all four. Best night yet off the model: he took the 🎯 unders and the 🎯 over that the shadows also liked, and passed on the two 🎯 overs that missed.

### 2026-10-26
- **Night (3 games):** OVER 1-0 (model 1-0); 🔥 (FD line) 1-0. Read accuracy ✅1. NO EDGE 1 over / 4 under (first line). Owner's bets 3-0.
- ✅ Bobrovsky (TOR) 🎯 OVER 26.5 DK / 🔥 25.5 FD — exp 28.2 sv / 31.8 shots; CGY shot 34, 29 saves. H2H (27.8) ≈ league; CGY L5 against 32.0 agreed.
- NO EDGE: Reimer (NYR) 5 vs 25.5 (LAK 26 ≈ 26.3 exp; left early — not confirmed why); Kuemper (LAK) 23 vs 21.5 FD / 22.5 DK (NYR 26 vs 28.4; line 3.7 below expected → over); Cooley (CGY) 26 vs 26.5 DK / 25.5 FD (TOR 28 vs 29.2); Jarry (EDM) 26 vs 26.5 DK / 25.5 FD (DET 29 vs 26.3); Postava (DET) 🎯 under 25 vs 25.5 (EDM 28 vs 27.7). Four of five finished within a save of the line — the books were sharp tonight.
- Home/road nudge (now road +1.5 only, home cut dropped Oct 26): no nudge-made or nudge-removed tags (shadow B also had Bobrovsky OVER).
- Shadows: A 1-1 by first line (Bobrovsky LEAN OVER ✅; Cooley DK LEAN OVER ❌ at 26.5, though its FD OVER 25.5 won). B 1-0. Live 1-0.
- 🎯 2-0 (Bobrovsky over, Postava under). No ⚠️.
- **Owner's reads:** Reimer under on "home + Kings shooting less" — right on volume (26), win sealed by Reimer leaving early. Cooley over — toss-up, won on the FD number. Bobrovsky over with the model — right. He keeps taking the better book's number (FD a save lower on both overs).

### 2026-10-27
- **Night (11 games):** UNDER 1-0, LEAN UNDER 0-1, OVER 0-1 (model 1-2); no 🔥. Read accuracy 🍀1 ❌2. NO EDGE 6 over / 10 under. Owner's bets 4-2.
- 🍀 Saros (NSH) UNDER 25.5 DK won / 24.5 FD lost — exp 22.4 sv / 25.3 shots; NYI shot 28, 25 saves. Won DK by half a save with volume above expected. H2H (NYI on NSH avg 29.5) pointed over and was right.
- ❌ Dostal (ANA) LEAN UNDER 21.5 DK/FD — exp 21.5 / 24.2; VAN shot 33, 27 saves (6 GA). VAN's L5 for was tiny (17, 13, 17, 14, 17 = 15.6) and then they shot 33; ANA's L5 against was 27.6 (average) and H2H 27.5 ≈ league — nothing in our data warned. Zero cushion. Owner bet it.
- ❌ Ellis (BUF) OVER 25.5 DK/FD — exp 27.1 / 30.6; SJS shot only 23, 23 saves (shutout). SJS L5 for 30.0 (all road) and BUF L5 against 32.4 both said over; H2H (SJS on BUF 26.0) said under and was right. Tag exists only because of the road +1.5 nudge (shadows A and B NO EDGE). BUF dominated, 40 shots (guess: SJS never got going at home).
- Merilainen (VAN): first line DK 28.5 NO EDGE; FD later LEAN OVER 27.5 ⚠️ (ANA 4th least for) lost — ANA shot 23 vs 30.2 exp, 18 saves. Warning right.
- NO EDGE far past the line: Fowler (MTL) 46 vs 26.5 DK / 24.5 FD (STL 46 vs 28.7 — stopped all of them); Askarov (SJS) 38 vs 26.5 DK / 24.5 FD (BUF 40 vs 27.3); Vladar (PHI) 11 vs 25.5 (CBJ 15); Kochetkov (CAR) 14 vs 19.5 (BOS 15 vs 24.8); Binnington (STL) 18 vs 24.5 (MTL 20, Suzuki out); Stevenson (WPG) 19 vs 26.5 (FLA 24); Varlamov (NYI) 20 vs 24.5 (NSH 23 vs 29.0). 🎯 under Hill (VGK) 25 vs 20.5 ❌ (OTT 26).
- Home/road nudge (road +1.5): made Ellis's OVER (lost); no tags removed. Nudge-made tags since it went live: **8-7**.
- Shadows: A 0-1 (Dostal LEAN UNDER). B 1-1 (Saros UNDER DK ✅, Dostal ❌). Live 1-2.
- 🎯 under 0-1 (Hill). ⚠️ 1 for 1 as a warning (Merilainen).
- **Owner's reads:** Vladar under — right, all three reasons showed. Kochetkov under after the line moved — right, better number. Merilainen under against the FD LEAN OVER — right. Lost with the model on Dostal and on Forsberg's NO EDGE under. He beat the model on its untagged goalies again (NO EDGE unders 4-1).

### 2026-10-28
- **Night (4 games):** OVER 0-3, LEAN OVER 0-1 (model 0-4); no 🔥. Read accuracy 😬1 ❌3. NO EDGE 3 over / 1 under (first line). Owner's bets 3-1 (two of the wins lucky).
- 😬 Cooley (CGY) LEAN OVER 27.5 DK/FD — exp 26.8 sv / 30.2 shots; EDM shot 32 (volume right), Cooley only 8 saves — left early (pull not confirmed). H2H (EDM on CGY 36.0) agreed. Hyman out for EDM didn't lower volume.
- ❌ Blackwood (COL) OVER 26.5 DK/FD — exp 27.6 / 31.1; NJD shot 22, 20 saves. NJD L5 for 30.8, COL L5 against 33.0 and H2H 29.5 all said over — nothing in our data warned. COL dominated 44-22.
- ❌ Woll (PHI) OVER 27.5 DK/FD — exp 27.6 / 31.1; WSH shot 30 (~31 needed), 25 saves (5 GA). Zero cushion; PHI L5 against 24.2 and H2H 24.5 both warned under. Tag made by the road +1.5 nudge (shadow B NO EDGE). Owner took the under ✅.
- ❌ Bobrovsky (TOR) OVER 24.5 DK / 26.5 FD — exp 27.6 / 31.1; SEA shot only 17, 12 saves (5 GA). SEA L5 for 24.8 (none above 27) and H2H 25.5 warned; McCann out for SEA. Books split 2 saves (DK 24.5 vs FD 26.5).
- Thompson (WSH): first line DK 20.5 NO EDGE → over; FD LEAN UNDER 21.5 lost (PHI 25 ≈ 24.8 exp, 23 saves — lost on save%).
- NO EDGE far past the line: Allen (NJD) 39 vs 26.5 (COL 44 vs 29.1 exp); Grubauer (SEA) 🎯 over 17 vs 25.5 (TOR 21 vs 28.6; H2H 30.3 said over).
- Home/road nudge (road +1.5): made Woll's OVER and Cooley's LEAN OVER — both lost (Cooley right on volume). Nudge-made tags since it went live: **8-9**.
- Shadows: A 0-2 (Blackwood, Bobrovsky OVER). B 0-2 (same). Live 0-4. All three road-goalie tags (Cooley, Woll, Bobrovsky) were overs and all lost.
- 🎯 over 0-1 (Grubauer). No ⚠️.
- **Owner's reads:** 3-1 against the model's overs. Woll under right (narrow, goals helped); Cooley under and Jarry over won on a pull and a shutout, not volume; Grubauer 🎯 over wrong. He beat the model's tags on both games he faded (Woll, Cooley).


### 2026-10-29
- **Night (11 games):** OVER 1-6, UNDER 1-2, LEAN UNDER 1-0 (model 3-8); 🔥 Skinner (DK) ❌, Silovs (FD line) ✅. Read accuracy ✅3 😬1 ❌7. NO EDGE 5 over / 5 under. Owner's bets 3-4.
- ✅ Silovs (PIT) OVER 24.5 DK / 🔥 23.5 FD — exp 26.1 sv / 29.5 shots; UTA 34, 30 saves.
- ✅ Oettinger (DAL) UNDER 21.5 — exp 20.3 / 22.9; MTL 21, 16 saves.
- ✅ Gibson (DET) 🎯 LEAN UNDER 21.5 DK (FD 20.5 NO EDGE) — exp 21.9 / 24.7; CHI 19, 18 saves.
- 😬 Skinner (WPG) 🎯 🔥 OVER 25.5 DK / 24.5 FD — exp 28.9 / 32.6; TBL shot 31 (enough), Skinner only 16 saves → pulled (31 shots, 16 saves; reason not confirmed). Morrissey out.
- ❌ Swayman (BOS) OVER 24.5 — exp 27.3 / 30.8; STL shot 18, 14 saves. H2H 29.5 agreed. Tag made by the road nudge (shadow B NO EDGE). STL led and sat back (guess).
- ❌ Dobes (MTL) OVER 24.5 — exp 26.4 / 29.8; DAL shot 19, 17 saves. Nudge-made too (A and B NO EDGE). MTL won 5-2-ish; Suzuki out for MTL doesn't explain DAL's low volume.
- ❌ Merilainen (VAN) OVER 26.5 — exp 28.3 / 32.0; SJS shot 24, 21 saves. SJS L5 for 27.8 and falling (31, 30, 28, 27, 23) — the trend pointed down; H2H 31.5 agreed with the tag.
- ❌ Sorokin (NYI) OVER 26.5 — exp 27.6 / 31.2; MIN shot 25, 22 saves. H2H 30.8 agreed. Thin-ish cushion (1.1).
- ❌ Greaves (CBJ) OVER 26.5 — exp 27.7 / 31.3; CAR 27, 24 saves. Owner bet it.
- ❌ Kochetkov (CAR) 🎯 UNDER 20.5 — exp 19.8 / 22.4; CBJ 26, 24 saves. 0.7 cushion; H2H 22.3 agreed. Owner bet it.
- ❌ Wallstedt (MIN) UNDER 21.5 — exp 21.1 / 23.8; NYI 26, 22 saves (lost by half a save). H2H (29.0) said over and was right; Faber out for MIN.
- Knight (CHI): DK 28.5 NO EDGE → under (27; DET 31); FD LEAN OVER 27.5 lost.
- NO EDGE far past the line: Hofer (STL) 31 vs 23.5 (BOS 32 vs 26.2); Cossa (UTA) 31 vs 23.5 (PIT 34 vs 27.7, Rust out); Ellis (BUF) 29 vs 24.5 (ANA 35, Terry out); Kuemper (LAK) 17 vs 24.5 (OTT 22); Vasilevskiy (TBL) 17 vs 22.5 (WPG 21). Dostal void (Husso started: 24 vs 24.5 DK / 23.5 FD).
- Home/road nudge (road +1.5): made Swayman's and Dobes's OVERs — both lost. Nudge-made tags since it went live: **8-11**. Road goalies faced −3.1 shots vs live (−1.6 vs old), home +0.1. Every road-goalie OVER since Oct 27 has lost (0-10) — logged as a pattern to test mid-Nov, not a rule.
- Shadows: A 3-7, B 3-6, live 3-8 (same misses; B's only edge is skipping the two nudge-made overs).
- 🎯 under 1-1 (Gibson ✅, Kochetkov ❌), 🎯 over 0-2 (Skinner, Knight). No ⚠️.
- **Owner's reads:** Askarov over right (both reasons real, narrow). Ellis under on Terry out wrong (ANA 35). Knight under beat the 🎯 and FD tag. Followed the model 2-2 (Silovs ✅, Skinner pulled, Kochetkov and Greaves ❌).

### 2026-10-30
- **Night (3 games):** OVER 0-2 (model 0-2); 🔥 Hellebuyck ❌. Read accuracy ❌2. NO EDGE 1 over / 2 under. Owner's bets 1-1.
- ❌ Hellebuyck (NJD) 🔥 OVER 22.5 FD / 23.5 DK — exp 26.8 sv / 30.3 shots; VGK shot 21, 19 saves. Road goalie; tag made by the road nudge (A and B NO EDGE). NJD's L5 against was 25.2 (18 at DAL, 44 at COL — all over the place); H2H 31.5 agreed. NJD led and VGK didn't chase. FD moved 22.5 → 23.5 before puck drop (market went the wrong way too).
- ❌ Grubauer (SEA) 🎯 OVER 26.5 DK/FD — exp 27.8 / 31.4; CGY shot 27, Grubauer only 10 saves → left early (pull or injury, not confirmed). Even the full 27 was short of the ~30 the line needed. CGY L5 for 27.8 (average); the over leaned on SEA's L5 against 31.0. H2H 31.8 agreed. Shadow A LEAN OVER, B OVER — all three lost.
- NO EDGE: Wolf (CGY) 20 vs 26.5 DK / 25.5 FD under (SEA 22, McCann out); Schmid (FLA) 22 vs 22.5 DK under / 21.5 FD over (WPG 24 vs 26.5 exp; FLA shot 38); Hill (VGK) 27 vs 26.5 DK over (NJD 32 vs 29.3).
- Road-goalie OVER tags since Oct 27: **0-12**. Model OVER tags since Oct 27: **1-12**. Nudge-made tags: **8-12**.
- 🎯 over 0-1 (Grubauer). No ⚠️.
- **Owner's reads:** Wolf under on McCann out — right, reason showed (beats the model's NO EDGE). Followed the 🔥 on Hellebuyck — wrong on volume.

