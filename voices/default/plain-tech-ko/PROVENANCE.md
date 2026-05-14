# plain-tech-ko PROVENANCE

- 유형: 디폴트 프리셋 (저장소 동봉, 배포 가능)
- register: 한국어 기술 블로그·문서·튜토리얼.
- 목적: 문학 register `concrete-essay-ko` 와 짝을 이뤄 장르별 프리셋 분리 원칙을 구현. 같은 엔진이 장르 한 축만 갈아끼우면 동작.
- `fingerprint.json`: 본 register 의 목표 지표값. 손으로 추정한 합의값. 관용 기술어 화이트리스트와 창작 비유 블랙리스트를 동봉.
- `descriptor.md`: 본 저장소 직접 작성. 입말 톤·외래어 허용·창작 비유 금지를 명시.
- `exemplars.md`: 본 저장소 직접 작성. 일반 데브옵스 주제 4편.
- 라이선스:
  - `fingerprint.json`: 사실 데이터·합의값, CC0.
  - `descriptor.md`·`exemplars.md`: 본 저장소 원저작물, CC0.

## 프리셋 선택 가이드

| 입력 장르 | 프리셋 |
|---|---|
| 칼럼·에세이·문학 단편 | `concrete-essay-ko` |
| 기술 블로그·문서·API 가이드·튜토리얼 | `plain-tech-ko` |
| 공공보고서·논문초록·법률 문서 | (미정 — 향후 `formal-report-ko` 후보) |

프리셋을 잘못 고르면 결과물에 "장르 미스매치 AI 티" 가 발생한다.
