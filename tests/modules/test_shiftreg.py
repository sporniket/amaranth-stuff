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
from amaranth.hdl import Signal, unsigned

### amarant-stuff deps
from amaranth_stuff.modules import ShiftRegisterSendLsbFirst
from testing_for_amaranth import TestRunner, Story, TestSuiteRunner


def test_ShiftRegisterSendLsbFirst():
    TestSuiteRunner(
        lambda: ShiftRegisterSendLsbFirst(Signal(unsigned(4), name="dataIn"), 6),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "load": dut.load,
            "din": dut.dataIn,
            "dout": dut.dataOut,
            "doutinv": dut.dataOutInverted,
        },
        [
            Story(
                "Phase should delay first load",
                {
                    "rst": [1, 0, 0, 0] + [0, 0, 0, 0] + [0, 0, 0, 0] + [0],
                    "din": [0, 0, 0, 0] + [0, 0, 0, 0] + [0b1011, 0, 0, 0] + [0],
                    "load": [0, 0, 0, 0] + [0, 0, 0, 1] + [0, 0, 0, 1] + [0],
                    "dout": [0, 0, 0, 0] + [0, 0, 0, 0] + [1, 1, 0, 1] + [0],
                },
                given=["rst", "din"],
            ),
        ],
    ).run()
