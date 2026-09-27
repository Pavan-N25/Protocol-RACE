"""Simple CLI for Protocol-RACE."""
import argparse
import json
from protocol_race.detectors import detect_prompt_injection, detect_jailbreak, detect_social_engineering
from protocol_race.redactor import redact_sensitive
from protocol_race.file_analyzer import analyze_file


def main():
    p = argparse.ArgumentParser(prog="protocol-race")
    p.add_argument("--inspect", help="Inspect a text input for attacks")
    p.add_argument("--score", action="store_true", help="Print scored detector features and score")
    p.add_argument("--file", help="Analyze a file content")
    args = p.parse_args()
    if args.inspect:
        text = args.inspect
        text = args.inspect
        d1 = detect_prompt_injection(text)
        d2 = detect_jailbreak(text)
        d3 = detect_social_engineering(text)
        redacted_text, count = redact_sensitive(text)
        out = {"detectors": [d1, d2, d3], "redacted_count": count, "redacted_text": redacted_text}
        # optionally include scored detector
        if args.score:
            try:
                from protocol_race.detectors import scored_detection

                out["scored"] = scored_detection(text)
            except Exception as e:
                out["scored_error"] = str(e)
        print(json.dumps(out, indent=2))
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            return
        res = analyze_file(content)
        print(json.dumps(res, indent=2))
    else:
        p.print_help()


if __name__ == "__main__":
    main()
