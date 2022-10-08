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
### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

### test deps ###
from amaranth.sim import Simulator, Delay, Settle
from amaranth.cli import (
    main_parser,
)  # READ amaranth/cli.py to find out parameters and what it does.
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial
from amaranth.back import rtlil, cxxrtl, verilog
from amaranth._toolchain import require_tool
import inspect
import subprocess
import re

from amaranth_stuff import Demux


class Test:
    """Just a collection of utilities"""

    @staticmethod
    def _clockDomain(name="sync") -> ClockDomain:
        """Retrieve the named clock domain and make sure it has a rst signal"""
        cd = ClockDomain(name)
        cd.rst = (
            Signal()
        )  # FIXME only if cd.rst does not exist (no such attribute or none)
        return cd

    @staticmethod
    def _buildTestBench(dut: Elaboratable, test) -> Module:
        m = Module()
        cd = Test._clockDomain("sync")
        m.domains.sync = cd
        m.submodules.dut = dut
        test(m, cd)
        return m

    @staticmethod
    def _asSafeName(description: str) -> str:
        safeName = re.sub("[ '\"()\\[\\]]", "-", description)
        safeName = re.sub("[.]+", " ", safeName)
        safeName = safeName.strip()
        safeName = re.sub("[ ]+", "_", safeName)
        safeName = re.sub("[-]*[_][-_]*", "_", safeName)
        return safeName

    @staticmethod
    def _generateSbyConfig(sbyName: str, ilName: str, depth: int):
        print(f"Generating {sbyName}...")
        with open(sbyName, "wt") as f:
            f.write(
                "\n".join(
                    [
                        "[tasks]",
                        "bmc",
                        "cover",
                        "",
                        "[options]",
                        "bmc: mode bmc",
                        "cover: mode cover",
                        f"depth {depth}",
                        "multiclock off",
                        "",
                        "[engines]",
                        "smtbmc boolector",
                        "",
                        "[script]",
                        f"read_ilang {ilName}",
                        "prep -top top",
                        "",
                        "[files]",
                        f"{ilName}",
                    ]
                )
            )

    @staticmethod
    def describe(
        description: str, dut: Elaboratable, test, depth: int, platform: Platform = None
    ):
        """Perform a test on amaranth module using SymbiYosis (sby)

        Args:
            description (str): A distinctive, one line description ; file names will be derived from the description.
            dut (Elaboratable): The amaranth module to test
            test (_type_): a function(m:Module, cd:ClockDomain) that will append assertions tho the given module.
            depth (int): The depth of the formal verification to perform
            platform (Platform): the test platform
        """
        print(f"##########>")
        print(f"##########> {description}")
        print(f"##########>")
        baseName = Test._asSafeName(description)
        ilName = f"tmp.{baseName}.il"
        sbyName = f"tmp.{baseName}.sby"

        m = Test._buildTestBench(dut, test)
        fragment = Fragment.get(m, platform)
        output = rtlil.convert(
            fragment,
            ports=dut.ports(),
        )
        print(f"Generating {ilName}...")
        with open(ilName, "wt") as f:
            f.write(output)
        Test._generateSbyConfig(sbyName, ilName, depth)

        invoke_args = [require_tool("sby"), "-f", sbyName]
        print(f"Running sby -f {' '.join(invoke_args)}...")
        with subprocess.Popen(invoke_args) as proc:
            if proc.returncode is not None and proc.returncode != 0:
                exit(proc.returncode)


def shouldAssertTheCorrectBitWhenInputIsInRange(m: Module, cd: ClockDomain):
    rst = cd.rst
    demux = m.submodules.dut
    channelCount = demux.channelCount
    for i in range(0, channelCount):
        with m.If(~Past(rst) & (Past(demux.input) == i)):
            m.d.sync += [
                Assert(demux.output == (1 << i)),
                Assert(~(demux.outOfRange)),
            ]


def shouldAssertTheErrorBitWhenInputIsOutOfRange(m: Module, cd: ClockDomain):
    rst = cd.rst
    demux = m.submodules.dut
    channelCount = demux.channelCount
    with m.If(~Past(rst) & (Past(demux.input) == channelCount)):
        m.d.sync += [Assert(demux.output == 0), Assert(demux.outOfRange)]


def run(width: int):
    dut = Demux(
        (1 << 2) - 1
    )  # meaning that there is 1 invalid input for testing the error signal of demux
    Test.describe(
        "should assert the correct bit according to input",
        dut,
        shouldAssertTheCorrectBitWhenInputIsInRange,
        2,
    )
    Test.describe(
        "should assert the error bit when input is out of range",
        dut,
        shouldAssertTheErrorBitWhenInputIsOutOfRange,
        2,
    )


def test_all():
    """To be run using 'python3 -m pytest test_demux.py'"""
    run(16)


if __name__ == "__main__":
    run(8)
