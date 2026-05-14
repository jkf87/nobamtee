# Voice Capsule Schema (v0.1)

캡슐은 파일이 아니라 디렉터리다.

```
voices/{realm}/{voice-id}/
├── fingerprint.json   # 필수
├── descriptor.md      # 필수
├── exemplars.md       # default 캡슐 권장, user 캡슐 선택
└── PROVENANCE.md      # 필수
```

`realm` ∈ {`default`, `user`}.
`voice-id` 는 kebab-case (`concrete-essay-ko`, `myvoice` 등).

## `fingerprint.json`

캡슐 보이스의 정량 지표.

```json
{
  "voice_id": "concrete-essay-ko",
  "version": "0.1.0",
  "tolerance": 0.15,
  "computed_from": "PROVENANCE.md 참조",
  "metrics": {
    "sentence_count": 0,
    "char_count": 0,
    "sentence_length_mean": 0.0,
    "sentence_length_stdev": 0.0,
    "ending_da_ratio": 0.0,
    "passive_double_ratio": 0.0,
    "modal_can_ratio": 0.0,
    "passive_by_ratio": 0.0,
    "conjunction_density_per_kchar": 0.0,
    "english_loan_per_kchar": 0.0
  }
}
```

`tolerance`: 윤문 후 메트릭이 fingerprint ± tolerance 범위에 들면 수렴 판정.

새 지표는 후방 호환만 지키면 자유 추가. 엔진은 미지의 키를 무시한다.

## `descriptor.md`

≤300자. 사람이 읽고 톤을 이해할 수 있도록 산문으로 작성.

## `exemplars.md`

3–5 단락, 단락당 ≤200자. 캡슐 보이스로 새로 쓴 일반 주제 글. 출처 산문의 내용·표현·고유명사를 재현하지 않는다.

## `PROVENANCE.md`

```markdown
# {voice-id} PROVENANCE

- 추출 일자: 2026-05-14
- 추출 도구: scripts/extract_capsule.py v0.1
- 출처 메타 정보: {출처 카테고리 또는 로컬 파일명}
- descriptor 작성: {사람 / 모델+큐레이션}
- exemplars 작성: {사람} ({date}).
- 라이선스: 데이터 (json·md) CC0.
```

## 규칙

- `fingerprint.json` 의 `metrics` 는 stdlib 만으로 재계산 가능해야 한다.
- `descriptor.md` / `exemplars.md` 변경 시 PROVENANCE 에 변경 기록 추가.
