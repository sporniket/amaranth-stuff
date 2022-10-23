"""
---
(c) 2022 David SPORN
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
from amaranth_stuff.testing import Test

###
### Test suite on RippleCounter
###


def test_RippleCounter_shouldIncrementValueAtEachClock():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        for i in range(1, 2**width - 1):  # Does not work for i = 0 !!
            with m.If(~Past(rst) & (Past(counter.value) == Const(i, unsigned(width)))):
                m.d.sync += [Assert(counter.value == Const(i + 1, unsigned(width)))]

    Test.describe(RippleCounter(3), testBody)


def test_RippleCounter_shouldReturnToZeroAfterReachingMaxValueSupportedByTheWidth():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        with m.If(~Past(rst) & (Past(counter.value) == (2**width - 1))):
            m.d.sync += [Assert(counter.value == 0)]

    Test.describe(RippleCounter(3), testBody)


###
### Test suite on SlowRippleCounter
###


def test_SlowRippleCounter_shouldIncrementValueAtEachBeatLeadingEdge():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        for i in range(0, 2**width - 1):
            with m.If(
                ~Past(rst)
                & (Past(counter.value) == i)
                & (~Past(counter.beat, 2))
                & (Past(counter.beat))
            ):
                m.d.sync += [Assert(counter.value == (i + 1))]

    Test.describe(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldReturnToZeroAfterReachingMaxValueSupportedByTheWidth():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        with m.If(
            ~Past(rst)
            & (Past(counter.value) == (2**width - 1))
            & (~Past(counter.beat, 2))
            & (Past(counter.beat))
        ):
            m.d.sync += [Assert(counter.value == 0)]

    Test.describe(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldKeepValueAtEachBeatTrailingEdge():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        for i in range(0, 2**width):
            with m.If(
                ~Past(rst)
                & (Past(counter.value) == i)
                & (Past(counter.beat, 2))
                & (~Past(counter.beat))
            ):
                m.d.sync += [Assert(counter.value == i)]

    Test.describe(SlowRippleCounter(3), testBody)


def test_SlowRippleCounter_shouldKeepValueWhenBeatDoesNotChange():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        for i in range(1, 2**width):  # Does not work for i = 0 !!
            with m.If(
                ~Past(rst)
                & (Past(counter.value) == i)
                & (Past(counter.beat, 2))
                & (Past(counter.beat))
            ):
                m.d.sync += [Assert(counter.value == i)]
            with m.If(
                ~Past(rst)
                & (Past(counter.value) == i)
                & (~Past(counter.beat, 2))
                & (~Past(counter.beat))
            ):
                m.d.sync += [Assert(counter.value == i)]

    Test.describe(SlowRippleCounter(3), testBody)
