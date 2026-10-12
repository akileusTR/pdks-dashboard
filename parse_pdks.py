import re
import json

with open(
    "data/raw.txt",
    "r",
    encoding="utf-8"
) as f:
    text = f.read()

lines = [
    x.strip()
    for x in text.splitlines()
    if x.strip()
]

days = []

for i in range(len(lines)):

    if re.match(
        r"\d{2}\.\d{2}\.\d{4}",
        lines[i]
    ):

        try:

            date = lines[i]

            name = lines[i + 1]

            target = int(lines[i + 2])

            inside = int(lines[i + 3])

            days.append(
                {
                    "date": date,
                    "name": name,
                    "target": target,
                    "inside": inside,
                    "difference": inside - target
                }
            )

        except:
            pass

result = {
    "days": days
}

with open(
    "data/latest.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    )
)
