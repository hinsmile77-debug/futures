# 618차 dev 이식 — 남은 한 조각: `bar_gap_section` (점검 항목)

> **MW0601 618차를 `dev` 로 체리픽할 때 이 파일 하나만 자동 적용을 뺐다.**
> 코드(라이브 `[BarGap]` 로그)는 다 들어갔다. 빠진 것은 **일일점검 수집기의
> 표시 항목** 하나뿐이고, 그것 없이도 라이브 로그로 진단은 된다.

작성: 2026-09-22 (MW0601 618차 후속) · 원 커밋 `49a2244` (v9-dev)

---

## 1. 왜 자동으로 안 넣었나

`git cherry-pick` 이 이 파일에서 충돌을 냈는데, **충돌을 그냥 해소하면 안 되는**
종류였다.

| | v9-dev | dev |
|---|---|---|
| 줄 수 | 2,970 | **5,298** |
| `state_snapshot_section`(MW0601 523차 G-1) | 있음 | **없음** |
| §9-b 절 | 있음 | 없음 |
| `devmemory_section` · `_exit_normally` 증거 항목 | 있음 | 있음(동일 문구) |

두 PC 가 같은 파일을 **각자 발전시켰다.** 618차 패치는 v9-dev 기준으로
`state_snapshot_section` 바로 뒤에 붙어 있어서, 충돌을 「618차 쪽 채택」으로
풀면 **523차 G-1 기능이 통째로 딸려 들어온다.** 618차 범위 밖이다.

⇒ 그래서 이 파일만 dev 원본을 그대로 두고, 손이식 절차를 이 문서로 넘긴다.

## 2. 무엇이 아쉬운가 — 없으면 무엇을 못 보나

일일점검 산출물에 이 표가 안 실린다:

```
### `raw_candles` 절단선·결손 (618차)

| 항목 | 값 |
|---|---|
| `raw_candles` 당일 max ts | **15:07** |
| 절단선(파생 = 강제청산 − 2분) | `15:08` |
| 판정 | **결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조 |
| `raw_candles` 당일 행수 | 381 |
| `session_bars` 당일 행수 | 411 (기대 411) |

- 결손 **3봉**: 09:41, 09:42, 15:08
  - 전부 `session_bars` 에 보존됨 → **데이터 손실 아님**.
```

🔴 **이게 막으려던 사고**: 2026-09-22 MW0601 점검 1차 진단이 `raw_candles`
당일 max=15:07 을 **「15:07 이후 38분 수집 공백」**으로 읽었다. 5거래일 비교로
뒤집혔다. 15:08 에서 끝나는 것이 **정상**인데, 그 사실이 코드 주석에만 있어
점검 산출물 어디에도 안 실렸기 때문이다.

대체 수단은 있다 — 라이브 로그 `logs/<날짜>_SYSTEM.log` 의 `[BarGap]` 두 줄
(기동 직후 · 15:46 확정)이 그대로 남는다. 이 절은 그것을 **점검 문서로 끌어올릴
뿐**이다.

## 3. 이식 절차 (dev 기준, 3곳)

### (1) 함수 추가 — `devmemory_section` 정의 **바로 앞**

⚠ dev 파일은 `import os` · `import sys` 가 이미 상단에 있다(28·33행). 추가 import 불필요.

