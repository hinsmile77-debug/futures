// 미륵이 피터2 수집기 — X 검색 페이지에서 트윗을 읽는다(읽기 전용).
//
// 페이지 타이머는 백그라운드 탭에서 분당 1회로 묶이므로 쓰지 않는다. 대신 DOM 변화(MutationObserver)를
// 보고, 트윗 article 이 나타나면 그때 모아서 보낸다. 새로고침 주기는 background.js 가 쥔다.
// 수집 규칙은 peter-daily 스킬의 window.C() 와 같다 — id·시각(datetime)·본문.

(function () {
  if (!/from(%3A|:)PeterLeejoa/i.test(location.href)) return;

  const sent = new Set();
  let cycle = 0;
  let timer = null;

  function collect() {
    const out = [];
    for (const a of document.querySelectorAll("article")) {
      const t = a.querySelector("time");
      if (!t) continue;
      const h = (t.closest("a") && t.closest("a").getAttribute("href")) || "";
      const id = h.split("/status/")[1];
      if (!id) continue;
      const tid = id.split(/[/?]/)[0];
      // 인용·리트윗 안의 남의 글은 빼고 그의 글만 — 링크가 /PeterLeejoa/status/ 여야 한다
      if (!/\/PeterLeejoa\/status\//i.test(h)) continue;
      const x = (a.querySelector('[data-testid="tweetText"]') || {}).innerText || "";
      out.push({ id: tid, dt: t.getAttribute("datetime"), text: x });
    }
    return out;
  }

  function pageError() {
    const body = (document.body && document.body.innerText) || "";
    if (/Something went wrong|다시 시도|문제가 발생|Rate limit|속도 제한/i.test(body)
        && !document.querySelector("article")) {
      return body.slice(0, 80);
    }
    if (/로그인|Log in|Sign in/i.test(body) && !document.querySelector("article")) {
      return "login_required";
    }
    return null;
  }

  // 확장이 재로드·갱신되면 이 탭에 남은 옛 스크립트는 「고아」가 된다 — chrome.runtime 이 끊겨
  // sendMessage 가 "Extension context invalidated" 를 던진다(5초 하트비트마다 반복).
  // 끊긴 것을 알면 관찰자·타이머를 걷고 조용히 물러난다. 다음 탭 새로고침이 새 스크립트를 심는다.
  let hb = null;
  function alive() {
    try { return !!(chrome.runtime && chrome.runtime.id); } catch (e) { return false; }
  }
  function teardown() {
    try { obs.disconnect(); } catch (e) {}
    if (hb) { clearInterval(hb); hb = null; }
  }

  function send(force) {
    if (!alive()) { teardown(); return; }
    cycle += 1;
    const all = collect();
    const fresh = all.filter((t) => !sent.has(t.id + ":" + t.text.length));
    const meta = { url: location.href, articles: all.length, cycle: cycle, error: pageError() };
    if (!fresh.length && !force) return;
    try {
      chrome.runtime.sendMessage({ type: "peter2_tweets", tweets: fresh, meta: meta }, (r) => {
        void chrome.runtime.lastError;   // 서비스워커 재기동 틈의 「수신자 없음」은 다음 주기가 메운다
        if (r && r.ok) for (const t of fresh) sent.add(t.id + ":" + t.text.length);
      });
    } catch (e) {
      teardown();                        // Extension context invalidated
    }
  }

  // 「새 게시물 보기」 알약이 뜨면 누른다(새로고침 사이에 들어온 글)
  function clickPill() {
    const pill = document.querySelector('[data-testid="pillLabel"]');
    if (pill) { try { pill.click(); } catch (e) {} }
  }

  const obs = new MutationObserver(() => {
    clickPill();
    if (timer) return;
    // 같은 틱의 연쇄 변경을 한 번으로 묶는다(마이크로태스크 — 타이머 스로틀 영향 없음)
    timer = Promise.resolve().then(() => { timer = null; send(false); });
  });
  obs.observe(document.documentElement, { childList: true, subtree: true });

  // 로드 직후 1회는 무조건 보낸다 — 새 트윗이 없어도 하트비트가 된다
  window.addEventListener("load", () => send(true));
  if (document.readyState === "complete") send(true);
  // 화면이 보일 때는 5초마다 하트비트(보이지 않으면 Chrome 이 늦추지만 새로고침이 대신한다)
  hb = setInterval(() => send(true), 5000);
})();
