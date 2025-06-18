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

import pytest
from subprocess import CalledProcessError
from typing import List

### amaranth -- main deps
from amaranth import ClockDomain, Elaboratable, Module, Signal
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.hdl import Assert

### amarant-stuff deps
from amaranth_stuff.testing.TestBench import Story, TestBench
from amaranth_stuff.testing import TestRunner


###
### Test suite on TestBench -- basic features
###


def test_testbench_can_register_new_ports():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.dut
        assert len(tb.ports()) == 0

        a = tb.registerPort(Signal())
        assert len(tb.ports()) == 1
        assert (
            a.name == "test_bench_0"
        )  # should give a serialized name to unnamed signals
        b = tb.registerPort(Signal(name="b", init=1))
        assert len(tb.ports()) == 2
        assert b.name == "b"  # should leave named signals as they are
        c = tb.registerPort(Signal())
        assert len(tb.ports()) == 3
        assert (
            c.name == "test_bench_2"
        )  # should give a serialized name to unnamed signals

        m.d.sync += b.eq(~a)
        m.d.sync += c.eq(a)

        # Use the framework testbench
        ftb = m.submodules.testBench
        ftb.givenStoryBook(
            participants={"rst": rst, "a": a},
            stories=[
                Story("after asserting a", {"rst": [0, 0], "a": [1]}),
                Story("after negating a", {"rst": [0, 0], "a": [0]}),
            ],
        )

        with m.If(ftb.matchesStory("after asserting a")):
            m.d.sync += [Assert(~b), Assert(c)]

        with m.If(ftb.matchesStory("after negating a")):
            m.d.sync += [Assert(b), Assert(~c)]

    TestRunner.perform(TestBench(), testBody)


def test_with_failing_test():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.dut

        a = tb.registerPort(Signal())
        b = tb.registerPort(Signal(name="b", init=1))
        m.d.sync += b.eq(~a)

        # Use the framework testbench
        ftb = m.submodules.testBench
        ftb.givenStoryBook(
            participants={"rst": rst, "a": a},
            stories=[Story("after asserting a", {"rst": [0, 0], "a": [1]})],
        )

        with m.If(ftb.matchesStory("after asserting a")):
            m.d.sync += Assert(b)  # MUST fail : b is setup to be (~a)

    with pytest.raises(CalledProcessError):
        TestRunner.perform(TestBench(), testBody)


###
### Test suite on TestBench -- storybook features
###


def test_testBench_provide_helper_to_test_stories():
    class DummyCounter(Elaboratable):
        def __init__(self, width):
            self.out = Signal(width)
            self.chipSelect = Signal()
            self.reset = Signal()

        def ports(self) -> List[Signal]:
            return [self.reset, self.chipSelect, self.out]

        def elaborate(self, platform: Platform) -> Module:
            m = Module()

            with m.If(self.reset):
                m.d.sync += self.out.eq(0)
            with m.Elif(self.chipSelect):
                m.d.sync += self.out.eq((self.out + 1)[0:2])

            return m

    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        counter = m.submodules.dut

        tb.givenStoryBook(
            participants={"rst": counter.reset, "cs": counter.chipSelect},
            stories=[
                Story("nominal", {"rst": [1, 0, 0], "cs": [1, 1, 1]}),
                Story(
                    "cycle",
                    {
                        "rst": [1, 0, 0, 0, 0],
                        "cs": [1, 1, 1, 1, 1],
                    },
                ),
                Story(
                    "reset happens",
                    {
                        "rst": [1, 0, 0, 1, 0],
                        "cs": [1, 1, 1, 1, 1],
                    },
                ),
            ],
        )

        with m.If(tb.matchesStory("nominal")):
            m.d.sync += Assert(counter.out == 2)
        with m.If(tb.matchesStory("cycle")):
            m.d.sync += Assert(counter.out == 0)
        with m.If(tb.matchesStory("reset happens")):
            m.d.sync += Assert(counter.out == 1)

    TestRunner.perform(DummyCounter(2), testBody)


def test_testBench_provide_helper_to_verify_the_content_of_a_logger():
    class DummySynchronousNotGate(Elaboratable):
        def __init__(self):
            self.dataIn = Signal()
            self.dataOut = Signal()

        def ports(self) -> List[Signal]:
            return [self.dataIn, self.dataOut]

        def elaborate(self, platform: Platform) -> Module:
            m = Module()
            m.d.sync += self.dataOut.eq(~self.dataIn)
            return m

    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        gate = m.submodules.dut

        tb.givenStoryBook(
            participants={"rst": rst, "din": gate.dataIn, "dout": gate.dataOut},
            stories=[
                Story(
                    "typical",
                    {
                        "din": [1, 0, 0, 1, 0, 0, 1, 0]
                    },  # require the story to start with one to have meaningfull logger values.
                ),
            ],
        )

        logger = tb._loggers["dout"]

        with m.If(tb.matchesStory("typical")):
            m.d.sync += tb.verifyLogs("dout", [1, 1, 0, 1, 1, 0])

    TestRunner.perform(DummySynchronousNotGate(), testBody)


def test_testBench_provide_helper_to_verify_the_content_of_a_logger_and_the_current_value():
    class DummySynchronousNotGate(Elaboratable):
        def __init__(self):
            self.dataIn = Signal()
            self.dataOut = Signal()

        def ports(self) -> List[Signal]:
            return [self.dataIn, self.dataOut]

        def elaborate(self, platform: Platform) -> Module:
            m = Module()
            m.d.sync += self.dataOut.eq(~self.dataIn)
            return m

    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        gate = m.submodules.dut

        tb.givenStoryBook(
            participants={"rst": rst, "din": gate.dataIn, "dout": gate.dataOut},
            stories=[
                Story(
                    "typical",
                    {"din": [1, 0, 0, 1, 0, 0, 1, 0]},
                ),
            ],
        )

        with m.If(tb.matchesStory("typical")):
            m.d.sync += tb.verifyLogsAndNow("dout", [1, 1, 0, 1, 1, 0, 1])

    TestRunner.perform(DummySynchronousNotGate(), testBody)
