# CYBOS 기준 PCR·GEX·ATM OI 안정 구현 경로

작성일: 2026-05-13  
범위: KOSPI200 옵션 체인 기반 PCR(OI) / GEX / ATM OI 산출

---

## 1) 결론 요약

Cybos Plus에서 다음 조합이 가장 안정적이다.

- 체인(종목 마스터): `CpUtil.CpOptionCode`
- 종목별 스냅샷(가격/OI/그릭스/잔존일/금리): `Dscbo1.OptionMst`
- OI 실시간 갱신: `Dscbo1.OptionMo`
- 그릭스 재계산(보정/검증): `CpUtil.CpCalcOptGreeks`

핵심 원칙:

1. OI 증감은 서버 필드 단일 의존보다 `현재 OI - 전일 OI` 차분을 기본으로 사용
2. 장중 OI는 잠정/확정 구분값을 함께 저장
3. 실시간 파이프라인은 OI(`OptionMo`)와 가격/체결(`OptionMst` 주기 재조회 또는 실시간 현재가 객체)을 분리

---

## 2) 요구사항별 매핑

### A. 옵션 종목 코드 체인 조회

- 객체: `CpOptionCode`
- 방법:
  - `GetCount()`
  - `GetData(type, index)`
- 주요 필드:
  - `type=0`: 옵션코드
  - `type=2`: 콜/풋 구분
  - `type=3`: 행사월
  - `type=4`: 행사가

### B. 행사가별 콜/풋 현재가

- 기본 객체: `OptionMst`
- 필드: `GetHeaderValue(93)` (현재가)

### C. 행사가별 미결제약정(OI)

- 기본 객체: `OptionMst`
- 필드:
  - `GetHeaderValue(99)`: 현재 미결제약정수량
  - `GetHeaderValue(37)`: 전일 미결제약정수량
  - `GetHeaderValue(100)`: OI 구분(전일확정/당일잠정/당일확정)
- 실시간 갱신 객체: `OptionMo`
  - 설명상 OptionMst 99 연동

### D. 거래량(가능하면)

- 객체: `OptionMst`
- 필드: `GetHeaderValue(97)` (누적체결수량)

### E. GEX용 gamma 또는 계산 입력값

- 직접 사용(권장 1순위): `OptionMst`
  - `GetHeaderValue(110)`: Gamma
  - `GetHeaderValue(109)`: Delta
  - `GetHeaderValue(111~113)`: Theta/Vega/Rho
  - `GetHeaderValue(115)`: 변동성
- 계산 보정(권장 2순위): `CpCalcOptGreeks`
  - 입력: 콜풋, 옵션가격, 기초가격, 행사가, 변동성, 잔존일수, 무위험이자율, 배당
  - 출력: TV/Delta/Gamma/Theta/Vega/Rho/IV
- OptionMst 보조 입력 필드:
  - `GetHeaderValue(13)`: 잔존일수
  - `GetHeaderValue(36)`: CD금리(무위험 이자율)
  - `GetHeaderValue(53)`: 내재변동성(증거금 계산용)

---

## 3) 안정 구현 아키텍처

## STEP 0. 환경/전제

- Windows + 32-bit Python(Conda `py37_32`)
- Cybos Plus 로그인 및 `CpUtil.CpCybos.IsConnect == 1`

## STEP 1. 체인 스냅샷 빌드

1. `CpOptionCode` 전체 순회
2. 레코드화: `{code, call_put, ym, strike}`
3. 대상 만기 필터(근월/차근월 등)

## STEP 2. 종목별 스냅샷 수집

각 옵션 코드마다 `OptionMst` 1회 요청:

- 가격/체결: 93, 97
- OI: 99, 37, 100
- Greek/Vol: 109, 110, 111, 112, 113, 115
- 계산 보조: 13, 36, 15(ATM 구분)

저장 권장 키:

- `trade_date, trade_time, code, ym, strike, cp`

## STEP 3. 실시간 갱신

- OI: `OptionMo.Subscribe(code)`
- 가격/거래량:
  - 방법 A: `OptionMst` 주기 재조회(예: 1~3초)
  - 방법 B: 옵션 현재가 실시간 객체 병행(운영환경 검증 후)

## STEP 4. 지표 계산

