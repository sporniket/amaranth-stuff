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


class SlowBeat(Elaboratable):
    """A clock signal that have a frequency of up to platform.default_clk_frequency/2 with 50% duty cycle"""

    def __init__(self, frequency: int):
        """Set up the target frequency.

        Args:
            freq (int): target frequency, in Hertz.
        """
        self.frequency = frequency
        self.beat_p = Signal(reset=1)  # the active high clock signal
        self.beat_n = Signal()  # the active low clock signal

    def ports(self) -> List[Signal]:
        return [self.beat_p, self.beat_n]

    def elaborate(self, platform: Platform) -> Module():
        # sanity check
        frequencyMax = platform.default_clk_frequency // 2
        if self.frequency > frequencyMax:
            raise ValueError(
                f"Cannot instanciate a slow beat of {self.frequency} Hz"
                f" when platform clock frequency is {platform.default_clk_frequency} Hz ;"
                f" Maximum allowed {frequencyMax} Hz "
            )

        m = Module()
        limit = int(platform.default_clk_frequency // self.frequency // 2)  # limit >= 1
        timer = Signal(range(limit), reset=limit - 1)

        m.d.comb += self.beat_n.eq(~self.beat_p)
        with m.If(timer == 0):
            m.d.sync += timer.eq(timer.reset)
            m.d.sync += self.beat_p.eq(~self.beat_p)
        with m.Else():
            m.d.sync += timer.eq(timer - 1)

        return m
