// 미륵이 피터2 수집기 — 서비스워커
//
// 하는 일
//   1) 평일 08:30–15:45(KST) 동안 오늘 장중 구간으로 좁힌 X 검색 탭을 하나 유지한다(고정 탭, 비활성).
//   2) 그 탭을 RELOAD_SEC(45초) 마다 새로고침한다 — 백그라운드 탭의 페이지 타이머는 Chrome 이 분당 1회로
//      묶어 버리므로(intensive throttling), 갱신 주기는 여기(알람)가 쥔다.
//   3) content.js 가 모은 트윗을 127.0.0.1:8766/peter 로 보낸다(확장 출처라 CORS 제약이 없다).
//
// 하지 않는 일: 글쓰기·좋아요·팔로우 등 어떤 계정 행동도 하지 않는다. 읽기만 한다.

const RECEIVER = "http://127.0.0.1:8766/peter";
const HANDLE = "PeterLeejoa";
// [2026-10-08 점검] 종전 15초(오류 시 30초)는 X 검색 한도를 15분마다 소진했다 — 수신기 로그 실측
// PAGE_ERROR 791건이 :07–:10 · :22–:25 · :37–:40 · :52–:55 에 3–4분씩 몰렸다(15분 창 한도 패턴).
// 게다가 오류 하트비트가 5초마다 백오프를 15분씩 연장해 하루 종일 30초 모드였고, 그 사각에 들어온
// 트윗은 지연 98–200초로 잡혔다(평시 지연 중앙 ~20초). 한도 아래로 일정하게 도는 쪽이 낫다.
const RELOAD_SEC = 45;           // 평시 — 15분에 20회
const BACKOFF_SEC = 120;         // 오류 화면이면 새로고침을 멈추고 기다린다(창이 풀릴 시간)

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

async function ourTab() {
  const tabs = await chrome.tabs.query({ url: "https://x.com/search*" });
  const want = searchUrl();
  for (const t of tabs) {
    if ((t.url || "").includes(`since_time%3A${want.since}`)) return t;
  }
  return null;
}

async function ensureTab() {
  if (!inSession()) return null;
  let t = await ourTab();
  if (!t) {
    t = await chrome.tabs.create({ url: searchUrl().url, active: false, pinned: true });
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

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== "peter2_tweets") return false;
  (async () => {
    if (msg.meta && msg.meta.error) {
      // 이미 물러나 있으면 연장하지 않는다 — 오류 화면은 5초마다 하트비트를 보내므로,
      // 연장하면 새로고침이 영영 재개되지 않는다(종전 코드가 하루 종일 저속 모드였던 이유).
      const { backoffUntil = 0 } = await chrome.storage.local.get("backoffUntil");
      if (Date.now() >= backoffUntil) {
        await chrome.storage.local.set({ backoffUntil: Date.now() + BACKOFF_SEC * 1000 });
      }
    }
    try {
      const r = await fetch(RECEIVER, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tweets: msg.tweets || [], meta: msg.meta || {} }),
      });
      sendResponse({ ok: r.ok, status: r.status });
    } catch (e) {
      sendResponse({ ok: false, error: String(e) });   // 수신기 미기동 — 미륵이 쪽 하트비트 경보가 잡는다
    }
  })();
  return true;   // 비동기 응답
});
