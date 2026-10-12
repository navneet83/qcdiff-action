"""Run qcdiff for the GitHub Action: print the diff, mirror it into the job
step summary, set the `changed` output, and exit 0/1/2 like the CLI."""

import argparse
import os
import sys

import qcdiff


def set_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{name}={value}\n")


def step_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("--quiet", default="false")
    args = parser.parse_args()
    quiet = args.quiet.lower() == "true"

    try:
        report = qcdiff.diff_files(args.old, args.new)
    except (qcdiff.QasmError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        step_summary(f"### qcdiff\n\n:x: error: {e}\n")
        return 2

    text = str(report)
    if quiet:
        text = "\n".join(text.splitlines()[:2]) + "\n"
    print(f"--- {args.old}")
    print(f"+++ {args.new}")
    print(text, end="")

    set_output("changed", "true" if report.has_changes() else "false")

    if report.has_changes():
        step_summary(
            f"### qcdiff: circuit drift\n\n`{args.old}` vs `{args.new}`\n\n"
            f"```text\n{text}```\n"
        )
        return 1
    step_summary(f"### qcdiff\n\n:white_check_mark: `{args.new}` matches `{args.old}`.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
