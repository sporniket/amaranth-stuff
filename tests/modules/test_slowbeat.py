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
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.hdl import Assert

### amarant-stuff deps
from amaranth_stuff.modules import SlowBeat
from testing_for_amaranth import TestRunner, Story


# from .resources import *
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
        tb = m.submodules.testBench

        tb.givenStoryBook(
            participants={"rst": rst, "beat_p": slowbeat.beat_p},
            stories=[
                Story("After reset has been negated", {"rst": [1, 0]}),
                Story(
                    "After beat_p is up", {"rst": [0, 0], "beat_p": [0, 1]}
                ),  # requires full sequence for beat_p
                Story("After beat_p is down", {"rst": [0, 0], "beat_p": [0]}),
            ],
        )

        with m.If(tb.matchesStory("After reset has been negated")):
            m.d.sync += [
                Assert(slowbeat.beat_p == 0),
                Assert(slowbeat.beat_n == 1),
            ]
        with m.If(tb.matchesStory("After beat_p is up")):
            m.d.sync += [
                Assert(slowbeat.beat_p == 0),
                Assert(slowbeat.beat_n == 1),
            ]
        with m.If(tb.matchesStory("After beat_p is down")):
            m.d.sync += [
                Assert(slowbeat.beat_p == 1),
                Assert(slowbeat.beat_n == 0),
            ]

        m.d.sync += [Assert(slowbeat.beat_n == ~slowbeat.beat_p)]

    TestRunner.perform(
        SlowBeat(5),
        testBody,
        platform=DummyPlatformWith10HzDefaultClock(),
    )
