"""
---
(c) 2022~2025 David SPORN
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

### amarant-stuff deps
from general_logic_for_amaranth import MonoImpulse
from testing_for_amaranth import Story, TestSuiteRunner


def test_MonoImpulse():
    TestSuiteRunner(
        lambda: MonoImpulse(),
        lambda dut, clockDomain: {
            "rst": clockDomain.rst,
            "dout": dut.dataOut,
            "doutinv": dut.dataOutInverted,
        },
        [
            Story(
                "Should pulse only once",
                {
                    "rst": [1] + [0, 0, 0, 0],
                    "dout": [0] + [1, 0, 0, 0],
                    "doutinv": [1] + [0, 1, 1, 1],
                },
                given=["rst"],
            ),
        ],
    ).run()
