# Daily reviews and patterns

Written by the daily review (Claude) each morning after results are graded, plus the owner's own reads.
Purpose: spot repeatable reasons the model misses, so they can be **tested** and maybe built in later.
Nothing here changes the model by itself (owner's rule: no rules on hunches; test against results first).

## Read accuracy (season to date, from Oct 12)
Judges the read on shot volume, not just the bet result.
- **Through Oct 16:** Right reads ✅ 11 · Lucky wins 🍀 2 · Unlucky losses 😬 1 · Wrong reads ❌ 9 (volume read right ✅+😬 = 12/23 = 52%)
- Oct 16: 😬1 (only one tagged goalie on a 2-game night).
- Oct 15: ✅6 🍀1 ❌1.
- Oct 14: ✅1 (only one tagged goalie on a 2-game night).
- Oct 12 is partial (only Markstrom 🍀 and Wallstedt ❌ were reviewed); full nightly counting starts Oct 13 (✅4 ❌7).

## Patterns to watch (update as evidence builds; note game count)
- **H2H low-volume matchups vs. an OVER/LEAN OVER read** (1 game). Owner faded Wallstedt o26.5 (Oct 12) because VGK had shot little on MIN in H2H (avg 24.0) — model said 25.7 expected. Went under (21). Test idea: does H2H avg below line predict unders when the model leans over?
  - Oct 13: no new case. Caution on H2H generally: in 6 of the 7 wrong reads Oct 13 the H2H L4 *agreed* with the tag (Skinner 29.5, Allen 30, Stolarz 31 shots for overs; Hill 21.3, Blackwood 19.5, Luukkonen 26 for unders) — H2H did not save any of them. Only Dostal's H2H (26.8 on ANA) pointed against the lean under, and it was right (CGY 36).
  - Oct 14: H2H right on COL-DAL (DAL on COL avg 20.5 → 22 shots, Wedgewood under won; COL on DAL 27.5 → 27). Wrong on MTL-WSH (WSH on MTL avg 33.8 → only 23; MTL on WSH 26.8 → 30). Mixed — no edge from H2H alone yet.
  - Oct 15: H2H pointed against the model on 4 tagged reads — right on Woll (DET on PHI avg 26.0 → 26 vs 33.2 exp) and Levi (UTA on EDM 25.5 → 24 vs 29.7), wrong on Varlamov (OTT on NYI 25.5 → 19) and Merilainen (FLA on VAN 27.5 → 39). Owner's H2H reads: Skinner (CHI on WPG avg 22 → 28) wrong; Bobrovsky H2H (BUF on TOR avg 30) warned against his under and was right (34). Running tally when H2H disagrees with the model: 3 right / 3 wrong (Dostal, Woll, Levi vs Varlamov, Merilainen, + Oct 14 WSH). Still a coin flip; test once ~15–20 disagreements.
  - Oct 16: H2H wrong twice. COL on PIT avg 27.3 vs model 31.6 exp → COL shot 32 (model right). Owner's "H2H looks good" on Dostal (BOS on ANA avg 34.0) → BOS shot 22. Running when H2H disagrees with the model: 3 right / 4 wrong.
- **Home team "tight at home" in L5 shots against** (3 games, 3 support; Oct 15: owner took Daws u21.5 because NJD tight at home → NYR shot 19). Owner noted MIN allowing mid-20s at home in L5 (Oct 12, Wallstedt). Oct 13: owner faded Skinner (WPG) OVER 25.5 because WPG played tight at home last game → MIN shot 21. Test idea: home/road split of the last 5 vs. the season blend.
- **Unders outperforming overs early** (season to Oct 12: OVER 6-6, UNDER 12-5; NO EDGE 62% under). Covered by the Oct 14 accuracy analysis.
  - Oct 13 mixed: OVER 2-3, UNDER 2-2, LEAN UNDER 0-2; NO EDGE 5 over / 12 under (71% under) — the under lean on lines keeps showing up even when the model's tags miss.
  - Oct 14: UNDER 1-0; NO EDGE 1 over / 2 under (Dobes 18 vs 25.5, DeSmith 25 vs 26.5; Lindgren 26 vs 23.5 over).
  - Oct 15 (contradicts): NO EDGE went 8 over / 4 under (one of the unders, Garand, was likely a pull). OVER 4-1, UNDER 3-0.
  - Oct 16: NO EDGE 1 over / 2 under (Blackwood 29 vs 23.5; Dostal 18 vs 21.5; DiPietro 25 vs 27.5). LEAN OVER 0-1.
- **Thin cushion (line within ~1 save of expected)** (from the Oct 13 takeaway; Oct 14 analysis had gap <1 save at 2-5 for Oct 7–13). Since then: Oct 15 Daws ✅, Grubauer ✅, Wolf ✅; Oct 16 Silovs 😬 (28.0 vs 28.5, volume on target, lost on save%). Running since Oct 15: 3-1. Test: record by gap bucket once ~15–20 thin-gap tags.
- **Key defenseman out → more shots against** (new, from owner's notes Oct 13; 4 games: 2 support, 1 slight, 1 against). Dahlin out (BUF): MTL shot 38 vs 24.1 expected — owner faded the 🔥 UNDER for this reason. Roy out (WSH): CAR shot 35 vs 27.6. Makar out (COL, late): DAL 26 vs 24.6. Against: Matheson out (MTL): BUF shot only 17 vs 27.3. Oct 14 (5th game, support): Roy still out (WSH) → MTL shot 30 vs 27.3 expected. Oct 15 (5 more: 2 support, 3 against): Morrissey out (WPG) → CHI 28 vs 25.7; Byram out (CHI) → WPG 34 vs 27.7; against: Sanderson out (OTT) → NYI 21 vs 25.8; York out (PHI) → DET 26 vs 33.2; Faber out (MIN) → STL 25 vs 26.2 (slight). **Running: 10 games, 5 support, 1 slight support, 4 against (1 slight)** — weaker than it looked. Test: picks.csv `key_out` already logs this (injury stage 2) — compare team shots against vs expected with/without a key D out once ~15–20 games have one.
- **Key shooter out → fewer shots for** (new, 1 game; this is injury stage 3's idea). Oct 14: Johnston out (DAL) → DAL shot 22 on COL vs 24.9 expected (H2H also low, so not clean evidence). Oct 15: Sanderson out (OTT) → OTT shot 19 on NYI vs 22.9 exp (support); Hyman out (EDM) → EDM 24 vs 23.1 (neutral); Marchand out (FLA) → FLA 39 vs 30.7 (against). Running 4 games: 2 support, 1 neutral, 1 against. (Dahlin was listed DTD but played — hat trick — so BUF isn't a case.) Test with picks.csv `key_out` (forwards) once ~15–20 games.

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

