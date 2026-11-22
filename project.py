"""Check which shots a production can actually cut with the logged footage."""

import math


def items(data, key, *, allow_empty=False):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 500:
        raise ValueError(f"{key} must be a list of up to 500 entries")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Every entry in {key} must be an object")
    return value


def number(value, field, *, positive=False):
    if type(value) not in (int, float) or not 0 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite nonnegative number at most 1e12")
    if positive and value == 0:
        raise ValueError(f"{field} must be greater than zero")
    return value


def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


TITLE = "Cutroom Coverage"
DESCRIPTION = "Match a shot list against tagged footage to find the pickups your edit still needs."
PROMPT = "Build a short pickup list from the evidence. Separate missing setups from shots that only need a longer take. Quote shot names and time deficits. Do not infer what an untagged clip shows."


def tags(value):
    if not isinstance(value, list) or not value:
        raise ValueError("tags must be a nonempty list of strings")
    return {label(tag, "tag").casefold() for tag in value}


def analyze(data: dict) -> dict:
    footage = {}
    for shot in items(data, "footage", allow_empty=True):
        name = label(shot.get("id"), "footage id")
        start = number(shot.get("in"), "in")
        end = number(shot.get("out"), "out")
        if end <= start or name in footage:
            raise ValueError("Each footage ID must be unique and out must follow in")
        footage[name] = (tags(shot.get("tags")), end - start)

    rows = []
    seen = set()
    for need in items(data, "shot_list"):
        name = label(need.get("shot"), "shot")
        if name in seen:
            raise ValueError("Shot list names must be unique")
        seen.add(name)
        required = tags(need.get("tags"))
        seconds = number(need.get("seconds"), "seconds", positive=True)
        matches = [(length, clip) for clip, (logged, length) in footage.items() if required <= logged]
        best, clip = min(matches, key=lambda match: (-match[0], match[1])) if matches else (0, "—")
        missing = 0 if math.isclose(seconds, best, rel_tol=1e-14, abs_tol=0) else max(0, seconds - best)
        state = "Covered" if missing == 0 else ("Too short" if matches else "Missing")
        rows.append({"Planned shot": name, "Status": state, "Best clip": clip,
                     "Usable seconds": round(best, 3), "Seconds short": round(missing, 3)})
    covered = sum(row["Status"] == "Covered" for row in rows)
    return {"summary": f"{covered} of {len(rows)} planned shots have a continuous usable take long enough.",
            "metrics": {"Planned shots": len(rows), "Covered": covered,
                        "Need a pickup": len(rows) - covered}, "rows": rows}