```python
def bar_gap_section(root, cfg, day, out):
    """[MW0601 618차] `raw_candles` 절단선·결손 — 오독 재발 차단용.

    무엇을 막는가
    -------------
    2026-09-22 1차 진단이 `raw_candles` 당일 max=15:07 을 **「15:07 이후 38분
    수집 공백」**으로 읽었다. 5거래일 비교로 뒤집혔다 — 15:08 에서 끝나는 것이
    **정상**이고, 그 사실이 코드 주석(`main.py` 15:10 가드 · `utils/db_utils.py`
    session_bars 주석)에만 있어 점검 산출물 어디에도 안 실렸기 때문이다.

    판정
    ----
      · `== 15:08` → 정상 (절단선. 15:09~15:45 봉은 `session_bars` 에만 있다)
      · `<  15:08` → 결손. 재기동 공백인지 그 시각의 `[START]` 와 대조할 것
      · `>  15:08` → **이상**. 15:10 파이프라인 중단선이 안 먹었다는 뜻

    절단선은 리터럴이 아니라 `utils.time_utils.raw_candles_last_ts()` 파생값을
    쓴다 — 여기에 "15:08" 을 박으면 461차 `mdd_pct` 처럼 출처가 갈린다.

    ⚠ 읽기 전용이다(`mode=ro`). 다만 라이브 DB 전수 스캔은 아니다 — 하루치
      ts 만 읽는다(456차 장중 분석 금지의 취지는 대용량 스캔이다).
    """
    A = out.append
    day_txt = day.strftime("%Y-%m-%d")
    A("### `raw_candles` 절단선·결손 (618차)")
    A("")

    # 프로젝트 모듈을 쓴다 — 절단선을 여기서 다시 정의하지 않기 위해서다.
    try:
        if root not in sys.path:
            sys.path.insert(0, root)
        from utils.bar_gap import confirm_line, gap_vs_session
        from utils.bar_gap import raw_candle_minutes, session_bar_minutes
        from utils.time_utils import raw_candles_last_ts
    except Exception as e:
        A("(판정 모듈 로드 실패 — **미측정**) `%s`" % e)
        A("")
        return

    db = os.path.join(root, "data", "db", "raw_data.db")
    if not os.path.exists(db):
        A("(`data/db/raw_data.db` 없음 — **미측정**. `0` 도 `결손 없음` 도 아니다)")
        A("")
        return

    raw = raw_candle_minutes(db, day_txt)
    ses = session_bar_minutes(db, day_txt)
    if raw is None:
        A("(`raw_candles` 조회 실패 — **미측정**)")
        A("")
        return

    cut = raw_candles_last_ts().strftime("%H:%M")
    max_ts = max(raw) if raw else None
    if max_ts is None:
        verdict = "**행 없음** — 그날 파이프라인이 한 번도 안 돌았다"
    elif max_ts == cut:
        verdict = "정상 (절단선과 일치)"
    elif max_ts < cut:
        verdict = "**결손** — 아래 목록과 그 시각의 `[START]`/`[CLEAN EXIT]` 대조"
    else:
        verdict = "🔴 **이상** — 15:10 파이프라인 중단선 미작동"

    A("| 항목 | 값 |")
    A("|---|---|")
    A("| `raw_candles` 당일 max ts | **%s** |" % (max_ts or "(없음)"))
    A("| 절단선(파생 = 강제청산 − 2분) | `%s` |" % cut)
    A("| 판정 | %s |" % verdict)
    A("| `raw_candles` 당일 행수 | %d |" % len(raw))
    if ses is None:
        A("| `session_bars` 당일 행수 | (조회 실패 — 미측정) |")
    else:
        A("| `session_bars` 당일 행수 | %d (기대 411) |" % len(ses))
    A("")

    if ses:
        r = gap_vs_session(raw, ses)
        if r["missing"]:
            A("- 결손 **%d봉**: %s" % (len(r["missing"]), ", ".join(r["missing"][:20])
                                      + (" … 외 %d개" % (len(r["missing"]) - 20)
                                         if len(r["missing"]) > 20 else "")))
            A("  - 전부 `session_bars` 에 보존됨 → **데이터 손실 아님**. "
              "백필하지 않는다(533차 — 최근 N행 창이 밀린다).")
        else:
            A("- 결손 **0봉**")
        if r["permanent"]:
            A("- ⚠ **영구 결손 %d봉** (`session_bars` 에도 없음): %s"
              % (len(r["permanent"]), ", ".join(r["permanent"][:20])))
        if r["over_cut"]:
            A("- 🔴 절단선 초과 %d봉: %s" % (len(r["over_cut"]), ", ".join(r["over_cut"])))
        if r["orphan"]:
            A("- 🔴 `session_bars` 에 없는 raw 봉 %d개: %s"
              % (len(r["orphan"]), ", ".join(r["orphan"][:20])))
        A("")

    A("- 라이브 로그 대조: `logs/%s_SYSTEM.log` 의 `[BarGap]` 줄"
      % day.strftime("%Y%m%d"))
    A("  - 기동 직후 1줄(분그리드 기준) + 15:46 보충 직후 1줄(확정). "
      "**한 줄도 없으면 계측이 죽은 것**이지 결손이 없는 것이 아니다.")
    A("")
    A("> 결손 ts 는 그날 재기동 시각과 1:1 대응한다(실측 2026-09-07~09-22: "
      "결손일 3/12일, 12봉, 09-21 은 8회 재기동에 7봉). `[Shutdown] intent=` "
      "줄과 함께 보면 그 재기동이 사용자 의도인지 하드킬인지까지 갈린다.")
    A("")
```