### 4-1. PCR (OI 기준)

- `PCR_OI = Sum(Put_OI) / Sum(Call_OI)`
- 분모 0 보호 로직 필수

### 4-2. ATM OI

- 1안: `OptionMst(15) == 1` 종목 OI 사용
- 2안: 기초자산가와 strike 거리 최소 종목 선정(ATM 근사)
- 산출: `ATM_CALL_OI`, `ATM_PUT_OI`, `ATM_PCR_OI`

### 4-3. GEX

권장 내부 표준식(계수는 운영정의 필요):

- `UnitGEX_i = gamma_i * OI_i * contract_multiplier * spot_scale`
- `TotalGEX = Sum(Call_UnitGEX) - Sum(Put_UnitGEX)`

주의:

- 계약승수/스케일은 KRX 옵션 규격 기준으로 별도 상수화
- 장중 잠정 OI(100='1') 구간은 신뢰도 태그 부여

## STEP 5. 품질/안전 장치

- OI 구분(100) 미확정 시 레짐 판단 가중치 하향
- 만기 임박 종목(잔존일수 작음) 분리 집계
- API 지연/에러 시 직전값 carry + stale 플래그

---

## 4) 권장 데이터 모델

- `option_chain_snapshot`
  - `asof_ts, code, cp, ym, strike`
- `option_mst_snapshot`
  - `asof_ts, code, price, volume, oi, oi_prev, oi_state, delta, gamma, theta, vega, rho, vol, dte, rf_rate, atm_flag`
- `option_derived_metrics`
  - `asof_ts, ym, pcr_oi, atm_call_oi, atm_put_oi, atm_pcr_oi, total_gex, call_gex, put_gex, quality_flag`

---

## 5) 구현 순서 (실무 권장)

1. 체인 수집 + OptionMst 일괄 스냅샷부터 완성
2. PCR_OI/ATM_OI 배치 계산 검증
3. OptionMo 실시간 OI 델타 반영
4. GEX 계산식/계수 확정
5. 운영 대시보드(신뢰도 태그, 잠정/확정 구분) 연결

---

## 6) 확인한 근거 링크

### 공식/도움말

- CpOptionCode: https://cybosplus.github.io/cputil_rtf_1_/cpoptioncode.htm
- OptionMst: https://cybosplus.github.io/cpdib_rtf_1_/optionmst.htm
- OptionMo: https://cybosplus.github.io/cpdib_rtf_1_/optionmo.htm
- CpCalcOptGreeks: https://cybosplus.github.io/cputil_rtf_1_/cpcalcoptgreeks.htm

### 대신증권 QnR/도움말 커뮤니티

- QnR (미결제증감 관련): https://money2.daishin.com/e5/mboard/ptype_basic/Basic_018/DW_Basic_Read_Page.aspx?boardseq=60&seq=28662&page=1&searchString=&p=8827&v=8636&m=9508
- 도움말 (OptionMo 정의): https://money2.daishin.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=284&seq=52&page=2&searchString=%EB%AF%B8%EA%B2%B0%EC%A0%9C&p=8839&v=8642&m=9508
- QnR (FutOptChart OI 해석 이슈): https://money2.daishin.com/e5/mboard/ptype_basic/Basic_018/DW_Basic_Read_Page.aspx?boardseq=60&seq=24964&page=1&searchString=&p=8827&v=8636&m=9508

### GitHub 커뮤니티 탐색 결과 메모

- 공개 저장소에서 Cybos 기본 연동 예시는 존재하나, 옵션 체인+OI+GEX 완결 구현 예시는 드묾.
- 따라서 객체 스펙은 공식 문서(OptionMst/OptionMo/CpCalcOptGreeks)를 기준으로 직접 파이프라인 구현하는 것이 안전함.

---

## 7) 체크리스트

- [ ] CpOptionCode 체인 추출 완료
- [ ] OptionMst 필드맵 검증(93/97/99/100/109/110/115/13/36/15)
- [ ] OptionMo 실시간 OI 반영
- [ ] PCR_OI/ATM_OI 배치-실시간 일치 검증
- [ ] GEX 계약승수/스케일 정의 확정
- [ ] 잠정/확정 OI 품질 플래그 운영 반영
