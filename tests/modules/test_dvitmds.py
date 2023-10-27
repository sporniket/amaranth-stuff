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
from amaranth import ClockDomain, Module, Signal

### amaranth -- test deps
from amaranth.asserts import Assert

### amarant-stuff deps
from amaranth_stuff.modules import DviTmdsEncoder
from amaranth_stuff.testing import Test, Story

###
### Test suite on DviTmdsEncoder
###


def test_DviTmdsEncoder_shouldEncodeDataCorrectly():
    def testFactory(whenDin, whenPrevCnt, thenDout, thenCnt):
        print(
            f"=== generate test body, whenDin={bin(whenDin)}, whenPrevCnt={whenPrevCnt}, thenDout={bin(thenDout)}, thenCnt={thenCnt} ==="
        )

        def testBody(m: Module, cd: ClockDomain):
            rst = cd.rst
            encoder = m.submodules.dut

            tb = m.submodules.testBench
            tb.givenStoryBook(
                participants={
                    "rst": rst,
                    "vde": encoder.ports()[1],
                    "din": encoder.ports()[0],
                    "cnt": encoder.halfBalanceCounter,
                },
                stories=[
                    Story(
                        "typical test",
                        {
                            "rst": [0, 0],
                            "vde": [1],
                            "din": [whenDin],
                            "cnt": [whenPrevCnt],
                        },
                    ),
                ],
            )

            with m.If(tb.matchesStory("typical test")):
                m.d.sync += [
                    Assert(encoder.ports()[-1] == thenDout),
                    Assert(encoder.halfBalanceCounter == thenCnt),
                ]

        return testBody

    for testData in [
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
    ]:
        Test.perform(
            DviTmdsEncoder(
                Signal(8, name="dataIn"),
                Signal(name="vde"),
                Signal(name="ctl0"),
                Signal(name="ctl1"),
            ),
            testFactory(testData[0], testData[1], testData[2], testData[3]),
            description=f"{testData[0]}.{testData[1]}.{testData[2]}.{testData[3]}",
        )


def test_DviTmdsEncoder_shouldSendControlDataWhenVdeIsNegated():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        encoder = m.submodules.dut

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={
                "rst": rst,
                "vde": encoder.ports()[1],
                "ctl0": encoder.ports()[2],
                "ctl1": encoder.ports()[3],
            },
            stories=[
                Story(
                    f"When VDE is negated and CTL[0:1] is {i}",
                    {"rst": [0, 0], "vde": [0], "ctl0": [i // 2], "ctl1": [i % 2]},
                )
                for i in range(0, 4)
            ],
        )

        ctlValues = [
            0b0010101011,
            0b1101010100,
            0b0010101010,
            0b1101010101,
        ]

        for i in range(0, 4):
            with m.If(tb.matchesStory(f"When VDE is negated and CTL[0:1] is {i}")):
                m.d.sync += [
                    Assert(encoder.ports()[-1] == ctlValues[i]),
                    Assert(encoder.halfBalanceCounter == 0),
                ]

    Test.perform(
        DviTmdsEncoder(
            Signal(8, name="dataIn"),
            Signal(name="vde"),
            Signal(name="ctl0"),
            Signal(name="ctl1"),
        ),
        testBody,
    )
