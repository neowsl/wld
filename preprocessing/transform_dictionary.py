import argparse
import json


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("infile")
    parser.add_argument("outfile")

    args = parser.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    res = {}

    for entry in raw_data:
        base_forms = entry.get("base_forms") or []
        clean_forms = [str(f) for f in base_forms if f is not None]
        word_string = ", ".join(clean_forms) if clean_forms else "Unknown"

        definition = entry.get("definition", "No definition available")

        res[word_string] = definition

    with open(args.outfile, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4)


if __name__ == "__main__":
    main()
