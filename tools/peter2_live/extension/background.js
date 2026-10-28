// 미륵이 피터2 수집기 — 서비스워커
//
// 하는 일
//   1) 평일 08:30–15:45(KST) 동안 오늘 장중 구간으로 좁힌 X 검색 탭을 하나 유지한다(고정 탭, 비활성).
//   2) 그 탭을 RELOAD_SEC(80초) 마다 새로고침한다 — 백그라운드 탭의 페이지 타이머는 Chrome 이 분당 1회로
//      묶어 버리므로(intensive throttling), 갱신 주기는 여기(알람)가 쥔다.
//   3) content.js 가 모은 트윗을 127.0.0.1:8766/peter 로 보낸다(확장 출처라 CORS 제약이 없다).
//
// 하지 않는 일: 글쓰기·좋아요·팔로우 등 어떤 계정 행동도 하지 않는다. 읽기만 한다.
//
// 🔴 2026-10-08 — 탭이 무한히 늘어났다. 원인과 대책을 여기 적어둔다.
//   종전 ourTab() 은 탭을 **URL 로** 찾았다(`tabs.query({url:"https://x.com/search*"})`).
//   그런데 X 는 SPA 라 **페이지 이동 없이** 주소만 /home 으로 바꿔버리는 일이 있다. 그 순간
//   탭은 멀쩡히 살아 있는데 질의에 안 잡히므로 ensureTab() 이 「탭이 없다」고 판단해 **새로 만든다.**
//   새 탭도 같은 일을 겪으므로 틱마다(15~30초) 한 장씩 쌓인다. 닫는 코드는 없었다.
//   실측 증거: `collector.json` 의 `url` 이 `https://x.com/home` — 즉 수집은 돌고 있었으나
//   출처가 검색 결과가 아니라 **홈 타임라인**이었다(2026-10-08 13:46 하트비트).
//   ⇒ ① 탭을 **tabId 로** 추적한다 ② 주소가 밀리면 새로 만들지 말고 **제자리로 되돌린다**
//      ③ 우리 것이 확실한 여분 탭은 거둬들인다 ④ content.js 가 이탈을 스스로 신고한다.

const RECEIVER = "http://127.0.0.1:8766/peter";
const HANDLE = "PeterLeejoa";
// [2026-10-08 점검] 종전 15초(오류 시 30초)는 X 검색 한도를 15분마다 소진했다 — 수신기 로그 실측
// PAGE_ERROR 791건이 :07–:10 · :22–:25 · :37–:40 · :52–:55 에 3–4분씩 몰렸다(15분 창 한도 패턴).
// 게다가 오류 하트비트가 5초마다 백오프를 15분씩 연장해 하루 종일 30초 모드였고, 그 사각에 들어온
// 트윗은 지연 98–200초로 잡혔다(평시 지연 중앙 ~20초). 한도 아래로 일정하게 도는 쪽이 낫다.
// [2026-10-16] 45초로도 한도를 매 창 소진했다 — 10-12–10-16 오류 군집이 14–17분 주기로 4–8분씩,
// 10-16 은 세션 분의 41%. 45초에서 약 9분(≈12회) 뒤 소진되므로 창당 예산 ≈ 12회로 추정 → 80초(창당 11회).
// ⚠ 추정이다. ratelimit_hook.js 가 실제 헤더(x-rate-limit-*)를 재서 수신기 로그 RATE 줄에 남긴다 —
//   그 실측으로 이 값을 다시 정할 것. 근거·절차: docs/피터2수집/.
const RELOAD_SEC = 80;           // 평시 — 15분에 약 11회
const BACKOFF_SEC = 120;         // 오류 화면인데 한도 헤더가 없을 때의 대기(종전 동작)
const RESET_PAD_SEC = 5;         // 한도 reset 시각 뒤 여유
const BACKOFF_MAX_SEC = 16 * 60; // reset 값이 이상해도 이보다 오래 멈추지 않는다(창 15분 + 여유)

