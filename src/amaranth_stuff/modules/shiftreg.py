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

### builtin deps
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth import Cat, Elaboratable, Module, Signal
from amaranth.build import Platform


class ShiftRegisterSendLsbFirst(Elaboratable):
    def __init__(self, dataIn: Signal, phase=0):
        self.dataIn = dataIn
        self.load = Signal()
        self.dataOut = Signal()
        self.dataOutInverted = Signal(reset=1)
        self._nextLoad = Signal()
        self._buffer = Signal.like(dataIn)
        self._state = Signal(dataIn.shape(), reset=(1 << (phase % dataIn.width)))
        self._syncReset = Signal(reset=1)

    def ports(self) -> List[Signal]:
        return [self.dataIn, self.load, self.dataOutInverted, self.dataOut]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # BEGIN combinatorial part

        m.d.comb += [
            self._nextLoad.eq(self._state[0]),
            self.dataOutInverted.eq(~self.dataOut),
        ]

        with m.If(self._syncReset == 0):
            nextState = Signal.like(self._state)
            m.d.comb += nextState.eq(Cat(self._state[1:], self._state[0]))

            nextBuffer = Signal.like(self._buffer)
            with m.If(self._nextLoad == 1):
                m.d.comb += nextBuffer.eq(self.dataIn)
            with m.Else():
                m.d.comb += nextBuffer.eq(Cat(self._buffer[1:], 0))

        # BEGIN synchronized part
        with m.If(self._syncReset == 1):
            m.d.sync += self._syncReset.eq(0)
        with m.Else():
            m.d.sync += [
                self.load.eq(self._nextLoad),
                self._buffer.eq(nextBuffer),
                self.dataOut.eq(nextBuffer[0]),
                self._state.eq(nextState),
            ]
        return m
