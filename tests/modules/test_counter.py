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
from amaranth_stuff.modules import RippleCounter
from amaranth_stuff.testing import Test


def test_shouldIncrementValueAtEachClock():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        for i in range(0, width - 1):
            with m.If(~Past(rst) & (Past(counter.value) == i)):
                m.d.sync += [Assert(counter.value == (i + 1))]

    Test.describe(
        "should increment value at each clock",
        RippleCounter(3),
        testBody,
        2,
    )


def test_shouldReturnToZeroAfterReachingMaxValueSupportedByTheWidth():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        counter = m.submodules.dut
        width = counter.width
        with m.If(~Past(rst) & (Past(counter.value) == (width - 1))):
            m.d.sync += [Assert(counter.value == 0)]

    Test.describe(
        "should return to zero after reaching the max value supported by the width",
        RippleCounter(3),
        testBody,
        2,
    )
