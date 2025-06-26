"""
---
(c) 2022~2025 David SPORN
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
from amaranth.hdl import ClockDomain, Module
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.hdl import Assert

### amarant-stuff deps
from general_logic_for_amaranth import SlowBeat
from testing_for_amaranth import TestRunner, Story, TestSuiteRunner


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


def test_SlowBeat():
    TestSuiteRunner(
        lambda: SlowBeat(5),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "dout": dut.beat_p,
            "doutInverted": dut.beat_n,
        },
        [
            Story(
                "should toggle at each clock at max frequency",
                {
                    "rst": [1, 0, 0, 0] + [0, 0, 0, 0] + [0, 0, 0, 0],
                    "dout": [1, 0, 1, 0] + [1, 0, 1, 0] + [1, 0, 1, 0],
                    "doutInverted": [0, 1, 0, 1] + [0, 1, 0, 1] + [0, 1, 0, 1],
                },
                given=["rst"],
            ),
        ],
        platform=DummyPlatformWith10HzDefaultClock(),
    ).run()
    TestSuiteRunner(
        lambda: SlowBeat(2),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "dout": dut.beat_p,
            "doutInverted": dut.beat_n,
        },
        [
            Story(
                "should round the period length to the highest even value",
                {
                    "rst": [1, 0, 0, 0] + [0, 0, 0, 0] + [0, 0, 0, 0],
                    "dout": [1, 1, 0, 0] + [1, 1, 0, 0] + [1, 1, 0, 0],
                    "doutInverted": [0, 0, 1, 1] + [0, 0, 1, 1] + [0, 0, 1, 1],
                },
                given=["rst"],
            ),
        ],
        platform=DummyPlatformWith10HzDefaultClock(),
    ).run()
