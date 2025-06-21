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

from testing_for_amaranth.SymbiYosysHelper import SymbiYosysHelper

from .assert_utils import thenIsExistingFile, thenSbyScriptContainsExpectedContent


def test_getSbyFileName_returns_expected_file_name():
    assert SymbiYosysHelper("whatever").getSbyFileName() == os.path.join(
        ".", "whatever.sby"
    )
    assert SymbiYosysHelper(
        "whatever", workingDir="foo"
    ).getSbyFileName() == os.path.join("foo", "whatever.sby")


def test_generateScriptContentToReadRtlil_returns_expected_content_when_using_default_depth():
    assert (
        SymbiYosysHelper("whatever").generateScriptContentToReadRtlil()
        == """[options]
mode bmc
depth 20

[engines]
smtbmc

[script]
read_rtlil whatever.il
prep -top top

[files]
whatever.il"""
    )


def test_generateScriptContentToReadRtlil_does_not_use_working_directory():
    assert (
        SymbiYosysHelper("whatever").generateScriptContentToReadRtlil()
        == SymbiYosysHelper(
            "whatever", workingDir="foo"
        ).generateScriptContentToReadRtlil()
    )


def test_generateScriptContentToReadRtlil_uses_default_depth_when_given_depth_too_shallow():
    assert (
        SymbiYosysHelper("whatever", depth=19).generateScriptContentToReadRtlil()
        == """[options]
mode bmc
depth 20

[engines]
smtbmc

[script]
read_rtlil whatever.il
prep -top top

[files]
whatever.il"""
    )


def test_generateScriptContentToReadRtlil_uses_given_depth_when_high_enough():
    assert (
        SymbiYosysHelper("whatever", depth=21).generateScriptContentToReadRtlil()
        == """[options]
mode bmc
depth 21

[engines]
smtbmc

[script]
read_rtlil whatever.il
prep -top top

[files]
whatever.il"""
    )


def test_writeScriptToReadRtlil_write_expected_script_into_expected_file(tmp_path):
    wd = str(tmp_path)
    ut = SymbiYosysHelper("whatever", workingDir=wd)
    ut.writeScriptToReadRtlil()

    thenIsExistingFile(os.path.join(wd, "whatever.sby"))
    thenSbyScriptContainsExpectedContent(os.path.join(wd, "whatever"))
