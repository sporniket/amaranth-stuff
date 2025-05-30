"""
---
(c) 2022,2023 David SPORN
---
This is part of Sporniket's "Amaranth Stuff" project.

Sporniket's "Amaranth Stuff" project is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Sporniket's "Amaranth Stuff" project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with Sporniket's "Amaranth Stuff" project.
If not, see <https://www.gnu.org/licenses/>. 
---
"""

### amarant-stuff deps
from amaranth_stuff.testing import Story


def test_Story_includes_all_participant_as_given_if_not_specified():
    story = Story("a title", {"a": [1, 0, 1], "b": [0, 0, 1]})

    assert story.title == "a title"
    assert story.content["a"] == [1, 0, 1]
    assert story.content["b"] == [0, 0, 1]
    assert story.given == ["a", "b"]
    assert story.expected == []


def test_Story_includes_deduces_expected_participants_from_specified_given():
    story = Story("a title", {"a": [1, 0, 1], "b": [0, 0, 1]}, given=["a"])

    assert story.title == "a title"
    assert story.content["a"] == [1, 0, 1]
    assert story.content["b"] == [0, 0, 1]
    assert story.given == ["a"]
    assert story.expected == ["b"]

    story = Story("a title", {"a": [1, 0, 1], "b": [0, 0, 1]}, given=["b"])

    assert story.title == "a title"
    assert story.content["a"] == [1, 0, 1]
    assert story.content["b"] == [0, 0, 1]
    assert story.given == ["b"]
    assert story.expected == ["a"]


def test_Story_ignores_given_participants_not_in_content():
    story = Story("a title", {"a": [1, 0, 1], "b": [0, 0, 1]}, given=["d", "a", "c"])

    assert story.title == "a title"
    assert story.content["a"] == [1, 0, 1]
    assert story.content["b"] == [0, 0, 1]
    assert story.given == ["a"]
    assert story.expected == ["b"]
