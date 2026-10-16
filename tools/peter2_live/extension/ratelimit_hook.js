// 미륵이 피터2 수집기 — X 요청 한도 계측(페이지 MAIN world, document_start)
//
// 🔴 2026-10-16 — 수집 장애가 「X 검색 한도 15분 창 소진」으로 보였으나 **추정**이었다
//   (오류 군집 14–17분 주기 · 45초 새로고침에서 약 9분 뒤 소진 → 창당 약 12회).
//   추정으로 주기를 맞추지 말고 X 가 응답 헤더로 주는 실제 예산을 잰다.
//   docs/피터2수집/ 참조.
//
// 하는 일: 페이지의 fetch·XHR 를 감싸 GraphQL 타임라인 응답의
//   x-rate-limit-limit / -remaining / -reset 헤더와 상태코드를 읽어 window.postMessage 로
//   content.js(격리 world)에 넘긴다. 요청 본문·응답 본문은 건드리지 않는다(읽기만).
// 하지 않는 일: 요청을 막거나 바꾸지 않는다. 오류를 삼키지 않는다(원래 동작 그대로 반환).
(function () {
  if (window.__peter2RlHooked) return;
  window.__peter2RlHooked = true;

  // 한도를 재는 대상 — 검색(SearchTimeline)과 프로필(UserTweets)은 예산이 따로다
  const OPS = /\/graphql\/[^/]+\/(SearchTimeline|UserTweets|UserTweetsAndReplies)\b/;
  const LOAD_MS = 8000;    // 페이지 로드 직후 이 안에 나간 요청 = 새로고침이 부른 것, 이후 = X 자체 폴링

  let n = 0;                 // 이 페이지에서 본 타임라인 응답 수(load + poll)

  function report(url, status, get) {
    const m = OPS.exec(url || "");
    if (!m) return;
    const num = (h) => { const v = get(h); return v == null || v === "" ? null : Number(v); };
    n += 1;
    const d = {
      source: "peter2-rl",
      op: m[1],
      status: status,
      lim: num("x-rate-limit-limit"),
      rem: num("x-rate-limit-remaining"),
      reset: num("x-rate-limit-reset"),     // unix 초
      phase: performance.now() < LOAD_MS ? "load" : "poll",
      n_page: n,
      at: Date.now(),
    };
    try {
      // content.js 는 document_idle 에 붙는다 — 그 전에 온 첫 응답(새로고침 직후)을 놓치지 않도록
      // 두 world 가 함께 보는 DOM 에도 마지막 값을 남긴다.
      document.documentElement.setAttribute("data-peter2-rl", JSON.stringify(d));
      window.postMessage(d, location.origin);
    } catch (e) { /* 계측 실패가 페이지를 깨면 안 된다 */ }
  }

  const _fetch = window.fetch;
  if (typeof _fetch === "function") {
    window.fetch = function (input, init) {
      const url = typeof input === "string" ? input : (input && input.url) || "";
      const p = _fetch.apply(this, arguments);
      p.then((r) => { try { report(url, r.status, (h) => r.headers.get(h)); } catch (e) {} },
             () => {});
      return p;
    };
  }

  const XO = XMLHttpRequest.prototype.open;
  const XS = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url) {
    this.__p2url = url;
    return XO.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function () {
    const x = this;
    if (OPS.test(x.__p2url || "")) {
      x.addEventListener("loadend", function () {
        try { report(x.__p2url, x.status, (h) => x.getResponseHeader(h)); } catch (e) {}
      });
    }
    return XS.apply(this, arguments);
  };
})();
