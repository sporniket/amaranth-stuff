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
import inspect
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

### amaranth -- main deps
from amaranth import ClockDomain, Elaboratable, Fragment, Module, Signal
from amaranth.build import Platform

### amaranth -- testing
from amaranth.back import rtlil  # , cxxrtl, verilog
from amaranth._toolchain import require_tool  # May need to be re-implemented locally

### internal
from .TestBench import TestBench


class Test:
    """Just a collection of utilities"""

    @staticmethod
    def _generateTestBench(ilName: str, dut: Elaboratable, test, platform: Platform):
        ###
        # Keep references to the clock domain and the reset signal
        # to add them to the ports
        # otherwise the verification always pass !!
        sync = ClockDomain("sync")
        rst = Signal(reset=1)
        sync.rst = rst

        ###
        # Prepare testbench and convert to rtlil
        m = Module()
        m.domains.sync = sync
        m.submodules.dut = dut
        m.submodules.testBench = testBench = TestBench()
        test(m, sync)

        fragment = Fragment.get(m, platform)
        output = rtlil.convert(
            fragment,
            ports=dut.ports() + [sync.rst, sync.clk],
        )
        with open(ilName, "wt") as f:
            f.write(output)

        return testBench.requiredDepth

    @staticmethod
    def _asSafeName(description: str) -> str:
        safeName = re.sub("[ '\"()\\[\\]]", "_", description)
        safeName = re.sub("[.]+", " ", safeName)
        safeName = safeName.strip()
        safeName = re.sub("[ ]+", "_", safeName)
        safeName = re.sub("[-]", "_", safeName)
        return safeName

    @staticmethod
    def _generateSbyConfig(sbyName: str, ilName: str, depth: int):
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
    def perform(
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
        Path("build-tests").mkdir(parents=True, exist_ok=True)
        currFrame = inspect.currentframe()
        callFrameStack = inspect.getouterframes(currFrame)
        frameDescription = callFrameStack[1][3]
        if frameDescription == "__main__":
            frameDescription = test.__name__
        baseName = (
            frameDescription
            if description is None
            else f"{frameDescription}__{Test._asSafeName(description)}"
        )
        print(f"##########>")
        print(f"##########> {baseName}")
        print(f"##########>")
        ilName = f"{baseName}.il"
        sbyName = f"{baseName}.sby"

        print(f"Generating {ilName}...")
        requiredDepth = Test._generateTestBench(ilName, dut, test, platform)
        print(f"Generating {sbyName}...")
        Test._generateSbyConfig(sbyName, ilName, max([depth, requiredDepth]))

        invoke_args = [require_tool("sby"), "-f", sbyName]
        print(f"Running {' '.join(invoke_args)}...")
        runResult = subprocess.run(invoke_args)

        # Cannot work in subfolder directly, so move the resulting files afterwards.
        shutil.move(baseName, "build-tests")
        shutil.move(ilName, "build-tests")
        shutil.move(sbyName, "build-tests")

        runResult.check_returncode()
