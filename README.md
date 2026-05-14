# 노밤티 (nobamtee)

한국어 글의 "AI 밤티" (통계적으로 튀는 저품질 표식) 를 패턴 사전 없이 보이스 캡슐 한 개로 제거한다. 엔진 이름은 `voice-capsule`.

---

## 컨셉

AI가 쓴 한국어 글의 티는 카테고리 40+개를 외워서 잡는 게 아니다. "사람이 쓴 글" 의 좌표에서 얼마나 떨어져 있느냐의 거리로 측정된다. 거리는 한국어 문장 표면의 정량 지표로 환산된다: 문장 길이 분포, 종결어미 비율, `~할 수 있다` 빈도, 접속사 밀도, 영어 외래어 비율, post-editese 3축 등. "AI 같은가" 는 한 줄 수치가 된다.

윤문도 같은 원리로 동작한다. 원문 메트릭과 캡슐 fingerprint 의 거리를 좁히는 방향으로, 거리를 크게 만드는 구간만 다시 쓴다. 나머지 (사실·수치·고유명사·인용) 는 한 글자도 건드리지 않는다.

보이스 캡슐은 산문 자체가 아니라 세 겹의 파생 표현이다.

| 레이어 | 정체 | 분량 |
|---|---|---|
| A. `fingerprint.json` | 보이스의 정량 지표 | 10–15개 수치 |
| B. `descriptor.md` | 톤 묘사. 사람이 읽고 보이스를 가늠하는 산문 | ≤300자 |
| C. `exemplars.md` | 그 보이스로 새로 쓴 짧은 단락 3–5편 (외부 출처 미참조) | 단락당 ≤200자 |

캡슐 디렉터리에 raw 산문은 존재하지 않는다. 추출 단계에서 raw 는 소비되고, 파생 표현 3종만 디스크에 남는다.

작동을 한 줄로 적으면:

```
원문 + 보이스 캡슐 → 윤문본 + 충실도 diff + 메트릭 비교
```

---

## 작동 원리

### 파이프라인

```
1) Read  캡슐 (descriptor + fingerprint + 선택 exemplars)
2) Read  원문
3) 메모리 안에서
   ├─ 원문 메트릭 계산
   ├─ 캡슐 fingerprint 와의 거리 산출
   ├─ 거리를 크게 만드는 구간 = 윤문 후보
   ├─ 후보 구간만 캡슐 톤으로 재작성
   ├─ Do-NOT 토큰은 그대로 보존
   └─ 자체 invariant 검증 (위반 edit 1건 → 롤백 후 1회 재시도)
4) Write final.md (본문 + VC-SUMMARY 메타 블록)
```

도구 호출 총 3회 캡. 다른 에이전트 호출 없음. 자동 검수 루프 없음.

### 충실도 계약 (의미 불변)

윤문본은 다음을 token level 로 보존한다. 위반 edit 만 롤백.

- 수치·날짜·단위 (`50nM`, `2024년 5월`, `°C`, `kg`)
- 고유명사·기관명·제품명·법령명 (한자 병기 포함)
- 영어 약어·식별자 (`LLM`, `API`, `IPv6`, `K-방산`)
- 큰따옴표 직접인용. `"..."` 안쪽 한 글자도 변하지 않는다.
- 법률 조문, 수식, 코드블록
- 사용자 지정 `donot_keywords`

### 변경률 가드

| 변경률 | 처리 |
|---|---|
| ≤ 30% | 정상 |
| 30 ~ 50% | `over_polish_warning` 플래그 |
| > 50% | 강제 중단, 직전 안전 버전 (≤30%) 으로 롤백 |

변경률 = `1 - LCS(원문, 윤문본).length / max(|원문|, |윤문본|)` 의 근사.

### 캡슐 선택

장르가 맞지 않는 캡슐을 쓰면 결과물에 새로운 AI 티가 생긴다. 기술 글이 문학 톤이 되거나, 문학이 기술 톤이 되는 식이다. 캡슐은 register 와 맞춘다.

| 입력 장르 | 캡슐 |
|---|---|
| 칼럼·에세이·문학 단편 | `voices/default/concrete-essay-ko` |
| 기술 블로그·문서·API 가이드·튜토리얼 | `voices/default/plain-tech-ko` |

---

## 철칙

1. 의미 불변. 사실·수치·고유명사·직접인용은 토큰 단위로 보존.
2. 캡슐 한정. 캡슐이 침묵하는 차원은 원문 그대로.
3. 추적 가능. 모든 변경은 diff 와 메트릭 before/after 로 노출.
4. raw 비축 금지. 출처 산문은 디스크에 남기지 않는다.

---

## 사용

```bash
# 1) 새 캡슐 추출. raw 산문은 캡슐 디렉터리에 저장되지 않는다.
python3 scripts/extract_capsule.py path/to/source.md \
  --out voices/user/myvoice \
  --voice-id myvoice

# 2) 윤문. Claude Code 안에서 자연어로
"이 글, voices/default/plain-tech-ko 로 윤문해줘"
```

산출물은 `_workspace/{YYYY-MM-DD-NNN}/final.md` 에 저장된다. 본문 끝 `<!-- VC-SUMMARY -->` HTML 주석 블록에 메트릭·diff·플래그가 들어 있다. 마크다운 뷰어에는 본문만 보인다.

---

## 디렉터리

```
.
├── README.md
├── CLAUDE.md
├── LICENSE
├── .gitignore
├── .claude/
│   ├── skills/voice-capsule/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── capsule-schema.md
│   │       └── fidelity-contract.md
│   └── agents/voice-capsule-rewriter.md
├── scripts/extract_capsule.py
└── voices/
    └── default/
        ├── concrete-essay-ko/
        │   ├── fingerprint.json
        │   ├── descriptor.md
        │   ├── exemplars.md
        │   └── PROVENANCE.md
        └── plain-tech-ko/
            ├── fingerprint.json
            ├── descriptor.md
            ├── exemplars.md
            └── PROVENANCE.md
```

`_workspace/` 와 `voices/user/` 는 `.gitignore` 처리되며 저장소에 포함되지 않는다.

---

## 라이선스

MIT. 디폴트 캡슐 데이터 (`fingerprint.json`·`descriptor.md`·`exemplars.md`) 는 CC0.
