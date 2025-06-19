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
from amaranth import Elaboratable, Module, Mux, Signal
from amaranth.build import Platform


class Delay(Elaboratable):
    """Generate logic that wait the specified amount of clock cycles before asserting its output."""

    def __init__(self, delay: int = 0):
        self.delay = Signal(range(delay + 1), init=delay)
        self.dataOut = Signal()
        self.dataOutInverted = Signal(init=1)

    def ports(self) -> List[Signal]:
        return [self.delay, self.dataOut, self.dataOutInverted]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # BEGIN combinatorial logic
        m.d.comb += [self.dataOutInverted.eq(~self.dataOut)]

        # BEGIN synchronized logic
        with m.If(self.delay == 0):
            m.d.sync += [self.dataOut.eq(1)]
        with m.Else():
            m.d.sync += [self.delay.eq((self.delay - 1)[0 : len(self.delay)])]

        return m
