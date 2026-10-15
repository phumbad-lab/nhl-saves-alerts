# Daily reviews and patterns

Written by the daily review (Claude) each morning after results are graded, plus the owner's own reads.
Purpose: spot repeatable reasons the model misses, so they can be **tested** and maybe built in later.
Nothing here changes the model by itself (owner's rule: no rules on hunches; test against results first).

## Read accuracy (season to date, from Oct 12)
Judges the read on shot volume, not just the bet result.
- **Through Oct 14:** Right reads ✅ 5 · Lucky wins 🍀 1 · Unlucky losses 😬 0 · Wrong reads ❌ 8 (read accuracy 5/14 = 36%)
- Oct 14: ✅1 (only one tagged goalie on a 2-game night).
- Oct 12 is partial (only Markstrom 🍀 and Wallstedt ❌ were reviewed); full nightly counting starts Oct 13 (✅4 ❌7).

## Patterns to watch (update as evidence builds; note game count)
- **H2H low-volume matchups vs. an OVER/LEAN OVER read** (1 game). Owner faded Wallstedt o26.5 (Oct 12) because VGK had shot little on MIN in H2H (avg 24.0) — model said 25.7 expected. Went under (21). Test idea: does H2H avg below line predict unders when the model leans over?
  - Oct 13: no new case. Caution on H2H generally: in 6 of the 7 wrong reads Oct 13 the H2H L4 *agreed* with the tag (Skinner 29.5, Allen 30, Stolarz 31 shots for overs; Hill 21.3, Blackwood 19.5, Luukkonen 26 for unders) — H2H did not save any of them. Only Dostal's H2H (26.8 on ANA) pointed against the lean under, and it was right (CGY 36).
  - Oct 14: H2H right on COL-DAL (DAL on COL avg 20.5 → 22 shots, Wedgewood under won; COL on DAL 27.5 → 27). Wrong on MTL-WSH (WSH on MTL avg 33.8 → only 23; MTL on WSH 26.8 → 30). Mixed — no edge from H2H alone yet.
- **Home team "tight at home" in L5 shots against** (2 games, 2 support). Owner noted MIN allowing mid-20s at home in L5 (Oct 12, Wallstedt). Oct 13: owner faded Skinner (WPG) OVER 25.5 because WPG played tight at home last game → MIN shot 21. Test idea: home/road split of the last 5 vs. the season blend.
- **Unders outperforming overs early** (season to Oct 12: OVER 6-6, UNDER 12-5; NO EDGE 62% under). Covered by the Oct 14 accuracy analysis.
  - Oct 13 mixed: OVER 2-3, UNDER 2-2, LEAN UNDER 0-2; NO EDGE 5 over / 12 under (71% under) — the under lean on lines keeps showing up even when the model's tags miss.
  - Oct 14: UNDER 1-0; NO EDGE 1 over / 2 under (Dobes 18 vs 25.5, DeSmith 25 vs 26.5; Lindgren 26 vs 23.5 over).
- **Key defenseman out → more shots against** (new, from owner's notes Oct 13; 4 games: 2 support, 1 slight, 1 against). Dahlin out (BUF): MTL shot 38 vs 24.1 expected — owner faded the 🔥 UNDER for this reason. Roy out (WSH): CAR shot 35 vs 27.6. Makar out (COL, late): DAL 26 vs 24.6. Against: Matheson out (MTL): BUF shot only 17 vs 27.3. Oct 14 (5th game, support): Roy still out (WSH) → MTL shot 30 vs 27.3 expected. Test: picks.csv `key_out` already logs this (injury stage 2) — compare team shots against vs expected with/without a key D out once ~15–20 games have one.
- **Key shooter out → fewer shots for** (new, 1 game; this is injury stage 3's idea). Oct 14: Johnston out (DAL) → DAL shot 22 on COL vs 24.9 expected (H2H also low, so not clean evidence). Test with picks.csv `key_out` (forwards) once ~15–20 games.

## Owner's reads (his reasoning on bets/fades)
- 2026-10-12 · Wallstedt (MIN) vs VGK · model LEAN OVER o26.5 · **owner faded**: H2H VGK shots on MIN low; MIN tighter at home in L5 (mid-20s). Result 21 saves → fade correct.

- 2026-10-13 · Vladar (PHI) vs SEA · model OVER o23.5 · **owner faded**: SEA on the road shoots mid-20s. SEA shot 31, 29 saves → fade wrong, model right.
- 2026-10-13 · Skinner (WPG) vs MIN · model OVER o25.5 · **owner faded**: WPG played tight at home last game. MIN shot 21, 19 saves → fade right.
- 2026-10-13 · Oettinger (DAL) vs COL · NO EDGE 24.5 · **owner took o24.5**: COL shoots, DAL faced weaker teams. COL shot 25, 22 saves → lost, read wrong (volume ~average).
- 2026-10-13 · Thompson (WSH) @ CAR · NO EDGE 26.5 · **owner took o26.5**: CAR shoots, WSH allowed less vs weak teams, top D (Roy) out. CAR shot 35, 31 saves → won, read right; all three reasons showed up.
- 2026-10-13 · Luukkonen (BUF) @ MTL · model 🔥 UNDER u24.5 · **owner faded**: Dahlin out. MTL shot 38, 35 saves → fade right; beat the model's 🔥.

- 2026-10-14 · Wedgewood (COL) vs DAL · model UNDER u22.5 · **owner took u22.5** (no note). DAL shot 22, 20 saves → won, read right on volume.
- 2026-10-14 · DeSmith (DAL) @ COL · NO EDGE 26.5 · **owner took o26.5** (no note). COL shot 27 (≈ expected 27.9; line needed ~30), 25 saves → lost, read wrong on volume. Shadow B also leaned over (25.6) and missed.

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

