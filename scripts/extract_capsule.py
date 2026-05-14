#!/usr/bin/env python3
"""voice-capsule — raw 텍스트에서 보이스 캡슐 (fingerprint + PROVENANCE 스텁) 추출.

raw 산문은 캡슐 디렉터리에 절대 복사하지 않는다.
descriptor.md / exemplars.md 는 사람이 별도 작성한다 (스크립트는 빈 스텁만 만들어 둠).

Usage:
  python scripts/extract_capsule.py path/to/source.md \\
      --out voices/user/myvoice \\
      --voice-id myvoice

Outputs (in --out):
  fingerprint.json      필수 (자동 계산)
  PROVENANCE.md         필수 (자동 작성)
  descriptor.md         TODO 스텁 (사람이 ≤300자 작성)

Hard rules:
  - stdlib only
  - raw 텍스트는 한 번 읽고 폐기. 캡슐 디렉터리에 raw 파일을 만들지 않는다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ENDING_DA = re.compile(r"다$")
PASSIVE_DOUBLE = re.compile(r"되어(진다|졌다|진|졌|지는|지)")
MODAL_CAN = re.compile(r"수\s+있(다|는|음|었다|을|던)")
PASSIVE_BY = re.compile(r"에\s+의해")
CONJUNCTIONS = re.compile(
    r"(그러나|그리고|또한|따라서|결국|결과적으로|즉|한편|반면|그러므로|그래서)"
)
ENGLISH_LOAN = re.compile(r"[A-Za-z]{2,}")
SENT_SPLIT = re.compile(r"[\.!?]+\s+|[\n\r]+")


def split_sentences(text: str) -> list[str]:
    raw = SENT_SPLIT.split(text)
    return [s.strip() for s in raw if len(s.strip()) > 1]


def compute_fingerprint(text: str) -> dict | None:
    sents = split_sentences(text)
    if not sents:
        return None
    lens = [len(s) for s in sents]
    mean = sum(lens) / len(lens)
    var = sum((l - mean) ** 2 for l in lens) / max(len(lens), 1)
    stdev = var ** 0.5
    da_count = sum(1 for s in sents if ENDING_DA.search(s))
    char_count = sum(lens) or 1
    n = max(len(sents), 1)
    return {
        "sentence_count": len(sents),
        "char_count": char_count,
        "sentence_length_mean": round(mean, 2),
        "sentence_length_stdev": round(stdev, 2),
        "ending_da_ratio": round(da_count / n, 4),
        "passive_double_ratio": round(len(PASSIVE_DOUBLE.findall(text)) / n, 4),
        "modal_can_ratio": round(len(MODAL_CAN.findall(text)) / n, 4),
        "passive_by_ratio": round(len(PASSIVE_BY.findall(text)) / n, 4),
        "conjunction_density_per_kchar": round(
            len(CONJUNCTIONS.findall(text)) / char_count * 1000, 3
        ),
        "english_loan_per_kchar": round(
            len(ENGLISH_LOAN.findall(text)) / char_count * 1000, 3
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="raw 텍스트에서 voice 캡슐을 추출. raw 산문은 보관하지 않는다."
    )
    ap.add_argument("source", help="원본 텍스트 (.md/.txt)")
    ap.add_argument("--out", required=True, help="캡슐 출력 디렉터리")
    ap.add_argument("--voice-id", required=True, help="kebab-case 식별자")
    args = ap.parse_args()

    src = Path(args.source).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    text = src.read_text(encoding="utf-8")
    fp = compute_fingerprint(text)
    if fp is None:
        print("error: 빈 입력", file=sys.stderr)
        return 1

    payload = {
        "voice_id": args.voice_id,
        "version": "0.1.0",
        "tolerance": 0.15,
        "computed_from": "PROVENANCE.md 참조",
        "metrics": fp,
    }
    (out / "fingerprint.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    prov = (
        f"# {args.voice_id} PROVENANCE\n\n"
        f"- 추출 일자: {date.today().isoformat()}\n"
        f"- 추출 도구: scripts/extract_capsule.py v0.1\n"
        f"- 출처 파일명 (메타만): `{src.name}`\n"
        f"- raw 산문 보관 여부: **아니오** — 본 디렉터리에 raw 텍스트가 존재하지 않는다.\n"
        f"- descriptor.md / exemplars.md: 사람 또는 큐레이터가 별도 작성. 본 스크립트는 작성하지 않는다.\n"
        f"- 라이선스: fingerprint.json 은 사실 데이터 (CC0). 출처 산문의 저작권은 본 캡슐과 무관.\n"
    )
    (out / "PROVENANCE.md").write_text(prov, encoding="utf-8")

    if not (out / "descriptor.md").exists():
        (out / "descriptor.md").write_text(
            "<!-- TODO: ≤300자 톤 묘사. fingerprint.json 의 수치를 참고하되 그대로 옮기지는 말 것. -->\n",
            encoding="utf-8",
        )

    print(f"capsule written: {out}")
    print(f"  voice_id: {args.voice_id}")
    print(
        f"  sentences: {fp['sentence_count']}, chars: {fp['char_count']}, "
        f"mean len: {fp['sentence_length_mean']}, ~다 ratio: {fp['ending_da_ratio']}"
    )
    print(
        f"  modal_can: {fp['modal_can_ratio']}, passive_double: {fp['passive_double_ratio']}, "
        f"passive_by: {fp['passive_by_ratio']}"
    )
    print(f"  raw 보관: 아니오")
    return 0


if __name__ == "__main__":
    sys.exit(main())
