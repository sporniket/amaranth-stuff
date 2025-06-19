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
from amaranth.hdl import Elaboratable, Module, Signal, Const
from amaranth.build import Platform


class Pulsar(Elaboratable):
    def __init__(self, period: int = 1):
        self.dataOut = Signal()
        self.dataOutInverted = Signal(init=1)
        self._delay = Signal(Const(period).shape())
        self._period = period

    def ports(self) -> List[Signal]:
        return [self.dataOutInverted, self.dataOut]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # BEGIN combinatorial part

        m.d.comb += [
            self.dataOutInverted.eq(~self.dataOut),
        ]

        # BEGIN synchronized part
        with m.If(self._delay != 0):
            m.d.sync += [
                self._delay.eq((self._delay - 1)[0 : len(self._delay)]),
                self.dataOut.eq(0),
            ]
        with m.Else():
            m.d.sync += [self._delay.eq(self._period), self.dataOut.eq(1)]

        return m
