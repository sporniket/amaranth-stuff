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
from amaranth.hdl import Cat, Elaboratable, Module, Signal, Const
from amaranth.build import Platform


class ShiftRegisterSendLsbFirst(Elaboratable):
    def __init__(self, dataIn: Signal, delay=0):
        self.dataIn = dataIn
        self.load = Signal()
        self.dataOut = Signal()
        self.dataOutInverted = Signal(init=1)
        self._buffer = Signal.like(dataIn)
        self._state = Signal(dataIn.shape(), init=(1 << (len(dataIn) - 1)))
        self._delay = Signal(Const(delay).shape(), init=delay)

    def ports(self) -> list[Signal]:
        return [self.dataIn, self.load, self.dataOutInverted, self.dataOut]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # BEGIN combinatorial part

        m.d.comb += [
            #            self._nextLoad.eq(self._state[0]),
            self.dataOut.eq(self._buffer[0]),
            self.dataOutInverted.eq(~self.dataOut),
            self.load.eq(self._state[0]),
        ]

        # BEGIN synchronized part
        with m.If(self._delay != 0):
            m.d.sync += self._delay.eq((self._delay - 1)[0 : len(self._delay)])
        with m.Else():
            with m.If(self._state[0]):
                m.d.sync += [self._buffer.eq(self.dataIn)]
            with m.Else():
                m.d.sync += [self._buffer.eq(Cat(self._buffer[1:], 0))]

            m.d.sync += [
                self._state.eq(Cat(self._state[-1], self._state[0:-1])),
            ]

        return m
