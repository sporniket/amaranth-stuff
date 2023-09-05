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
### builtin deps
import pytest
from subprocess import CalledProcessError
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.testing import Test, Story


from amaranth_boards.resources import *  # from .resources import *
from amaranth.build import Resource, Clock, Pins


class DummyModule(Elaboratable):
    def __init__(self):
        self.input = Signal()
        self.output = Signal()
        self.complement = Signal(reset=1)

    def ports(self) -> List[Signal]:
        return [self.input, self.output, self.complement]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        m.d.comb += self.complement.eq(~self.output)
        m.d.sync += self.output.eq(self.input)
        return m


def test_shouldFailMiserably():
    def testBody(m: Module, cd: ClockDomain):
        dummy = m.submodules.dut

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": cd.rst, "input": dummy.input},
            stories=[
                Story("Reset", {"rst": [1]}),
                Story("Not reset", {"rst": [0], "input": [1]}),
            ],
        )

        with m.If(tb.matchesStory("Reset")):
            m.d.sync += Assert(
                dummy.complement & dummy.output
            )  # fails because complement = not(output)
        with m.If(tb.matchesStory("Not reset")):
            m.d.sync += Assert(
                dummy.complement & dummy.output
            )  # fails because complement = not(output)

    with pytest.raises(CalledProcessError):
        Test.describe(DummyModule(), testBody)
