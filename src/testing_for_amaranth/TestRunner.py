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
from amaranth.hdl import ClockDomain, Elaboratable, Fragment, Module, Signal
from amaranth.build import Platform

### amaranth -- testing
from amaranth.back import rtlil  # , cxxrtl, verilog
from amaranth._toolchain import require_tool  # May need to be re-implemented locally

### internal
from .TestBench import TestBench


IGNORED_FRAME_NAMES = ["run", "_runBehaviourTest", "_runReachabilityTest"]


class TestRunner:
    __test__ = False  # so that pytest does NOT try to collect it

    """A system to generate test benches to be formally verified by SymbiYosis (sby)"""

    def __init__(self, deviceFactory, castingFactory, story):
        if len(story.expected) == 0:
            raise ValueError(f"story.must.have.expected.participants")
        self._deviceFactory = deviceFactory
        self._castingFactory = castingFactory
        self._story = story

    def _runBehaviourTest(self):
        def testBody(m: Module, cd: ClockDomain):
            dut = m.submodules.dut
            tb = m.submodules.testBench
            tb.givenStoryBook(
                participants=self._castingFactory(dut, cd),
                stories=[self._story],
            )
            with m.If(tb.matchesStory(self._story.title)):
                for p in self._story.expected:
                    m.d.sync += tb.verifyLogsAndNow(p, self._story.content[p])

        TestRunner.perform(
            self._deviceFactory(),
            testBody,
            description=f"{self._story.title}__behaviour",
        )

    def _runReachabilityTest(self):
        def testBody(m: Module, cd: ClockDomain):
            dut = m.submodules.dut
            tb = m.submodules.testBench
            tb.givenStoryBook(
                participants=self._castingFactory(dut, cd),
                stories=[self._story],
            )
            with m.If(tb.matchesStory(self._story.title)):
                for p in self._story.expected:
                    m.d.sync += tb.fail(p)

        TestRunner.perform(
            self._deviceFactory(),
            testBody,
            description=f"{self._story.title}__reachability",
            expectFailure=True,
        )

    def run(self):
        self._runReachabilityTest()
        self._runBehaviourTest()

    @staticmethod
    def _generateTestBench(ilName: str, dut: Elaboratable, test, platform: Platform):
        ###
        # Keep references to the clock domain and the reset signal
        # to add them to the ports
        # otherwise the verification always pass !!
        sync = ClockDomain("sync")
        rst = Signal(init=1)
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
                        f"read_rtlil {ilName}",
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
        expectFailure: bool = False,
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
        for fs in callFrameStack[1:]:
            frameDescription = fs[3]
            if frameDescription not in IGNORED_FRAME_NAMES:
                break
        if frameDescription == "__main__":
            frameDescription = test.__name__
        baseName = (
            frameDescription
            if description is None
            else f"{frameDescription}__{TestRunner._asSafeName(description)}"
        )
        print(f"##########>")
        print(f"##########> {baseName}")
        print(f"##########>")
        ilName = f"{baseName}.il"
        sbyName = f"{baseName}.sby"

        print(f"Generating {ilName}...")
        requiredDepth = TestRunner._generateTestBench(ilName, dut, test, platform)
        print(f"Generating {sbyName}...")
        TestRunner._generateSbyConfig(sbyName, ilName, max([depth, requiredDepth]))

        invoke_args = [require_tool("sby"), "-f", sbyName]
        print(f"Running {' '.join(invoke_args)}...")
        runResult = subprocess.run(invoke_args)

        # Cannot work in subfolder directly, so move the resulting files afterwards.
        shutil.move(baseName, "build-tests")
        shutil.move(ilName, "build-tests")
        shutil.move(sbyName, "build-tests")

        if expectFailure:
            if runResult.returncode == 0:
                raise subprocess.CalledProcessError(
                    runResult.returncode,
                    runResult.cmd,
                    runResult.stdout,
                    runResult.stderr,
                )
        else:
            runResult.check_returncode()
