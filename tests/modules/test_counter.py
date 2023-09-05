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
from amaranth_stuff.modules import RippleCounter, SlowRippleCounter
from amaranth_stuff.testing import Test, Story

###
### Test suite on RippleCounter
###


def test_RippleCounter_shouldIncrementValueAtEachClock():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value},
            stories=[
                Story("After reset has been negated", {"rst": [1, 0]}),
                Story(
                    "After value has reached 0",
                    {"rst": [0, 0], "value": [maxValue, 0]},
                ),
            ]
            + [
                Story(
                    f"After value has reached {i}",
                    {"rst": [0], "value": [i]},
                )
                for i in range(1, maxValue)
            ],
        )

        with m.If(tb.matchesStory("After reset has been negated")):
            m.d.sync += Assert(counter.value == 1)
        for i in range(0, maxValue):
            with m.If(tb.matchesStory(f"After value has reached {i}")):
                m.d.sync += Assert(counter.value == (i + 1))

    Test.describe(RippleCounter(3), testBody)


def test_RippleCounter_shouldReturnToZeroAfterReachingMaxValueSupportedByTheWidth():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        maxRange = 2**width
        maxValue = maxRange - 1

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={"rst": rst, "value": counter.value},
            stories=[
                Story(
                    "After the counter has reached the max value",
                    {"rst": [0], "value": [maxValue]},
                ),
            ],
        )
        with m.If(tb.matchesStory("After the counter has reached the max value")):
            m.d.sync += Assert(counter.value == 0)

    Test.describe(RippleCounter(3), testBody)


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

    Test.describe(SlowRippleCounter(3), testBody)


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

    Test.describe(SlowRippleCounter(3), testBody)


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

    Test.describe(SlowRippleCounter(3), testBody)


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

    Test.describe(SlowRippleCounter(3), testBody)
