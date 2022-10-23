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
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.modules import SlowBeat
from amaranth_stuff.testing import Test


from amaranth_boards.resources import *  # from .resources import *
from amaranth.build import Resource, Clock, Pins


class DummyPlatformWith10HzDefaultClock(Platform):
    default_clk = "clk10"
    connectors = []
    resources = [
        Resource("clk10", 0, Pins("Whatever", dir="i"), Clock(10)),
    ]
    required_tools = []

    def toolchain_prepare(self, fragment, name, **kwargs):
        return None


def test_shouldBeatAtSpecifiedFrequency():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        slowbeat = m.submodules.dut
        with m.If(~Past(rst) & (Past(slowbeat.beat_p))):
            m.d.sync += [Assert(~slowbeat.beat_p)]
        with m.If(~Past(rst) & (~Past(slowbeat.beat_p))):
            m.d.sync += [Assert(slowbeat.beat_p)]
        m.d.sync += [Assert(slowbeat.beat_n == ~slowbeat.beat_p)]

    Test.describe(
        SlowBeat(5),
        testBody,
        platform=DummyPlatformWith10HzDefaultClock(),
    )
