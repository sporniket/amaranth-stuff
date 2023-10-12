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
from subprocess import CalledProcessError
import pytest

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.testing import Test, Story
from amaranth_stuff.modules import DelayTimer8Bits


def test_DelayTimer8Bits_should_use_default_values_as_expected():
    stories = [
        Story(
            "for 5 cycle after reset",
            {
                "rst": [1, 0, 0, 0, 0, 0],
                "enable": [1, 1, 1, 1, 1, 1],
                "prescalerStrobe": [0, 0, 0, 0, 0, 0],
                "counterStrobe": [0, 0, 0, 0, 0, 0],
            },
        )
    ]

    def testStory(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        timer = m.submodules.dut

        tb.givenStoryBook(
            participants={
                "rst": rst,
                "enable": timer.enable,
                "prescalerStrobe": timer.dataRegisterWrite.prescalerStrobe,
                "counterStrobe": timer.dataRegisterWrite.counterStrobe,
            },
            stories=stories,
        )

        with m.If(tb.matchesStory("for 5 cycle after reset")):
            m.d.sync += Assert(rst == 1)  # MUST fail

    def testBehaviour(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        timer = m.submodules.dut

        tb.givenStoryBook(
            participants={
                "rst": rst,
                "enable": timer.enable,
                "prescalerStrobe": timer.dataRegisterWrite.prescalerStrobe,
                "counterStrobe": timer.dataRegisterWrite.counterStrobe,
                "counter": timer.timerOutput.counter,
                "timeout": timer.timerOutput.timeout,
                "beat": timer.timerOutput.beat,
            },
            stories=stories,
        )

        with m.If(tb.matchesStory("for 5 cycle after reset")):
            m.d.sync += tb.verifyLogs("counter", [2, 1, 0, 2, 1, 0])
            m.d.sync += tb.verifyLogs("timeout", [0, 0, 1, 0, 0, 1])
            m.d.sync += tb.verifyLogsAndNow("beat", [0, 0, 0, 1, 1, 1, 0])

    with pytest.raises(CalledProcessError):
        Test.perform(
            DelayTimer8Bits(1, 2, enable=1), testStory, description="verify story"
        )

    Test.perform(
        DelayTimer8Bits(1, 2, enable=1), testBehaviour, description="verify behaviour"
    )
