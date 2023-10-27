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
from amaranth import ClockDomain, Module

### amaranth -- test deps
from amaranth.asserts import Assert

### amarant-stuff deps
from amaranth_stuff.modules import Sequencer
from amaranth_stuff.testing import Test, Story

###
### Test suite on Sequencer
###


def test_Sequencer_should_work_as_expected():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        sequencer = m.submodules.dut
        tb = m.submodules.testBench

        tb.givenStoryBook(
            participants={"rst": rst, "steps": sequencer.steps},
            stories=[
                Story(
                    "when reaching end of step 0",
                    {"steps": [1, 1]},
                ),
                Story(
                    "when reaching end of step 1",
                    {"steps": [2, 2, 2]},
                ),
                Story(
                    "when reaching end of step 2",
                    {"steps": [4, 4, 4, 4]},
                ),
                Story(
                    "when reaching end of step 3",
                    {"steps": [8]},
                ),
            ],
        )

        with m.If(tb.matchesStory("when reaching end of step 0")):
            m.d.sync += Assert(sequencer.steps == 2)
        with m.If(tb.matchesStory("when reaching end of step 1")):
            m.d.sync += Assert(sequencer.steps == 4)
        with m.If(tb.matchesStory("when reaching end of step 2")):
            m.d.sync += Assert(sequencer.steps == 8)
        with m.If(tb.matchesStory("when reaching end of step 3")):
            m.d.sync += Assert(sequencer.steps == 1)

    Test.perform(Sequencer([2, 3, 4, 1]), testBody)
