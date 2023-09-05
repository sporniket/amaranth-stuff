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
### amaranth -- main deps
from amaranth import *

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.modules import Decoder
from amaranth_stuff.testing import Test, Story


def test_shouldAssertTheCorrectBitWhenInputIsInRange():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        decoder = m.submodules.dut
        span = decoder.span

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "input": decoder.input},
            stories=[
                Story(f"When input is {i}", {"rst": [0], "input": [i]})
                for i in range(0, span)
            ],
        )
        for i in range(0, span):
            with m.If(tb.matchesStory(f"When input is {i}")):
                m.d.sync += [
                    Assert(decoder.output == (1 << i)),
                    Assert(~(decoder.outOfRange)),
                ]

    Test.perform(
        Decoder(
            (1 << 2) - 1
        ),  # there is 1 invalid input for testing the error signal of decoder
        testBody,
    )


def test_shouldAssertTheErrorBitWhenInputIsOutOfRange():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        decoder = m.submodules.dut
        span = decoder.span

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "input": decoder.input},
            stories=[
                Story("When input is out of range", {"rst": [0], "input": [span]})
            ],
        )
        with m.If(tb.matchesStory("When input is out of range")):
            m.d.sync += [Assert(decoder.output == 0), Assert(decoder.outOfRange)]

    Test.perform(
        Decoder(
            (1 << 2) - 1
        ),  # there is 1 invalid input for testing the error signal of decoder
        testBody,
    )
