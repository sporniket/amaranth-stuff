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
from amaranth.hdl import Assert

### amarant-stuff deps
from amaranth_stuff.modules import Decoder
from amaranth_stuff.testing import TestRunner, Story, TestSuiteRunner


def test_Decoder():
    span = (1 << 2) - 1
    # there is 1 invalid input for testing the error signal of decoder
    TestSuiteRunner(
        lambda: Decoder(span),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "input": dut.input,
            "output": dut.output,
            "outOfRange": dut.outOfRange,
        },
        [
            Story(
                f"When input is {i}",
                {"rst": [0], "input": [i], "output": [1 << i], "outOfRange": [0]},
                given=["rst", "input"],
            )
            for i in range(0, span)
        ]
        + [
            Story(
                "When input is out of range",
                {"rst": [0], "input": [span], "output": [0], "outOfRange": [1]},
                given=["rst", "input"],
            )
        ],
    ).run()
