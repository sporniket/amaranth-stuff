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
from amaranth.hdl import Elaboratable, Module, Signal
from amaranth.build import Platform


class Sequencer(Elaboratable):
    def __init__(self, program: List[int]):
        for step in program:
            if step == 0:
                raise ValueError("A step MUST have a duration of at least one cycle !")
        self.steps = Signal(len(program))
        self._maxCounter = sum(program) - 1
        self.counter = Signal(range(0, self._maxCounter))
        self._program = program
        self._boundaries = [
            0 if i == 0 else sum(program[0:i]) - 1 for i, v in enumerate(program)
        ]
        self.reset = Signal(init=1)  # synchronous reset

    def ports(self) -> List[Signal]:
        return [self.steps]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        with m.If(self.reset):
            # synchronous reset
            m.d.sync += [self.reset.eq(0), self.steps.eq(1)]

        with m.Else():
            # change value at each boundary
            for i, v in enumerate(self._boundaries):
                with m.If(self.counter == v):
                    m.d.sync += self.steps.eq(1 << i)

            # Run counter
            m.d.sync += self.counter.eq((self.counter + 1)[0 : len(self.counter)])
            with m.If(self.counter == self._maxCounter):
                m.d.sync += [self.counter.eq(0), self.steps.eq(1)]

        return m
