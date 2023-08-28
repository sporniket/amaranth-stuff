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
from amaranth import *
from amaranth.build import Platform


class TestBench(Elaboratable):
    def __init__(self):
        self._ports = []

    def ports(self) -> List[Signal]:
        return self._ports

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        return m

    def registerPort(self, signal):
        if signal.name == "$signal":
            signal.name = f"test_bench_{len(self._ports)}"
            print(f"register signal name : {signal.name}")
        self._ports.append(signal)
        return signal
