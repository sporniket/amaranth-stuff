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
from amaranth.hdl import Elaboratable, Module, Mux, Signal
from amaranth.build import Platform


class Decoder(Elaboratable):
    """Generate a decoder that supports an input in range [0..span[."""

    def __init__(self, span: int):
        if span < 2:
            raise ValueError("Decoder MUST have a span of at least 2.")
        self.span = span
        self.input = Signal(range(0, span))
        self.output = Signal(span, init=1)
        self.outOfRange = Signal()

    def ports(self) -> List[Signal]:
        return [self.input, self.output, self.outOfRange]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        previousInput = Signal(self.input.shape())
        with m.If(previousInput != self.input):
            m.d.sync += previousInput.eq(self.input)
            for i in range(0, self.span):
                m.d.sync += self.output[i].eq(Mux(self.input == i, 1, 0))
            m.d.sync += self.outOfRange.eq(Mux(self.input < self.span, 0, 1))

        return m