// 오류 화면에서 얼마나 물러날지. 한도 헤더가 「소진(rem=0 또는 429)」을 말하면 **reset 시각까지**
// 기다린다 — 소진된 창에서 120초마다 재시도해 봐야 오류 화면만 다시 받는다(F-3).
// 헤더가 없으면(미측정) 종전 120초 그대로 — 모르는 값으로 길게 멈추지 않는다.
function backoffMsFor(meta, now) {
  const rl = meta && meta.rl;
  const spent = rl && (rl.status === 429 || rl.rem === 0);
  if (spent && rl.reset > 0) {
    const until = rl.reset * 1000 + RESET_PAD_SEC * 1000;
    return Math.min(Math.max(until - now, 30 * 1000), BACKOFF_MAX_SEC * 1000);
  }
  return BACKOFF_SEC * 1000;
}

function kstNow() {
  const d = new Date(Date.now() + 9 * 3600 * 1000);
  return { y: d.getUTCFullYear(), m: d.getUTCMonth(), d: d.getUTCDate(),
           hm: d.getUTCHours() * 100 + d.getUTCMinutes(), wd: d.getUTCDay() };
}

function kstUnix(k, hh, mm) {
  return Math.floor((Date.UTC(k.y, k.m, k.d, hh, mm) - 9 * 3600 * 1000) / 1000);
}

function searchUrl() {
  const k = kstNow();
  const s = kstUnix(k, 8, 30), e = kstUnix(k, 15, 45);
  const q = encodeURIComponent(`from:${HANDLE} since_time:${s} until_time:${e}`);
  return { url: `https://x.com/search?q=${q}&src=typed_query&f=live`, since: s };
}

function inSession() {
  const k = kstNow();
  return k.wd >= 1 && k.wd <= 5 && k.hm >= 830 && k.hm <= 1545;
}

// 우리가 만든 탭인지 — 사람이 직접 연 검색 탭과 구분한다.
// `since_time:` 은 사람이 손으로 치는 값이 아니므로 소유 표식으로 쓸 수 있다.
function isOurUrl(u) {
  u = u || "";
  return u.indexOf("https://x.com/search") === 0
      && /from(%3A|:)PeterLeejoa/i.test(u)
      && /since_time(%3A|:)\d+/.test(u);
}

