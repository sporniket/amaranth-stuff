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
from amaranth.lib.wiring import *
from amaranth.build import Platform


class SignatureOfDelayTimer(Signature):
    def __init__(self, counterWidth: int = 8):
        super().__init__(
            {
                "dataRegisterWrite": In(
                    Signature(
                        {
                            "dataIn": In(counterWidth),
                            "prescalerStrobe": In(1),
                            "counterStrobe": In(1),
                        }
                    )
                ),
                "enable": In(1),
                "timerOutput": Out(
                    Signature(
                        {
                            "counter": Out(counterWidth),
                            "timeout": Out(1),
                            "beat": Out(1),
                        }
                    )
                ),
            }
        )


class DelayTimer8Bits(Component):
    signature = SignatureOfDelayTimer().freeze()

    def __init__(self, prescaler: int = 1, counter: int = 1, *, enable: int = 0):
        super().__init__()
        self._prescaler = Signal(
            8, reset=1 if prescaler < 1 else 255 if prescaler > 255 else prescaler
        )
        self._counter = Signal(
            8, reset=1 if counter < 1 else 255 if counter > 255 else counter
        )
        if enable > 0:
            # override enable reset value
            self.enable.reset = Const.cast(1).value  # taken from Signal(...) code

    def ports(self) -> List[Signal]:
        return [
            self.dataRegisterWrite.dataIn,
            self.dataRegisterWrite.prescalerStrobe,
            self.dataRegisterWrite.counterStrobe,
            self.enable,
            self.timerOutput.counter,
            self.timerOutput.timeout,
            self.timerOutput.beat,
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        return m
