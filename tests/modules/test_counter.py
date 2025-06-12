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
from amaranth_stuff.modules import RippleCounter, SlowRippleCounter
from amaranth_stuff.testing import TestRunner, Story, TestSuiteRunner

###
### Test suite on RippleCounter
###


def test_RippleCounter():
    TestSuiteRunner(
        lambda: RippleCounter(3),
        lambda dut, clockDomain: {"rst": clockDomain.rst, "value": dut.value},
        [
            Story(
                "One full cycle",
                {
                    "rst": [1, 0, 0, 0] + [0, 0, 0, 0] + [0, 0],
                    "value": [0, 1, 2, 3] + [4, 5, 6, 7] + [0, 1],
                },
                given=["rst"],
            ),
            Story(
                "When reset stays high",
                {"rst": [1, 1], "value": [0, 0]},
                given=["rst"],
            ),
        ],
    ).run()


###
### Test suite on SlowRippleCounter
###


def test_SlowRippleCounter_shouldIncrementValueAtEachBeatLeadingEdge():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value, "beat": counter.beat},
            stories=[
                Story(
                    f"Beat after value has reached {i}",
                    {"rst": [0], "value": [i], "beat": [0, 1]},
                )
                for i in range(0, maxValue)
            ],
        )
        for i in range(0, maxValue):
            with m.If(tb.matchesStory(f"Beat after value has reached {i}")):
                m.d.sync += Assert(counter.value == (i + 1))

    TestRunner.perform(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldReturnToZeroAfterReachingMaxValueSupportedByTheWidth():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value, "beat": counter.beat},
            stories=[
                Story(
                    "Beat after value has reached maxValue",
                    {"rst": [0], "value": [maxValue], "beat": [0, 1]},
                )
            ],
        )
        with m.If(tb.matchesStory("Beat after value has reached maxValue")):
            m.d.sync += Assert(counter.value == 0)

    TestRunner.perform(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldKeepValueAtEachBeatTrailingEdge():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value, "beat": counter.beat},
            stories=[
                Story(
                    f"Beat falling after value has reached {i}",
                    {"rst": [0], "value": [i], "beat": [1, 0]},
                )
                for i in range(0, maxRange)
            ],
        )
        for i in range(0, maxRange):
            with m.If(tb.matchesStory(f"Beat falling after value has reached {i}")):
                m.d.sync += Assert(counter.value == i)

    TestRunner.perform(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldKeepValueWhenBeatDoesNotChange():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value, "beat": counter.beat},
            stories=[
                Story(
                    f"Beat stay negated after value has reached {i}",
                    {"rst": [0, 0], "value": [i], "beat": [0, 0]},
                )
                for i in range(0, maxRange)
            ]
            + [
                Story(
                    f"Beat stay asserted after value has reached {i}",
                    {"rst": [0, 0], "value": [i], "beat": [1, 1]},
                )
                for i in range(0, maxRange)
            ],
        )
        for i in range(0, maxRange):
            with m.If(
                tb.matchesStory(f"Beat stay negated after value has reached {i}")
            ):
                m.d.sync += Assert(counter.value == i)
            with m.If(
                tb.matchesStory(f"Beat stay asserted after value has reached {i}")
            ):
                m.d.sync += Assert(counter.value == i)

    TestRunner.perform(SlowRippleCounter(3), testBody)
