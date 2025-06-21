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

import os


class SymbiYosysHelper:
    def __init__(self, baseName: str, *, workingDir: str = "", depth: int = 20):
        if baseName == None or len(baseName) == 0:
            raise ValueError("must.be.non.empty:baseName")

        self._baseName = baseName.strip()
        if len(self._baseName) == 0:
            raise ValueError("must.be.non.blank:baseName")

        self._workingDir = "."
        if workingDir is not None:
            cleanWorkDir = workingDir.strip()
            if len(cleanWorkDir) > 0:
                self._workingDir = cleanWorkDir

        self._depth = max(depth, 20)

    def generateScriptContentToReadRtlil(self) -> str:
        return f"""[options]
mode bmc
depth {self._depth}

[engines]
smtbmc

[script]
read_rtlil {self._baseName}.il
prep -top top

[files]
{self._baseName}.il"""

    def getSbyFileName(self) -> str:
        return os.path.join(self._workingDir, f"{self._baseName}.sby")

    def writeScriptToReadRtlil(self) -> str:
        with open(self.getSbyFileName(), "wt") as f:
            f.write(self.generateScriptContentToReadRtlil())
