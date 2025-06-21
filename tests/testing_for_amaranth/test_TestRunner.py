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

import pytest
from subprocess import CalledProcessError

### amaranth -- main deps
from amaranth.hdl import Elaboratable, Module, Signal
from amaranth.build import Platform

### amarant-stuff deps
from testing_for_amaranth import TestRunner, Story

### utils for testing
from .assert_utils import (
    thenTestRunnerDidWorkedAsExpectedWithSuccess,
    thenTestRunnerDidWorkedAsExpectedWithFailure,
)


###
### Test suite on TestRunner -- run
###


def test_TestRunner_run__should_verify_reachability_and_behaviour():
    class DummyCounter(Elaboratable):
        def __init__(self, width):
            self.out = Signal(width)
            self.chipSelect = Signal()
            self.reset = Signal()

        def ports(self) -> list[Signal]:
            return [self.reset, self.chipSelect, self.out]

        def elaborate(self, platform: Platform) -> Module:
            m = Module()

            with m.If(self.reset):
                m.d.sync += self.out.eq(0)
            with m.Elif(self.chipSelect):
                m.d.sync += self.out.eq((self.out + 1)[0:2])

            return m

    TestRunner(
        lambda: DummyCounter(2),
        lambda dut, clockDomain: {
            "rst": dut.reset,
            "cs": dut.chipSelect,
            "out": dut.out,
        },
        Story(
            "nominal",
            {"rst": [1, 0, 0], "cs": [1, 1, 1], "out": [2]},
            given=["rst", "cs"],
        ),
    ).run()

    thenTestRunnerDidWorkedAsExpectedWithSuccess("nominal")


def test_TestRunner_run__should_fail_when_logic_is_wrong():
    class DummyCounter(Elaboratable):
        def __init__(self, width):
            self.out = Signal(width)
            self.chipSelect = Signal()
            self.reset = Signal()

        def ports(self) -> list[Signal]:
            return [self.reset, self.chipSelect, self.out]

        def elaborate(self, platform: Platform) -> Module:
            m = Module()

            with m.If(self.reset):
                m.d.sync += self.out.eq(0)
            with m.Elif(self.chipSelect):
                m.d.sync += self.out.eq((self.out + 1)[0:2])

            return m

    with pytest.raises(CalledProcessError):
        TestRunner(
            lambda: DummyCounter(2),
            lambda dut, clockDomain: {
                "rst": dut.reset,
                "cs": dut.chipSelect,
                "out": dut.out,
            },
            Story(
                "nominal",
                {"rst": [1, 0, 0], "cs": [1, 1, 1], "out": [1]},
                given=["rst", "cs"],
            ),
        ).run()

    thenTestRunnerDidWorkedAsExpectedWithFailure("nominal")
