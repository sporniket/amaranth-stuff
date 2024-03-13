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
from os.path import exists
from pathlib import Path
import pytest
from subprocess import CalledProcessError
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth import ClockDomain, Elaboratable, Module, Signal
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.asserts import Assert

### amarant-stuff deps
from amaranth_stuff.testing import Test, Story
from amaranth_stuff.modules import Sequencer, RippleCounter


# from .resources import *
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


def test_perform_shouldFailMiserably():
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
        Test.perform(DummyModule(), testBody)

    assert exists(Path("build-tests/test_perform_shouldFailMiserably.il"))
    assert exists(Path("build-tests/test_perform_shouldFailMiserably.sby"))


def test_perform_should_combine_test_name_and_provided_description():
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
        Test.perform(DummyModule(), testBody, description="foo")

    assert exists(
        Path(
            "build-tests/test_perform_should_combine_test_name_and_provided_description__foo.il"
        )
    )
    assert exists(
        Path(
            "build-tests/test_perform_should_combine_test_name_and_provided_description__foo.sby"
        )
    )


def test_perform_should_fail_flawed_long_test():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        sequencer = m.submodules.dut
        tb = m.submodules.testBench

        tb.givenStoryBook(
            participants={"rst": rst, "steps": sequencer.steps},
            stories=[
                Story(
                    "when reaching end of step 0",
                    {
                        "steps": [
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                            1,
                        ]
                    },
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
            m.d.sync += Assert(sequencer.steps == 4)

    with pytest.raises(CalledProcessError):
        Test.perform(Sequencer([18, 3, 4, 1]), testBody)


def test_perform_should_provide_a_correct_reset_signal():
    stories = [
        Story(
            "After value has reached 0",
            {"rst": [0], "value": [0]},
        ),
    ]

    def verifyStory(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value},
            stories=stories,
        )

        with m.If(tb.matchesStory("After value has reached 0")):
            m.d.sync += Assert(counter.value == 0)  # MUST fail

    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value},
            stories=stories,
        )

        with m.If(tb.matchesStory("After value has reached 0")):
            m.d.sync += Assert(counter.value == 1)  # MUST pass

    with pytest.raises(CalledProcessError):
        Test.perform(RippleCounter(3), verifyStory, description="verify story")

    Test.perform(RippleCounter(3), testBody, description="verify behaviour")