// 피터 페이지(우리 검색·그의 프로필·트윗 상세)인가. 고정 탭 거두기(③)와 탭 계수에 쓴다.
// 사람이 피터 페이지를 손으로 **고정**해 둘 일은 드물다 — 고정 + 피터 = 우리 탭이었던 것.
function isPeterUrl(u) {
  u = u || "";
  return u.indexOf("https://x.com/") === 0
      && (/from(%3A|:)PeterLeejoa/i.test(u) || /^https:\/\/x\.com\/PeterLeejoa(\/|\?|#|$)/i.test(u));
}

// 지금 세션의 검색 페이지에 제대로 서 있는가
function onStation(t) {
  const want = searchUrl();
  const u = (t && (t.url || t.pendingUrl)) || "";
  return isOurUrl(u) && u.indexOf(`since_time%3A${want.since}`) >= 0;
}

async function getTabId() {
  const { tabId = null } = await chrome.storage.local.get("tabId");
  return tabId;
}

async function setTabId(id) {
  await chrome.storage.local.set({ tabId: id });
}

async function ourTab() {
  // ① 기억해 둔 id 로 먼저 찾는다 — 주소가 밀려도 탭은 그대로다
  const id = await getTabId();
  if (id != null) {
    try {
      const t = await chrome.tabs.get(id);
      // 사람이 고정을 풀었다면 그 탭은 사람이 쓰겠다는 뜻이다 — 손대지 않고 놓아준다
      if (t && t.pinned && (t.url || t.pendingUrl || "").indexOf("https://x.com/") === 0) return t;
      if (t) await setTabId(null);
    } catch (e) { await setTabId(null); }   // 사용자가 닫았다
  }
  // ② 서비스워커가 재시작돼 id 를 잃었으면 URL 로 한 번 더 찾는다
  for (const t of await chrome.tabs.query({ url: "https://x.com/search*" })) {
    if (onStation(t)) { await setTabId(t.id); return t; }
  }
  // ③ [2026-10-28] Chrome 은 시작 설정과 무관하게 **고정 탭을 복원한다.** 어제 그 탭이 검색이 아니라
  //    트윗 상세(`/PeterLeejoa/status/…`)에 서 있었으면 ①(id 는 재시작으로 바뀜)·②(search* 만 조회)가
  //    못 알아보고 새로 만들어 **X 고정 탭이 둘**이 됐다(10-27 19:21 클릭 → 10-28 08:44 복원 · 08:45 신규).
  //    고정된 피터 탭을 거두어 쓴다 — ensureTab() 이 제자리로 되돌린다.
  for (const t of await chrome.tabs.query({ pinned: true, url: "https://x.com/*" })) {
    if (isPeterUrl(t.url || t.pendingUrl)) { await setTabId(t.id); return t; }
  }
  return null;
}

// 우리 것이 확실한 여분 탭을 거둔다. 사람이 연 검색 탭(`since_time` 없음)은 건드리지 않는다.
// [2026-10-28] 고정된 피터 탭(③과 같은 표식)도 여분이면 거둔다 — 복원이 두 장을 살린 경우.
async function reapStrays() {
  const keep = await getTabId();
  for (const t of await chrome.tabs.query({ url: "https://x.com/*" })) {
    if (t.id === keep) continue;
    const u = t.url || t.pendingUrl || "";
    if (!isOurUrl(u) && !(t.pinned && isPeterUrl(u))) continue;
    try { await chrome.tabs.remove(t.id); } catch (e) { /* 이미 닫혔다 */ }
  }
}

async function ensureTab() {
  if (!inSession()) return null;
  // 거두기(③)가 정리보다 먼저다 — 먼저 정리하면 복원된 어제 검색 탭을 닫고 새로 만든다(헛 교체)
  let t = await ourTab();
  await reapStrays();
  if (!t) {
    t = await chrome.tabs.create({ url: searchUrl().url, active: false, pinned: true });
    await setTabId(t.id);
    return null;            // 방금 열었다 — 이번 틱은 새로고침하지 않는다
  }
  if (!onStation(t)) {
    // 🔴 탭은 살아 있는데 주소가 밀렸다(X 의 SPA 이동, 날짜 경계 등).
    //    새 탭을 만들면 여기서 증식이 시작된다 — 만들지 말고 제자리로 되돌린다.
    try { await chrome.tabs.update(t.id, { url: searchUrl().url }); } catch (e) { await setTabId(null); }
    return null;            // 방금 이동시켰다 — 겹쳐서 새로고침하지 않는다
  }
  return t;
}

async function reloadOnce() {
  if (!inSession()) return;
  const t = await ensureTab();
  if (t && t.status !== "loading") {
    try { await chrome.tabs.reload(t.id, { bypassCache: false }); } catch (e) { /* 탭이 닫혔다 */ }
  }
}

async function tick() {
  const { backoffUntil = 0 } = await chrome.storage.local.get("backoffUntil");
  if (Date.now() < backoffUntil) return;   // 오류 화면 — 새로고침도 한도를 먹는다
  await reloadOnce();
}

function arm() {
  chrome.alarms.create("peter2", { periodInMinutes: RELOAD_SEC / 60 });
}
chrome.runtime.onInstalled.addListener(arm);
chrome.runtime.onStartup.addListener(arm);
chrome.alarms.onAlarm.addListener((a) => { if (a.name === "peter2") tick(); });

// [2026-10-28] 수집 탭 안에서 사람이 누르면 그 탭이 딴 데로 빠진다(실측 10-20 12:18 · 10-21 08:56 ·
//   10-27 19:21 · 10-28 09:41). 장중엔 이탈 신고로 되돌아왔지만 **장 밖엔 아무도 안 되돌려**
//   그 상태로 밤새 종료 → 다음 날 Chrome 이 그 고정 탭을 복원했다(→ ourTab ③).
//   ⇒ 누른 페이지는 **일반 탭으로 따로 열어 주고**, 수집 탭은 장 시간과 무관하게 검색으로 되돌린다.
//   `/home` 은 사람이 아니라 X SPA 가 스스로 미는 주소다(10-08) — 새 탭을 만들지 않는다(증식 금지).
const HANDOFF_MIN_MS = 3000;     // 같은 클릭의 연쇄 갱신(주소가 두세 번 바뀐다)을 한 번으로
const RETURN_MIN_MS = 30000;     // 되돌리기도 검색 한도를 먹는다 — X 가 계속 밀어도 30초에 한 번만
let lastHandoff = 0;
let lastReturn = 0;

function isHandoffUrl(u) {
  if ((u || "").indexOf("https://x.com/") !== 0) return false;
  const path = u.slice("https://x.com".length).split(/[?#]/)[0];
  return !(path === "/" || path === "" || path.indexOf("/home") === 0 || path.indexOf("/search") === 0);
}

chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (!info.url) return;
  if (tabId !== await getTabId()) return;
  if (!tab || !tab.pinned) return;          // 사람이 고정을 풀었다 — 그 탭은 사람 것이다
  if (onStation(tab)) return;               // 우리가 되돌린 결과(또는 정상 이동)
  const now = Date.now();
  if (isHandoffUrl(info.url) && now - lastHandoff >= HANDOFF_MIN_MS) {
    lastHandoff = now;
    // 일반(비고정) 탭이라 reapStrays·ourTab ③ 의 대상이 아니다 — 사람이 닫을 때까지 그대로 둔다
    try { await chrome.tabs.create({ url: info.url, active: true, pinned: false, index: tab.index + 1 }); }
    catch (e) { /* 창이 닫히는 중 */ }
  }
  if (now - lastReturn < RETURN_MIN_MS) return;   // 나머지는 다음 틱의 ensureTab() 이 맡는다
  lastReturn = now;
  try { await chrome.tabs.update(tabId, { url: searchUrl().url }); } catch (e) { await setTabId(null); }
});

// [2026-10-28] X 탭 계수 — 하트비트에 실어 「X 가 두 개 떴다」를 사람 눈이 아니라 점검이 잡게 한다.
//   peter_pinned 가 1 을 넘으면 복원 중복이다. 조회 실패는 null(미측정 ≠ 0, 계측 4원칙 ②).
async function tabCensus() {
  try {
    const xs = await chrome.tabs.query({ url: "https://x.com/*" });
    return { x: xs.length,
             x_pinned: xs.filter((t) => t.pinned).length,
             peter_pinned: xs.filter((t) => t.pinned && isPeterUrl(t.url || t.pendingUrl)).length };
  } catch (e) { return null; }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== "peter2_tweets") return false;
  (async () => {
    // 이탈 신고는 「오류」가 아니다 — 물러나는 게 아니라 **되돌려야** 한다(dev 611차 후속3)
    if (msg.meta && msg.meta.off_search) {
      if (sender && sender.tab && sender.tab.id != null) await setTabId(sender.tab.id);
      await ensureTab();
    } else if (msg.meta && msg.meta.error) {
      // 이미 물러나 있으면 연장하지 않는다 — 오류 화면은 5초마다 하트비트를 보내므로,
      // 연장하면 새로고침이 영영 재개되지 않는다(종전 코드가 하루 종일 저속 모드였던 이유).
      const { backoffUntil = 0 } = await chrome.storage.local.get("backoffUntil");
      if (Date.now() >= backoffUntil) {
        const now = Date.now();
        await chrome.storage.local.set({ backoffUntil: now + backoffMsFor(msg.meta, now) });
      }
    }
    // [2026-10-28 G-10] ext_ver — 수신기가 「지금 Chrome 에 실린 확장이 몇 판인가」를 로그로 남긴다.
    // 없으면(1.2.0 이하) 재로드 반영 여부를 chrome://extensions 를 열어 봐야만 알 수 있었다.
    const meta = Object.assign({}, msg.meta || {}, {
      tabs: await tabCensus(),
      ext_ver: chrome.runtime.getManifest().version,
    });
    try {
      const r = await fetch(RECEIVER, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tweets: msg.tweets || [], meta: meta }),
      });
      sendResponse({ ok: r.ok, status: r.status });
    } catch (e) {
      sendResponse({ ok: false, error: String(e) });   // 수신기 미기동 — 미륵이 쪽 하트비트 경보가 잡는다
    }
  })();
  return true;   // 비동기 응답
});
