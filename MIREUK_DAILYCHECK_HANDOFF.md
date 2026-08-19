# 인계 — 미륵이 일일 점검 스킬 설치·검증

> 이 문서는 **MW0602에서 새로 시작한 Cowork 태스크**(또는 `futures` 리포에서 도는 Claude Code
> 세션)가 그대로 따라 하도록 쓰였다. 앞 세션은 MW0601에만 연결돼 있어 `futures` 리포를 직접
> 보지 못했다. **그래서 스킬은 완성돼 있지만 경로는 아직 실측 검증되지 않았다.**
> 아래 §3 검증을 반드시 먼저 하라.

---

## 1. 무엇을 받았나

`mireuk_dailycheck_install.zip` 을 `futures` 리포 루트에서 풀면 이렇게 된다.

```
futures/
├─ .claude/
│  ├─ commands/
│  │  └─ dailycheck.md                     ← 슬래시 커맨드 /dailycheck
│  └─ skills/mireuk-daily-check/
│     ├─ SKILL.md                           ← 절차 (항상 읽힘)
│     ├─ references/
│     │  ├─ phases.md                       ← 장전 A / 장중 B / 장후 C 체크리스트
│     │  ├─ invariants.md                   ← 절대원칙 6종 · 한시예외 3종 · 재인용금지
│     │  ├─ evidence_map.md                 ← 증거 지도 (★ 실측 후 채워야 함)
│     │  └─ report_template.md              ← 보고서 양식
│     └─ scripts/collect_evidence.py        ← 증거 수집기 본체
└─ scripts/collect_evidence.py              ← 런처 (§2에서 만든다)
```

메시아(fuoption)에 먼저 만든 같은 계열 스킬을 미륵이 사정에 맞게 다시 쓴 것이다. 옮겨온 것이
아니라 다시 썼다 — 런타임(py37_32/py310_64), 브로커(Cybos COM), 멀티PC 규약, 절대원칙 6종,
매분 9단계, 한시예외 3종이 전부 다르기 때문이다.

### 미륵이판에만 있는 것

| 기능 | 왜 |
|---|---|
| **날짜 토큰 자동탐색** | 로그 파일명을 모른 채 만들었다. `20260812`/`2026-08-12`/`260812`/`0812` 중 무엇이든 파일명에 있으면 찾아 분류한다 |
| **설정 불변식 검사** | `config/settings.py` 를 정규식으로 읽어 한시예외 3종·`MAX_CONTRACTS`·`HURST_*` 등이 여전히 의도한 값인지 자동 확인. **이게 이 스킬의 핵심 기능이다** |
| **매분 루프 커버리지** | 09:00~15:10 중 몇 분이 로그에 기록됐는지. 매분 파이프라인이라 결측 구간이 곧 사건이다 |
| **PC명 태그 규약 점검** | 최근 12커밋에 `[MW####]` 접두가 붙었는지 |
| **평문 로그 지원** | 미륵이는 JSON 로깅이 아닐 가능성이 높아 평문 `logging` 포맷도 파싱한다. cp949 인코딩도 시도 |
| **py3.7 호환** | f-string·walrus 미사용. `py37_32`에서도 돈다 |

---

## 2. 설치

```powershell
cd C:\Users\pc1\PycharmProjects\futures
# zip 을 리포 루트에 두고
python -c "import zipfile; zipfile.ZipFile('mireuk_dailycheck_install.zip').extractall('.')"
```

런처(`scripts/collect_evidence.py`)는 **zip에 포함돼 있다** — 별도로 만들 필요 없다.
본체를 그대로 실행하는 30줄짜리 껍데기이며, 로직은 들어 있지 않다.

압축을 풀었으면 바로 확인한다.

```powershell
python scripts/collect_evidence.py --discover
```

`No such file` 이 나오면 zip을 아직 안 풀었거나 리포 루트가 아닌 곳에서 풀린 것이다.
`dir .claude\skills\mireuk-daily-check` 로 확인하라. 런처 없이 본체를 직접 불러도 된다:

```powershell
python .claude\skills\mireuk-daily-check\scripts\collect_evidence.py --root . --discover
```

## 3. 검증 — 반드시 이 순서로

### 3-1. 인벤토리 확인 (가장 먼저)

```powershell
python scripts/collect_evidence.py --discover
python scripts/collect_evidence.py --discover --date 2026-08-11   # 확실히 돌았던 날
```

**§1 표에 로그 파일이 나오는가?**

- **나온다** → 3-2로.
- **"파일을 하나도 못 찾았다"** → 로그가 기본 스캔 경로 밖에 있다.
  실제 로그 폴더를 찾아 `config/dailycheck_targets.json` 을 만든다:
  ```json
  {"scan_dirs": ["logs", "log", "data/logs", "실제경로"], "scan_depth": 3}
  ```
- **파일명에 날짜가 없다** → 수집기가 못 찾는다. 이때는 `DEFAULT_CONFIG` 방식을 버리고
  메시아판처럼 **파일명 고정 목록**으로 바꾸는 편이 낫다. `discover_files()` 를 고쳐라.

