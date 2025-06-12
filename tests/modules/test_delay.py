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
from amaranth_stuff.modules import Delay
from amaranth_stuff.testing import TestRunner, Story, TestSuiteRunner


def test_Delay():
    TestSuiteRunner(
        lambda: Delay(5),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "dout": dut.dataOut,
            "doutInv": dut.dataOutInverted,
        },
        [
            Story(
                f"should delay assertion",
                {
                    "rst": [1, 0, 0, 0] + [0, 0, 0, 0],
                    "dout": [0, 0, 0, 0] + [0, 0, 1, 1],
                    "doutInv": [1, 1, 1, 1] + [1, 1, 0, 0],
                },
                given=["rst"],
            )
        ],
    ).run()
