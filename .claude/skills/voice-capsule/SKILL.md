---
name: voice-capsule
version: "0.1.0"
description: 원문과 한국어 보이스 캡슐을 받아, 캡슐 보이스에 가깝게 원문을 다시 쓰되 사실·수치·고유명사·직접인용은 토큰 단위로 보존한다. 캡슐 인자가 명시될 때 발동된다.
---

# voice-capsule (v0.1)

## 입력

- `source_path`: 윤문 대상 한국어 텍스트 (.md/.txt).
- `capsule_path`: `voices/{default|user}/{voice-id}/` 디렉터리. `fingerprint.json` + `descriptor.md` 필수, `exemplars.md` 권장.
- `donot_keywords`: (옵션) 토큰 단위 추가 보존 목록.

## 출력

`_workspace/{YYYY-MM-DD-NNN}/final.md`. 윤문본 본문 + 끝부분 `<!-- VC-SUMMARY -->` 주석 블록에 메트릭·diff·플래그.

## 절차 (3 콜 캡)

1. Read 캡슐 — `descriptor.md` + `fingerprint.json` + (있으면) `exemplars.md`.
2. Read 원문.
3. 메모리 안에서:
   - 원문 메트릭을 fingerprint 와 같은 축으로 계산.
   - 거리 d(원문, 캡슐) = 축별 정규 차이의 가중합.
   - 거리를 키우는 구간 = 윤문 후보. 후보 외 구간은 건드리지 않는다.
   - Do-NOT 토큰 (수치·고유명사·인용·영어 약어·`donot_keywords`) 은 보존. 후보 안에 끼어 있으면 그 토큰만 보호하고 주변만 다시 쓴다.
   - 재작성은 descriptor 톤 묘사를 따른다. exemplars 가 있으면 리듬 참조.
   - 캡슐이 침묵하는 차원은 원문 그대로.
   - 변경률 30% 초과 → 경고 플래그. 50% 초과 → 안전 버전 (≤30%) 으로 롤백.
4. Write `final.md`.

## VC-SUMMARY 블록

```
<!-- VC-SUMMARY v0.1
run_id: 2026-05-14-001
capsule: voices/default/concrete-essay-ko
metrics:
  char_in: 1820
  char_out: 1612
  change_rate: 14.8%
distance:
  before: 0.62
  after: 0.21
  capsule_tolerance: 0.15
fidelity:
  preserved_tokens: 100%
  rolled_back_edits: 0
  donot_hits: ["LLM", "2024년", "KAERI"]
flags: []
-->
```

HTML 주석이라 마크다운 뷰어에는 본문만 보인다. 메타는 `grep VC-SUMMARY` 로 추출.

## 호출 형태

자연어 트리거 키워드 사전 없음. 캡슐 인자가 명시되면 발동, 아니면 발동하지 않는다.

- 슬래시 커맨드: `/voice-capsule <원문> --capsule <캡슐경로>`
- 자연어: "이 글, `voices/default/concrete-essay-ko` 로 윤문해줘"

## 한계

- 캡슐이 침묵하는 차원은 원문 보존 (캡슐에 "유머 톤" 묘사 없으면 유머는 안 살린다).
- 자동 검수 루프 없음. invariant 위반 edit 1건은 self-rollback, 그 이상은 사람 호출.
- 5,000자 초과는 분할 처리 권장.

## 참고

- 캡슐 형식: [`references/capsule-schema.md`](references/capsule-schema.md)
- 충실도 계약: [`references/fidelity-contract.md`](references/fidelity-contract.md)
