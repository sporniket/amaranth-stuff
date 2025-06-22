"""
---
(c) 2022~2025 David SPORN
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


class Story:
    """A Story represents a set of sequences of values for each participants.

    Each sequence is described from the oldest to the latest value. When the length of sequences are
    not the same, the longest sequences are starting before to end simultaneously.
    """

    def __init__(self, title: str, content, *, given=None):
        """Fully define a story

        * title : string, a distinctive title
        * content : a list of values by _participant_ name, e.g. {"a":[1,0,1], "b":[0,1,1]}
        * given : OPTIONNAL, the list of participants whose content is _given_ ; content of other participants are _expected_ ;
            when not specified, all participants are considered given.
        """
        self.title = title
        self.content = content
        if given is not None:
            self.given = []
            for p in given:
                if p in content:
                    self.given.append(p)
        else:
            self.given = [p for p in content]
        self.expected = []
        for p in content:
            if p not in self.given:
                self.expected.append(p)
