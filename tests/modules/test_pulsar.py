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
from amaranth import ClockDomain, Module, Signal, unsigned

### amaranth -- test deps
from amaranth.hdl import Assert

### amarant-stuff deps
from amaranth_stuff.modules import Pulsar
from amaranth_stuff.testing import TestRunner, Story, TestSuiteRunner


def test_Pulsar():
    TestSuiteRunner(
        lambda: Pulsar(3),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "dout": dut.dataOut,
            "doutinv": dut.dataOutInverted,
        },
        [
            Story(
                "Should pulse regularly",
                {
                    "rst": [1] + [0, 0, 0, 0] + [0, 0, 0, 0],
                    "dout": [0] + [1, 0, 0, 0] + [1, 0, 0, 0],
                    "doutinv": [1] + [0, 1, 1, 1] + [0, 1, 1, 1],
                },
                given=["rst"],
            ),
        ],
    ).run()
