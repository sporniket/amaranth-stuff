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
from amaranth import Elaboratable, Module, Signal
from amaranth.build import Platform


class Logger(Elaboratable):
    def __init__(self, source, size):
        self.source = source
        self.logs = [
            Signal.like(source, name=f"{source.name}_log_{i}")
            for i in range(0, size + 1)
        ]

    def ports(self):
        return self.logs

    def elaborate(self, platform):
        m = Module()

        m.d.sync += self.logs[0].eq(self.source)
        for i in range(1, len(self.logs)):
            m.d.sync += self.logs[i].eq(self.logs[i - 1])

        return m
