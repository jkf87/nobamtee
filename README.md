# 노밤티 (nobamtee)

한국어 글의 "AI 밤티" 를 패턴 사전 없이 보이스 캡슐 한 개로 제거한다. 엔진은 `voice-capsule`.

---

## 컨셉

AI가 쓴 한국어 글의 티는 카테고리 40+개를 외워서 잡는 게 아니다. "사람이 쓴 글" 의 좌표에서 떨어진 거리로 측정된다. 거리는 문장 길이 분포, 종결어미 비율, `~할 수 있다` 빈도, 접속사 밀도, 영어 외래어 비율 같은 한국어 표면 지표로 환산된다.

윤문도 같은 원리로 동작한다. 캡슐 fingerprint 와의 거리를 좁히는 방향으로, 거리를 키우는 구간만 다시 쓴다. 사실·수치·고유명사·인용은 토큰 단위로 보존된다.

보이스 캡슐은 산문 자체가 아니라 세 겹의 파생 표현이다.

| 레이어 | 정체 | 분량 |
|---|---|---|
| `fingerprint.json` | 보이스의 정량 지표 | 10–15개 수치 |
| `descriptor.md` | 톤 묘사 | ≤300자 |
| `exemplars.md` | 그 보이스로 쓴 짧은 단락 3–5편 | 단락당 ≤200자 |

작동:

```
원문 + 보이스 캡슐 → 윤문본 + 충실도 diff + 메트릭 비교
```

---

## 작동 원리

```
1) Read 캡슐 (descriptor + fingerprint + 선택 exemplars)
2) Read 원문
3) 메모리 안에서
   ├─ 원문 메트릭 계산
   ├─ 캡슐 fingerprint 와의 거리 산출
   ├─ 거리를 키우는 구간 = 윤문 후보
   ├─ 후보 구간만 캡슐 톤으로 재작성
   ├─ Do-NOT 토큰 (수치·고유명사·인용·약어) 은 그대로 보존
   └─ 자체 invariant 검증 (위반 edit 1건 → 롤백 후 1회 재시도)
4) Write final.md
```

도구 호출 3회 캡. 다른 에이전트 호출 없음.

### 변경률 가드

| 변경률 | 처리 |
|---|---|
| ≤ 30% | 정상 |
| 30 ~ 50% | `over_polish_warning` 플래그 |
| > 50% | 강제 중단, 안전 버전 (≤30%) 으로 롤백 |

---

## 캡슐 선택

장르가 맞지 않는 캡슐을 쓰면 결과물에 새로운 AI 티가 생긴다. 기술 글이 문학 톤이 되거나 그 반대. 캡슐은 register 와 맞춘다.

| 입력 장르 | 캡슐 |
|---|---|
| 칼럼·에세이·문학 단편 | `voices/default/concrete-essay-ko` |
| 기술 블로그·문서·튜토리얼 | `voices/default/plain-tech-ko` |

---

## 사용

```bash
# 새 캡슐 추출
python3 scripts/extract_capsule.py path/to/source.md \
  --out voices/user/myvoice --voice-id myvoice

# 윤문 (Claude Code 안에서 자연어로)
"이 글, voices/default/plain-tech-ko 로 윤문해줘"
```

산출물은 `_workspace/{YYYY-MM-DD-NNN}/final.md`. 본문 끝 `<!-- VC-SUMMARY -->` 주석 블록에 메트릭·diff 가 들어 있다.

---

## 라이선스

MIT. 디폴트 캡슐 데이터는 CC0.
