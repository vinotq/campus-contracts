import pytest

from campus_contracts.audience import audience_label, audience_matches
from campus_contracts.envelope import Audience


@pytest.mark.parametrize("factory", [dict, Audience])
def test_targeting_is_a_union_of_buildings_courses_and_groups(factory):
    audience = factory(buildings=["3"], courses=[2], groups=["СПО-7"])
    assert audience_matches(audience, building="3", course=1, group="ВО-1")
    assert audience_matches(audience, building="8", course=2, group="ВО-1")
    assert audience_matches(audience, building="8", course=1, group="СПО-7")
    assert not audience_matches(audience, building="8", course=1, group="ВО-1")
    assert not audience_matches(audience)


@pytest.mark.parametrize("audience", [{}, Audience(), {"buildings": [], "groups": [], "courses": []}])
def test_untargeted_publication_reaches_people_without_profile_fields(audience):
    assert audience_matches(audience)


def test_labels_are_the_same_for_reordered_and_duplicated_targets():
    assert audience_label(["10", "2", "2"], ["Б", "А", "А"], [3, 1, 3]) == (
        "корпуса 2, 10, курсы 1, 3, группы: 2"
    )
    assert audience_label(["2", "10"], ["А", "Б"], [1, 3]) == (
        "корпуса 2, 10, курсы 1, 3, группы: 2"
    )
    assert audience_label() == "все"
    assert audience_label(["Гамма"], ["СПО-7"], [2]) == "корпус Гамма, курс 2, группа СПО-7"
