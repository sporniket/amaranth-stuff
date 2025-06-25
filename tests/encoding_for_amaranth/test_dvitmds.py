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
from amaranth.hdl import Signal

### amarant-stuff deps
from encoding_for_amaranth import DviTmdsEncoder
from testing_for_amaranth import Story, TestSuiteRunner

###
### Test suite on DviTmdsEncoder
###


def test_DviTmdsEncoder():
    TestSuiteRunner(
        lambda: DviTmdsEncoder(
            Signal(8, name="dataIn"),
            Signal(name="vde"),
            Signal(name="ctl0"),
            Signal(name="ctl1"),
        ),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "vde": dut.videoDisplayEnable,
            "ctl0": dut.ctl0,
            "ctl1": dut.ctl1,
            "din": dut.dataIn,
            "dout": dut.dataOut,
            "cnt": dut.halfBalanceCounter,
            "thenCnt": dut.halfBalanceCounter,
        },
        [
            Story(
                f"When din is {test[0]} and cnt is {test[1]}",
                {
                    "rst": [0, 0],
                    "vde": [1],
                    "din": [test[0]],
                    "cnt": [test[1]],
                    "dout": [test[2]],
                    "thenCnt": [test[3]],
                },
                given=["rst", "vde", "din", "cnt"],
            )
            for test in [
                # data in , counter before, data out, counter after
                [0b11000000, 0, 0b0101000000, -3],
                [0b11000000, -3, 0b1110111111, 1],
                [0b11000000, 1, 0b0101000000, -2],
                [0b11110000, 0, 0b1000000101, -2],
                [0b11110000, -2, 0b0011111010, -1],
                [0b11110000, 2, 0b1000000101, 0],
                [0b00001111, 0, 0b0100000101, -2],
                [0b00001111, -2, 0b1111111010, 1],
                [0b00001111, 1, 0b0100000101, -1],
                [0b00111111, 0, 0b1001000000, -3],
                [0b00111111, -3, 0b0010111111, -1],
                [0b00111111, 2, 0b1001000000, -1],
                [0b01010101, 0, 0b0100110011, 0],
                [0b01010101, -2, 0b0100110011, -2],
                [0b01010101, 2, 0b0100110011, 2],
                [0b10101010, 0, 0b1000110011, 0],
                [0b10101010, -2, 0b1000110011, -2],
                [0b10101010, 2, 0b1000110011, 2],
            ]
        ]
        + [
            Story(
                f"When VDE is negated, ctl0 = {test[0]}, ctl1 = {test[1]}",
                {
                    "rst": [0, 0],
                    "vde": [0],
                    "ctl0": [test[0]],
                    "ctl1": [test[1]],
                    "dout": [test[2]],
                    "thenCnt": [0],
                },
                given=["rst", "vde", "ctl0", "ctl1"],
            )
            for test in [
                # ctl 0, ctl 1, data out
                [0, 0, 0b0010101011],
                [0, 1, 0b1101010100],
                [1, 0, 0b0010101010],
                [1, 1, 0b1101010101],
            ]
        ],
    ).run()
