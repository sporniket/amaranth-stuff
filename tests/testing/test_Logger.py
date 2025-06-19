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
from amaranth import ClockDomain, Module, Signal, signed

### amaranth -- test deps
from amaranth.hdl import Assert

### amarant-stuff deps
from amaranth_stuff.testing.Logger import Logger
from amaranth_stuff.testing import TestRunner


###
### Test suite on Logger
###


def test_Logger_should_use_signals_with_same_shape_and_reset_value():
    logger = Logger(Signal(signed(5), init=3), 6)
    # This is a pure python test, so of course the logger will not be used.
    logger._MustUse__silence = True

    assert logger.source.shape().width == 5 and logger.source.shape().signed == True
    assert len(logger.logs) == 7
    for i in logger.logs:
        assert i.shape().width == 5 and i.shape().signed == True and i.init == 3


def test_Logger_should_log_signal_history():
    def testBody(m: Module, cd: ClockDomain):
        rst = cd.rst
        tb = m.submodules.testBench
        logger = m.submodules.dut

        din = tb.registerPort(
            logger.source
        )  # otherwise cannot manipulate the source of the logger.
        witness = [
            tb.registerPort(Signal()) for i in range(0, 6)
        ]  # 6 signals from 0 to 5
        m.d.sync += [witness[0].eq(din)] + [
            witness[i].eq(witness[i - 1]) for i in range(1, 6)
        ]

        # When witness exhibits the values [0,0,1,0,1,1]
        with m.If(
            ~witness[0]
            & ~witness[1]
            & witness[2]
            & ~witness[3]
            & witness[4]
            & witness[5]
        ):
            m.d.sync += Assert(
                ~logger.logs[0]
                & ~logger.logs[1]
                & logger.logs[2]
                & ~logger.logs[3]
                & logger.logs[4]
                & logger.logs[5]
            )

    TestRunner.perform(Logger(Signal(), 5), testBody)
