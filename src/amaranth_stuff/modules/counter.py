"""
---
(c) 2022 David SPORN
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
from amaranth import *
from amaranth.build import Platform


class RippleCounter(Elaboratable):
    """Counter that is incremented at each clock ; the value has the specified width."""

    def __init__(self, width: int):
        self.width = width
        self.value = Signal(width)

    def ports(self) -> List[Signal]:
        return [self.value]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.sync += [self.value.eq((self.value + 1)[0 : self.width])]

        return m


class SlowRippleCounter(Elaboratable):
    """Counter that is incremented on each leading edge of the active high `beat` input."""

    def __init__(self, width: int):
        self.width = width
        self.value = Signal(width)
        self.beat = Signal()

    def ports(self) -> List[Signal]:
        return [self.beat, self.value]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        previousBeatValue = Signal()
        with m.If((self.beat != previousBeatValue)):
            m.d.sync += [previousBeatValue.eq(self.beat)]
            with m.If((self.beat == 1)):
                m.d.sync += [self.value.eq((self.value + 1)[0 : self.width])]

        return m