### (2) 호출 추가 — `build()` 의 §9 끝, `# ---- 10. 정기점검 리포트 폴더 ----` **바로 앞**

dev 에는 §9-b 가 없으므로 `9-c` 가 아니라 **`9-b`** 로 붙이는 편이 자연스럽다.

```python
    # ---- 9-b. raw_candles 절단선·결손 (618차) ----
    bar_gap_section(root, cfg, day, L)

    # ---- 10. 정기점검 리포트 폴더 ----
```

### (3) 증거 항목 문구 갱신 — `"data/_exit_normally"` 항목의 `why`

종전 문구는 「로그의 `[Shutdown] 정상 종료 플래그 기록` 과 교차확인하라」인데,
그 줄은 **정상 종료 때만** 나와서 「재시작이었나 하드킬이었나」를 구분하지 못한다.
618차가 그 질문에 답하는 줄을 새로 넣었다:

```
[618차] 의도는 파일이 아니라 로그 `[Shutdown] intent=<daily_close|auto_shutdown|
user_close|user_restart> keep_alive=<bool>` 로 읽는다 — `user_restart` 는 파일을
쓰지 않으므로 런처 로그의 「일시적 크래시」를 그대로 믿지 말 것
```

## 4. 검증

```
python .claude/skills/mireuk-daily-check/scripts/collect_evidence.py \
    --phase post --date <거래일> --out C:\tmp\_ev.md
```

- `### \`raw_candles\` 절단선·결손 (618차)` 절이 나오는가
- 「절단선(파생 …)」이 **15:08** 인가 (리터럴이 아니라 `utils.time_utils.
  raw_candles_last_ts()` 를 import 해 쓴다 — 하드코딩하면 출처가 갈린다)
- 모듈 로드 실패 시 **「(판정 모듈 로드 실패 — 미측정)」**이 찍히는가.
  조용히 비면 안 된다(계측 4원칙 ②).

## 5. 주의 — 숫자를 그대로 옮기지 말 것

이 문서와 618차 `DECISION_LOG` 에 나오는 **결손 3/12일 · 12봉 · 09-21 8회
재기동 7봉** 은 전부 **MW0601 실측**이다. MW0602 는 별개 계좌·별개 DB 라
빈도가 다르다. 코드는 데이터 비의존이라 그대로 돌지만, **dev 쪽 기록에 이
수치를 MW0602 실측인 양 적지 말 것.**

한편 **절단선 15:08 자체는 데이터가 아니라 코드에서 나온다** — dev 의
`is_force_exit_time`(15:10) · 15:10 파이프라인 가드 · `save_candle_and_features`
3곳이 v9-dev 와 동일함을 618차 이식 시 전수 확인했다. 그래서 dev 에서도 같다.