### 3-2. 전체 실행

```powershell
python scripts/collect_evidence.py --phase post --date 2026-08-11 --out logs\_ev_test.md
```

확인할 것:

- [ ] **§3 설정 불변식** — `config/settings.py` 를 찾았는가. 각 상수의 현재값이 실제와 맞는가.
      `미발견`이 나오면 상수명이 바뀐 것이다 → `DEFAULT_CONFIG["invariants"]` 를 실제 이름으로 고쳐라.
      **기대값도 실제 운영값으로 맞춰라** — CLAUDE.md 기준으로 넣어뒀지만 그 사이 바뀌었을 수 있다.
- [ ] **§4 로그 다이제스트** — 레벨 집계가 그럴듯한가. `PLAIN` 만 잔뜩이면 레벨 정규식이 안 맞는 것이다.
      태그가 전부 `-` 면 로거명 패턴이 안 맞는 것이다 → `TAG_LOGGER_RE` / `TAG_BRACKET_RE` 조정.
- [ ] **§6 매분 루프 커버리지** — 정상일 날에 90%+ 가 나오는가. 0%면 시각 파싱이 실패한 것이다
      → `TIME_RE` 를 실제 로그 포맷에 맞춰라.
- [ ] **§6 앵커** — 15:10 강제청산·15:40 SHAP 심사가 잡히는가.
- [ ] **§9 정기점검 리포트** — `docs/정기점검/` 하위가 보이는가.
- [ ] 출력 크기가 30~60KB 범위인가. 100KB를 넘으면 `max_error_samples_per_tag`·`max_warn_tags` 를 줄여라.

### 3-3. 증거 지도 채우기

`references/evidence_map.md` §1 표가 **비어 있다.** 3-1에서 확인한 실제 파일 패턴으로 채우고
커밋하라. 그때부터 그 표가 진실원천이 된다.

### 3-4. 스킬 실전 1회

```
/dailycheck post 2026-08-11
```

보고서가 `docs/정기점검/매일점검/MW0602-20260811-점검리포트.md` 로 나오는지, 기존 관행
(`MW0601-20260731-점검리포트.md`)과 형식이 어울리는지 확인한다.

---

## 4. 커밋

```bash
git add .claude/ scripts/collect_evidence.py
git commit -m "[MW0602] {차수}차: 일일 점검 스킬 — 증거 수집기와 국면별 체크리스트"
```

세션 차수는 **원격(git) 기준**으로 맞춘다(392차 관행). `dev_memory/DECISION_LOG.md` 에도
`## 2026-08-1X (MW0602 {차수}차 — 일일 점검 스킬 도입)` 형식으로 남긴다.

MW0601은 `git pull` 로 받으면 그대로 쓴다 — 수집기가 호스트명에서 PC를 뽑으므로 설정 변경이 필요 없다.

---

## 5. 예약작업 (선택)

메시아(fuoption)에는 평일 08:45 / 12:30 / 16:10 KST 예약작업 3개를 걸어뒀다. 미륵이도 같은
방식이 가능하나 **주의**: 예약작업은 매번 새 클라우드 세션에서 시작하고, 폴더 접근 권한은
세션마다 새로 받아야 한다. 데스크톱 앱이 켜져 있으면 클릭 한 번, 꺼져 있으면 조용히 종료된다.

미륵이의 시각에 맞춘 권장 cron (UTC 기준, KST=UTC+9):

| 국면 | KST | cron (UTC) |
|---|---|---|
| 장전 | 평일 08:45 | `45 23 * * 0-4` |
| 장중 | 평일 12:30 | `30 3 * * 1-5` |
| 장후 | 평일 16:30 | `30 7 * * 1-5` |

장후를 16:30으로 잡은 이유: 15:40 자가학습 마감 + EOD 재학습이 끝날 여유를 준다.
재학습이 더 오래 걸리면 늦춰라.

---

## 6. 알려진 한계

- **경로 미검증** — §3을 건너뛰면 안 된다. 특히 `config/settings.py` 상수명.
- **DB 미조회** — STEP 9 예측 DB는 파일 인벤토리에만 잡히고 내용은 안 본다.
  진입 건수·승률·손절 준수율을 자동 집계하려면 수집기에 sqlite 조회 절을 추가해야 한다.
  **이게 가장 가치 있는 다음 확장이다** — 417차가 밝힌 대로 진짜 신호는 손절 준수율에 있다.
- **Cybos COM 상태 미확인** — 접속 여부를 로그로만 추정한다. 직접 조회하려면 py37_32에서
  COM을 열어야 하는데, 장중에 그러면 라이브 프로세스와 충돌할 수 있다. 권장하지 않는다.
- **한시예외 기대값이 CLAUDE.md 시점 기준** — 2026-08-12 이후 바뀌었다면 `불일치`가 뜬다.
  그때는 값이 틀린 게 아니라 이 문서가 낡은 것이다. `DEFAULT_CONFIG["invariants"]` 를 갱신하라.
