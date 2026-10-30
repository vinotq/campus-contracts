from collections.abc import Mapping, Sequence

from campus_contracts.envelope import Audience


def audience_matches(
    audience: Audience | Mapping,
    *,
    building: str | None = None,
    course: int | None = None,
    group: str | None = None,
) -> bool:
    if isinstance(audience, Audience):
        buildings, courses, groups = audience.buildings, audience.courses, audience.groups
    else:
        buildings = audience.get("buildings") or ()
        courses = audience.get("courses") or ()
        groups = audience.get("groups") or ()
    return (
        not (buildings or courses or groups)
        or (building is not None and building in buildings)
        or (course is not None and course in courses)
        or (group is not None and group in groups)
    )


def audience_label(
    buildings: Sequence[str] = (),
    groups: Sequence[str] = (),
    courses: Sequence[int] = (),
) -> str:
    parts = []
    ordered_buildings = sorted(
        set(buildings), key=lambda value: (int(value), "") if value.isdigit() else (10**9, value)
    )
    if ordered_buildings:
        prefix = "корпус" if len(ordered_buildings) == 1 else "корпуса"
        parts.append(f"{prefix} {', '.join(ordered_buildings)}")
    if courses:
        ordered_courses = sorted(set(courses))
        prefix = "курс" if len(ordered_courses) == 1 else "курсы"
        parts.append(f"{prefix} {', '.join(str(value) for value in ordered_courses)}")
    if groups:
        ordered_groups = sorted(set(groups))
        parts.append(
            f"группа {ordered_groups[0]}" if len(ordered_groups) == 1 else f"группы: {len(ordered_groups)}"
        )
    return ", ".join(parts) or "все"
