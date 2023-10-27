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


class Sequencer(Elaboratable):
    def __init__(self, program: List[int]):
        for step in program:
            if step == 0:
                raise ValueError("A step MUST have a duration of at least one cycle !")
        self.steps = Signal(len(program))
        self._maxCounter = sum(program)
        self.counter = Signal(range(0, self._maxCounter))
        self._program = program
        self.reset = Signal(reset=1)  # synchronous reset

    def ports(self) -> List[Signal]:
        return [self.steps]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        with m.If(self.reset):
            # synchronous reset
            m.d.sync += [self.reset.eq(0), self.steps.eq(1)]

        with m.Else():
            # Run counter
            m.d.sync += self.counter.eq((self.counter + 1)[0 : self.counter.width])
            trigger = 0

            # Assert next step after each duration
            for step in self._program[:-1]:
                trigger = trigger + step - 1
                with m.If(self.counter == trigger):
                    m.d.sync += self.steps.eq(Cat(self.steps[-1], self.steps[:-1]))

            # Cycle counter, reset sequence
            trigger += self._program[-1] - 1
            with m.If(self.counter == trigger):
                m.d.sync += [self.counter.eq(0), self.steps.eq(1)]

        return m
