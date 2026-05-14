# 노밤티 (nobamtee)

한국어 "AI 밤티" 제거기. 문체 프리셋 한 축으로 동작.

## 원리

원문 메트릭과 프리셋 fingerprint 의 거리를 좁히는 방향으로, 거리를 키우는 구간만 다시 쓴다. 사실·수치·고유명사·인용은 토큰 단위로 보존. 패턴 사전·카테고리·트리거 키워드 없음.

## 철칙

- 의미 불변. 원문 명사·수치·고유명사·직접인용은 한 글자도 변하지 않는다.
- 변경률 상한 30%. 그 너머 경고, 50% 너머 강제 중단·롤백.
- 프리셋이 침묵하는 차원은 원문 그대로.

## 디렉터리

```
.claude/skills/voice-capsule/    # 스킬 본체 + references
.claude/agents/voice-capsule-rewriter.md
voices/default/{voice-id}/       # ship 가능
voices/user/{voice-id}/          # gitignored
scripts/extract_capsule.py
_workspace/{YYYY-MM-DD-NNN}/     # gitignored
```

## 파일 시스템 규약

- `Read` / `Write` / `Edit` / `Glob` 만 사용. `Bash ls/cat` 금지.
- 프리셋 디렉터리는 `fingerprint.json` · `descriptor.md` · `PROVENANCE.md` 필수.
- 프리셋 정의는 [`SKILL.md`](.claude/skills/voice-capsule/SKILL.md) 참조.

## 한계

- 문체 변환 깊이는 프리셋 descriptor + exemplars 의 풍부함을 따른다.
- 자동 검수 루프 없음. invariant 위반 edit 1건은 self-rollback, 그 이상은 사람.
- 5,000자 초과는 분할 처리 권장.
