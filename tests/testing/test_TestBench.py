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

### amaranth -- main deps
from amaranth import *

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### amarant-stuff deps
from amaranth_stuff.testing.TestBench import *
from amaranth_stuff.testing import Test


###
### Test suite on TestBench
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
        b = tb.registerPort(Signal(name="b", reset=1))
        assert len(tb.ports()) == 2
        assert b.name == "b"  # should leave named signals as they are
        c = tb.registerPort(Signal())
        assert len(tb.ports()) == 3
        assert (
            c.name == "test_bench_2"
        )  # should give a serialized name to unnamed signals

        m.d.sync += b.eq(~a)
        m.d.sync += c.eq(a)

        with m.If(~Past(rst) & ~rst & Past(a)):
            m.d.sync += [Assert(~b)]
            m.d.sync += [Assert(c)]
        with m.If(~Past(rst) & ~rst & ~Past(a)):
            m.d.sync += [Assert(b)]
            m.d.sync += [Assert(~c)]

    Test.describe(TestBench(), testBody)


def test_with_failing_test():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.dut

        a = tb.registerPort(Signal())
        b = tb.registerPort(Signal(name="b", reset=1))
        m.d.sync += b.eq(~a)

        with m.If(~Past(rst) & ~rst & Past(a)):
            m.d.sync += [Assert(b)]  # should fail, b is setup to be (~a)

    with pytest.raises(CalledProcessError):
        Test.describe(TestBench(), testBody)


def test_testBench_is_a_submodule_of_m():
    class Dummy(Elaboratable):
        def __init__(self):
            self._ports = []

        def ports(self) -> List[Signal]:
            return self._ports

        def elaborate(self, platform: Platform) -> Module:
            m = Module()
            return m

    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench

        a = tb.registerPort(Signal())
        b = tb.registerPort(Signal(name="b", reset=1))
        m.d.sync += b.eq(~a)

        with m.If(~Past(rst) & ~rst & Past(a)):
            m.d.sync += [Assert(~b)]  # should succeed

    Test.describe(Dummy(), testBody)
