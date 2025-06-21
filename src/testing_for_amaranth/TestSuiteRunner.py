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

from .TestRunner import TestRunner


class TestSuiteRunner:
    __test__ = False  # so that pytest does NOT try to collect it

    """A system to generate a suite of test benches to be formally verified by SymbiYosis (sby)"""

    def __init__(self, deviceFactory, castingFactory, stories):
        for i, story in enumerate(stories):
            if len(story.expected) == 0:
                raise ValueError(f"story.must.have.expected.participants:{i}")
        self._suite = [
            TestRunner(deviceFactory, castingFactory, story) for story in stories
        ]

    def run(self):
        for test in self._suite:
            test.run()
