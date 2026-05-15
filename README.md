# 노밤티 (nobamtee)

노밤티는 밤티같은 AI티가 나는 글을 수정해주는 도구입니다. 한국어 글의 AI 티를 패턴 사전 없이 문체 프리셋 한 개로 제거합니다. 엔진은 `voice-capsule` 입니다.

---

## 컨셉

**인공지능이 자주 사용하는 말투를 찾아 사람이 쓴 글과 비교하여 변경합니다.**

작동:

```
원문 + 문체 프리셋 → 윤문본 + 충실도 diff + 메트릭 비교
```

---

## 문체 프리셋

말투·리듬·문체를 세 파일로 운반하는 디렉터리입니다.

| 레이어 | 역할 |
|---|---|
| `fingerprint.json` | 정량 지표 — 어디를 다시 쓸지 |
| `descriptor.md` | 톤 묘사 — 어떤 톤으로 쓸지 |
| `exemplars.md` | 단락 예시 — 리듬·호흡 시연 |

---

## 작동 원리

```
1) Read 프리셋 (descriptor + fingerprint + 선택 exemplars)
2) Read 원문
3) 메모리 안에서
   ├─ 원문 메트릭 계산
   ├─ 프리셋 fingerprint 와의 거리 산출
   ├─ 거리를 키우는 구간 = 윤문 후보
   ├─ 후보 구간만 프리셋 톤으로 재작성
   ├─ Do-NOT 토큰 (수치·고유명사·인용·약어) 은 그대로 보존
   └─ 자체 invariant 검증 (위반 edit 1건 → 롤백 후 1회 재시도)
4) Write final.md
```

도구 호출 3회 캡. 다른 에이전트 호출은 없습니다.

> **invariant 란?**
> "어떤 작업을 하든 절대 변하면 안 되는 것" 을 뜻하는 프로그래밍 용어입니다. 본 엔진의 invariant 는 **원문의 보존 대상 토큰** (수치·날짜·고유명사·인용·영어 약어 등) 이 윤문본에도 그대로 남아 있어야 한다는 규칙입니다. 윤문 한 edit 이 이 규칙을 깨면 — 예를 들어 "50nM" 을 빠뜨리거나 인용문 안쪽을 바꾸면 — 그 edit 만 롤백하고 1회 다시 시도합니다. 재시도 후에도 위반이면 그 구간은 원문 그대로 두고 `VC-SUMMARY` 의 `flags` 에 기록됩니다.

### 변경률 가드

| 변경률 | 처리 |
|---|---|
| ≤ 30% | 정상 |
| 30 ~ 50% | `over_polish_warning` 플래그 |
| > 50% | 강제 중단, 안전 버전 (≤30%) 으로 롤백 |

---

## 프리셋 선택

장르에 맞는 프리셋을 지원합니다.

| 입력 장르 | 프리셋 |
|---|---|
| 칼럼·에세이·문학 단편 | `voices/default/concrete-essay-ko` |
| 기술 블로그·문서·튜토리얼 | `voices/default/plain-tech-ko` |

---

## 사용

```bash
# 새 프리셋 추출
python3 scripts/extract_capsule.py path/to/source.md \
  --out voices/user/myvoice --voice-id myvoice

# 윤문 (Claude Code 안에서 자연어로)
"이 글, voices/default/plain-tech-ko 프리셋으로 윤문해줘"
```

산출물은 `_workspace/{YYYY-MM-DD-NNN}/final.md` 에 저장됩니다. 본문 끝 `<!-- VC-SUMMARY -->` 주석 블록에 메트릭·diff 가 들어 있습니다.

---

## 라이선스

Apache-2.0. 디폴트 프리셋 데이터 (`voices/default/*/`) 는 CC0 도 추가 허용.
