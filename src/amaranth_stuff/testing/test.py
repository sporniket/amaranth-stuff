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
import inspect
import os
import re
import subprocess
import sys

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform

### amaranth -- testing
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial
from amaranth.back import rtlil  # , cxxrtl, verilog
from amaranth._toolchain import require_tool  # May need to be re-implemented locally


class Test:
    """Just a collection of utilities"""

    @staticmethod
    def _generateTestBench(ilName: str, dut: Elaboratable, test, platform: Platform):
        ###
        # Keep references to the clock domain and the reset signal
        # to add them to the ports
        # otherwise the verification always pass !!
        sync = ClockDomain("sync")
        rst = Signal()
        sync.rst = rst

        ###
        # Prepare testbench and convert to rtlil
        m = Module()
        m.domains.sync = sync
        m.submodules.dut = dut
        test(m, sync)

        fragment = Fragment.get(m, platform)
        output = rtlil.convert(
            fragment,
            ports=dut.ports() + [sync.rst, sync.clk],
        )
        with open(ilName, "wt") as f:
            f.write(output)

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
                        "[options]",
                        "mode bmc",
                        f"depth {depth}",
                        "",
                        "[engines]",
                        "smtbmc",
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
        dut: Elaboratable,
        test,
        *,
        description: str = None,
        depth: int = 20,
        platform: Platform = None,
    ):
        """Perform a test on amaranth module using SymbiYosis (sby)

        Args:
            description (str): A distinctive, one line description ; file names will be derived from the description.
            dut (Elaboratable): The amaranth module to test
            test : a function(m:Module, cd:ClockDomain) that will append assertions tho the given module.
            depth (int): The depth of the formal verification to perform
            platform (Platform): the test platform
        """
        if description is None:
            currFrame = inspect.currentframe()
            callFrameStack = inspect.getouterframes(currFrame)
            description = callFrameStack[1][3]
            if callFrameStack[1][3] == "__main__":
                description = test.__name__
        print(f"##########>")
        print(f"##########> {description}")
        print(f"##########>")
        baseName = Test._asSafeName(description)
        ilName = f"tmp.{baseName}.il"
        sbyName = f"tmp.{baseName}.sby"

        print(f"Generating {ilName}...")
        Test._generateTestBench(ilName, dut, test, platform)
        Test._generateSbyConfig(sbyName, ilName, depth)

        invoke_args = [require_tool("sby"), "-f", sbyName]
        print(f"Running {' '.join(invoke_args)}...")
        subprocess.run(invoke_args).check_returncode()
