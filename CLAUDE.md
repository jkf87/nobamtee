# 노밤티 (nobamtee) — voice-capsule engine

한국어 "AI 밤티" 제거기. 엔진은 보이스 캡슐 한 축으로 환원되어 있다.

## 원리

원문에서 "AI같음" 을 한국어 보이스 캡슐 한 개와의 거리로 정의한다. 거리가 멀수록 다듬고, 다듬더라도 의미는 보존한다. 패턴 사전·카테고리·트리거 키워드 없음.

## 3대 자산

1. **엔진** — 단일 에이전트 `voice-capsule-rewriter`. 원문 + 캡슐 → 윤문본 + 충실도 diff. 도구 호출 3회 캡.
2. **캡슐** — 보이스를 운반하는 디렉터리. `fingerprint.json` + `descriptor.md` + (옵션) `exemplars.md` + `PROVENANCE.md`.
3. **충실도 계약** — token-level 명사·수치·고유명사·인용 invariant.

## 철칙

- 의미 불변. 원문 명사·수치·고유명사·직접인용은 한 글자도 변하지 않는다.
- 변경률 상한 30%. 그 너머는 경고 플래그, 50% 너머는 강제 중단·롤백.
- 캡슐에 없는 스타일은 강요하지 않는다. 캡슐이 침묵하는 차원은 원문 보존.
- raw 산문은 저장소에 남기지 않는다. 추출 후 폐기.

## 디렉터리

```
.claude/
  skills/voice-capsule/SKILL.md
  skills/voice-capsule/references/
  agents/voice-capsule-rewriter.md
voices/
  default/{voice-id}/    # ship 가능. PD 출처 또는 신규 합성.
  user/{voice-id}/       # gitignored. 로컬 전용.
scripts/
  extract_capsule.py     # raw → 캡슐. raw 폐기.
_workspace/{YYYY-MM-DD-NNN}/   # 윤문 산출. gitignored.
```

## 파일 시스템 규약

- `Read` / `Write` / `Edit` / `Glob` 만 사용. `Bash ls/cat` 금지 (셸 환경 의존성).
- 캡슐 디렉터리는 반드시 `fingerprint.json` · `descriptor.md` · `PROVENANCE.md` 를 가진다. `exemplars.md` 는 default 캡슐 권장.
- `_workspace/{YYYY-MM-DD-NNN}/` 산출물은 gitignore. 누적 보관 책임은 사용자.

## 한계 (정직 선언)

- 보이스 변환의 깊이는 캡슐 descriptor + exemplars 가 풍부할수록 깊다. 빈 캡슐은 거의 작동하지 않는다.
- 자동 검수 루프는 없다. 충실도 invariant 위반 시 그 edit 만 self-rollback. 그 이상은 사람이 새 라운드를 명령한다.
- 5,000자 초과는 분할 처리 권장 (chunk ≤ 2,000자, 동일 캡슐 재사용).
