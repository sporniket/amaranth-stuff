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
from amaranth.hdl import Elaboratable, Module, Signal
from amaranth.build import Platform

### amarant-stuff deps
from testing_for_amaranth.TestBench import Story, TestBench
from testing_for_amaranth import TestSuiteRunner

### utils for testing
from .assert_TestRunnerDidWork import (
    thenTestRunnerDidWorkedAsExpectedWithSuccess,
)


###
### Test suite on TestSuiteRunner -- run
###


def test_TestSuiteRunner_run__should_run_for_each_stories():
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

    TestSuiteRunner(
        lambda: DummyCounter(2),
        lambda dut, clockDomain: {
            "rst": dut.reset,
            "cs": dut.chipSelect,
            "out": dut.out,
        },
        [
            Story(
                "nominal",
                {"rst": [1, 0, 0], "cs": [1, 1, 1], "out": [2]},
                given=["rst", "cs"],
            ),
            Story(
                "cycle",
                {"rst": [1, 0, 0, 0, 0], "cs": [1, 1, 1, 1, 1], "out": [0]},
                given=["rst", "cs"],
            ),
            Story(
                "reset happens",
                {"rst": [1, 0, 0, 1, 0], "cs": [1, 1, 1, 1, 1], "out": [1]},
                given=["rst", "cs"],
            ),
        ],
    ).run()

    thenTestRunnerDidWorkedAsExpectedWithSuccess("nominal")
    thenTestRunnerDidWorkedAsExpectedWithSuccess("cycle")
    thenTestRunnerDidWorkedAsExpectedWithSuccess("reset_happens")
