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
from amaranth import *

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.modules import ShiftRegisterSendLsbFirst
from amaranth_stuff.testing import Test, Story


def test_ShiftRegisterSendLsbFirst_should_serialize_data_in():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        shiftRegister = m.submodules.dut

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={
                "rst": rst,
                "load": shiftRegister.load,
                "din": shiftRegister.dataIn,
                "dout": shiftRegister.dataOut,
                "doutinv": shiftRegister.dataOutInverted,
            },
            stories=[
                Story(
                    "On load+4",
                    {"load": [1, 0, 0, 0, 1], "din": [0b1011, 0, 0, 0, 0, 0]},
                ),
            ],
        )

        with m.If(tb.matchesStory("On load+4")):
            m.d.sync += [
                Assert(shiftRegister.load == 0),
                Assert(shiftRegister.dataOut == 0),
                Assert(shiftRegister.dataOutInverted == 1),
                tb.verifyLogs("dout", [1, 1, 0, 1, 0]),
                tb.verifyLogs("doutinv", [0, 0, 1, 0, 1]),
            ]

    Test.perform(
        ShiftRegisterSendLsbFirst(Signal(unsigned(4), name="dataIn")), testBody
    )


def test_ShiftRegisterSendLsbFirst_should_delay_load_by_phase():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        shiftRegister = m.submodules.dut
        m.submodules.ref = shiftRegisterReference = ShiftRegisterSendLsbFirst(
            shiftRegister.dataIn
        )

        tb = m.submodules.testBench
        tb.givenStoryBook(
            participants={
                "rst": rst,
                "load": shiftRegister.load,
                "loadref": shiftRegisterReference.load,
            },
            stories=[
                Story(
                    "Reference load",
                    {"loadref": [1, 0, 0, 0, 1, 0, 0, 0, 1]},
                ),
            ],
        )

        with m.If(tb.matchesStory("Reference load")):
            m.d.sync += [
                tb.verifyLogs("load", [0, 0, 1, 0, 0, 0, 1, 0, 0]),
            ]

    Test.perform(
        ShiftRegisterSendLsbFirst(Signal(unsigned(4), name="dataIn"), 6), testBody
    )
