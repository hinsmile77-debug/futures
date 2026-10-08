// 미륵이 피터2 수집기 — 서비스워커
//
// 하는 일
//   1) 평일 08:30–15:45(KST) 동안 오늘 장중 구간으로 좁힌 X 검색 탭을 하나 유지한다(고정 탭, 비활성).
//   2) 그 탭을 RELOAD_SEC 마다 새로고침한다 — 백그라운드 탭의 페이지 타이머는 Chrome 이 분당 1회로
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
const RELOAD_SEC_FAST = 15;      // 평시
const RELOAD_SEC_SLOW = 30;      // X 가 오류·제한 화면을 띄우면 15분간 물러난다
const BACKOFF_MIN = 15;

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
  return null;
}

// 우리 것이 확실한 여분 탭을 거둔다. 사람이 연 검색 탭(`since_time` 없음)은 건드리지 않는다.
async function reapStrays() {
  const keep = await getTabId();
  for (const t of await chrome.tabs.query({ url: "https://x.com/search*" })) {
    if (t.id === keep) continue;
    if (!isOurUrl(t.url || t.pendingUrl || "")) continue;
    try { await chrome.tabs.remove(t.id); } catch (e) { /* 이미 닫혔다 */ }
  }
}

async function ensureTab() {
  if (!inSession()) return null;
  await reapStrays();
  let t = await ourTab();
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
  const slow = Date.now() < backoffUntil;
  await reloadOnce();
  if (!slow) {
    // 서비스워커는 이벤트 뒤 약 30초 산다 — 그 안에서 한 번 더 돌려 15초 주기를 만든다
    setTimeout(reloadOnce, RELOAD_SEC_FAST * 1000);
  }
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create("peter2", { periodInMinutes: RELOAD_SEC_SLOW / 60 });
});
chrome.runtime.onStartup.addListener(() => {
  chrome.alarms.create("peter2", { periodInMinutes: RELOAD_SEC_SLOW / 60 });
});
chrome.alarms.onAlarm.addListener((a) => { if (a.name === "peter2") tick(); });

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== "peter2_tweets") return false;
  (async () => {
    // 이탈 신고는 「오류」가 아니다 — 물러나는 게 아니라 **되돌려야** 한다
    if (msg.meta && msg.meta.off_search) {
      if (sender && sender.tab && sender.tab.id != null) await setTabId(sender.tab.id);
      await ensureTab();
    } else if (msg.meta && msg.meta.error) {
      await chrome.storage.local.set({ backoffUntil: Date.now() + BACKOFF_MIN * 60 * 1000 });
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
