// 미륵이 피터2 수집기 — X 검색 페이지에서 트윗을 읽는다(읽기 전용).
//
// 페이지 타이머는 백그라운드 탭에서 분당 1회로 묶이므로 쓰지 않는다. 대신 DOM 변화(MutationObserver)를
// 보고, 트윗 article 이 나타나면 그때 모아서 보낸다. 새로고침 주기는 background.js 가 쥔다.
// 수집 규칙은 peter-daily 스킬의 window.C() 와 같다 — id·시각(datetime)·본문.
//
// 🔴 2026-10-08 — 자격 검사는 **주입 시점 1회뿐**이었다.
//   X 는 SPA 라 페이지를 새로 읽지 않고 주소만 /home 으로 바꾸는 일이 있다. 그러면 이 스크립트는
//   계속 살아서 **홈 타임라인을 검색 결과인 양** 보냈다(그날 하트비트 `url=https://x.com/home`).
//   홈은 알고리즘 정렬이라 장중 구간의 **전수 보장이 없다** — 조용히 표본이 비는 길이다.
//   ⇒ 보낼 때마다 자격을 다시 보고, 벗어났으면 **수집 대신 이탈을 신고**한다(계측 4원칙 ②·④).

(function () {
  const OFF_REPORT_SEC = 30;        // 이탈 신고는 30초에 한 번 — 되돌리는 건 background 가 한다

  const sent = new Set();
  let cycle = 0;
  let timer = null;
  let lastOff = 0;

  // 지금 이 페이지가 「우리 검색 결과」인가. 주입 시점이 아니라 **매번** 묻는다.
  function offSearch() {
    return location.pathname.indexOf("/search") !== 0
        || !/from(%3A|:)PeterLeejoa/i.test(location.href);
  }

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
    // 🔴 종전에는 document.body 전체를 봤다. 오른쪽 트렌드 패널이 제 사정으로 띄우는
    //    「문제가 발생했습니다 … 다시 시도」가 걸려 **멀쩡한 페이지를 오류로 신고**했고,
    //    background 가 15분 물러났다(2026-10-08 PAGE_ERROR 다발). 본문 칸만 본다.
    const main = document.querySelector('[data-testid="primaryColumn"]') || document.body;
    const body = (main && main.innerText) || "";
    if (/Something went wrong|다시 시도|문제가 발생|Rate limit|속도 제한/i.test(body)
        && !main.querySelector("article")) {
      return body.slice(0, 80);
    }
    if (/로그인|Log in|Sign in/i.test(body) && !main.querySelector("article")) {
      return "login_required";
    }
    return null;
  }

  function send(force) {
    cycle += 1;

    if (offSearch()) {
      // 자격을 잃었다 — 홈 타임라인을 긁어 보내지 않는다. 사실만 알린다.
      const now = Date.now();
      if (now - lastOff < OFF_REPORT_SEC * 1000) return;
      lastOff = now;
      chrome.runtime.sendMessage({
        type: "peter2_tweets", tweets: [],
        // off_search 는 error 가 아니다 — background 는 물러나는 대신 탭을 되돌린다
        meta: { url: location.href, articles: 0, cycle: cycle, error: null, off_search: true },
      }, function () {});
      return;
    }

    const all = collect();
    const fresh = all.filter((t) => !sent.has(t.id + ":" + t.text.length));
    const meta = { url: location.href, articles: all.length, cycle: cycle,
                   error: pageError(), off_search: false };
    if (!fresh.length && !force) return;
    chrome.runtime.sendMessage({ type: "peter2_tweets", tweets: fresh, meta: meta }, (r) => {
      if (r && r.ok) for (const t of fresh) sent.add(t.id + ":" + t.text.length);
    });
  }

  // 「새 게시물 보기」 알약이 뜨면 누른다(새로고침 사이에 들어온 글)
  function clickPill() {
    if (offSearch()) return;
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
  setInterval(() => send(true), 5000);
})();
