# 키움 OpenAPI+ TR 정보 조사 절차

## 핵심 원칙

**KOA Studio Q&A 게시판 웹 접근은 세션 없이 불가** — 대신 **로컬 설치 파일을 직접 읽는 것이 가장 빠르고 정확하다.**

---

## 1. 로컬 `.enc` 파일에서 TR 정의 직접 읽기 (최우선)

### 설치 경로
```
C:\OpenAPI\data\
```

### 파일 형식
- `.enc` 파일 = ZIP 압축 → 내부에 `.dat` 텍스트 파일
- 파일명 = TR 코드 소문자 (예: `opw20006.enc`)

### 읽는 방법
```python
import zipfile, sys
sys.stdout.reconfigure(encoding='utf-8')

with zipfile.ZipFile('C:/OpenAPI/data/opw20006.enc', 'r') as z:
    print(z.namelist())          # 내부 파일 목록 확인
    with z.open('OPW20006.dat') as f:
        print(f.read().decode('cp949'))
```

### `.dat` 파일 구조 예시 (OPW20006)
```
[TRINFO]
TRName=TDB3065_Q01
TRType=2

[INPUT]
@START_선옵잔고상세현황요청
    계좌번호    = 0,  10, -1
    비밀번호    = 10, 64, -1
    조회일자    = 74,  8, -1
    비밀번호입력매체구분 = 82, 2, -1
@END_선옵잔고상세현황요청

[OUTPUT]
@START_선옵잔고상세현황합계=*,*,*       ← 싱글 레코드명
    선물매도수량 = 0,  9, -1
    ...
    조회건수     = 84, 4, -1             ← 멀티 행 수 기준
@END_선옵잔고상세현황합계

@START_선옵잔고상세현황=*,4,조회건수    ← 멀티 레코드명
    종목코드 =   0,  8, -1
    종목명   =   8, 40, -1
    매매일자 =  48,  8, -1
    매매구분 =  56, 10, -1              ← "매수"=LONG, "매도"=SHORT
    잔고수량 =  66,  9, -1
    매입단가 =  75, 15, -1
    매매금액 =  90, 15, -1
    현재가   = 115, 15, -1
    평가손익 = 130, 15, -1
    손익율   = 145, 15, -1
    평가금액 = 160, 15, -1
@END_선옵잔고상세현황
```

**주의**: `@START_레코드명` — 이 이름이 `GetRepeatCnt(tr_code, 레코드명)` 에 그대로 사용된다.

---

## 2. 전체 TR 목록 확인

```python
import os
tr_files = [f for f in os.listdir('C:/OpenAPI/data/') if f.endswith('.enc')]
print(sorted(tr_files))
```

---

## 3. 키움 Q&A 게시판 접근 (보조 수단)

- URL: `https://www3.kiwoom.com/h/common/bbs/VBbsBoardBWOAZView`
- **POST 방식 + 세션 필요 → WebFetch로 직접 접근 불가**
- 검색 방법: 키움 홈 → 고객서비스 → Open API+ → Q&A 검색
- WebSearch로 캐시 페이지나 GitHub 구현체에서 간접 확인 가능

---

## 4. koapy 라이브러리 활용 (런타임 조회)

```python
from koapy.backend.kiwoom_open_api_plus.core.KiwoomOpenApiPlusTrInfo import KiwoomOpenApiPlusTrInfo
info = KiwoomOpenApiPlusTrInfo.get_trinfo_by_code("opw20006")
print(info)
```
koapy가 설치되어 있으면 이 방법으로도 TR 메타데이터 조회 가능.

---

## 5. OPW20006 조사로 발견한 함정

| 잘못된 내용 | 정확한 내용 | 출처 |
|---|---|---|
| 레코드명 `선옵잔고상세현**활**` | `선옭잔고상세현**황**` (況, 현황) | enc 파일 |
| CS 답변: "잔고수량 없음" | **잔고수량 존재** (offset 66) | enc 파일 |
| CS 답변: "매도수구분 없음" | 없음 맞음. 대신 **매매구분** 사용 | enc 파일 |
| `보유수량` 필드 | OPW20006에 **없음** | enc 파일 |

> **키움 CS 답변이 틀릴 수 있다** — enc 파일이 진실의 원천.

---

## 6. GetRepeatCnt / GetCommData 패턴

```python
# 싱글 데이터 (항상 1행)
cnt_single = kiwoom.GetRepeatCnt("OPW20006", "선옵잔고상세현황합계")  # 1

# 멀티 데이터 (포지션 수)
cnt_multi  = kiwoom.GetRepeatCnt("OPW20006", "선옵잔고상세현황")      # 0~N

# 필드 읽기 (rq_name은 SetInputValue 시 사용한 이름)
for i in range(cnt_multi):
    item_code  = kiwoom.GetCommData("OPW20006", "futures_balance", i, "종목코드").strip()
    trade_gubun = kiwoom.GetCommData("OPW20006", "futures_balance", i, "매매구분").strip()
    qty        = kiwoom.GetCommData("OPW20006", "futures_balance", i, "잔고수량").strip()
    # trade_gubun == "매수" → LONG, "매도" → SHORT
```

---

## 요약 체크리스트

TR 관련 문제 발생 시 순서:

1. `C:\OpenAPI\data\<tr코드소문자>.enc` 파일 존재 확인
2. `zipfile` 로 `.dat` 추출 → 레코드명·필드명·오프셋 직접 확인
3. `GetRepeatCnt(tr_code, 레코드명)` — 레코드명은 `.dat`의 `@START_` 뒤 이름 그대로
4. `GetCommData(tr_code, rq_name, index, 필드명)` — 필드명은 `.dat`의 탭 뒤 이름 그대로
5. CS 답변은 참고만 — **enc 파일이 최종 권위**
