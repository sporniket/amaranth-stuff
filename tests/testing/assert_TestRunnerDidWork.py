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

import inspect
import os


def _thenFormalVerificationDidHappenSuccessfully(path):
    assert os.path.exists(path)
    assert os.path.isdir(path)
    assert os.path.exists(os.path.join(path, "PASS"))


def _thenFormalVerificationDidHappenWithFailure(path):
    assert os.path.exists(path)
    assert os.path.isdir(path)
    assert os.path.exists(os.path.join(path, "FAIL"))


def thenTestRunnerDidWorkedAsExpectedWithSuccess(storyName: str):
    frameDescription = inspect.getouterframes(inspect.currentframe())[1][3]
    _thenFormalVerificationDidHappenWithFailure(
        os.path.join(
            "build-tests",
            f"{frameDescription}__{storyName}__reachability",
        )
    )
    _thenFormalVerificationDidHappenSuccessfully(
        os.path.join(
            "build-tests",
            f"{frameDescription}__{storyName}__behaviour",
        )
    )


def thenTestRunnerDidWorkedAsExpectedWithFailure(storyName: str):
    frameDescription = inspect.getouterframes(inspect.currentframe())[1][3]
    _thenFormalVerificationDidHappenWithFailure(
        os.path.join(
            "build-tests",
            f"{frameDescription}__{storyName}__reachability",
        )
    )
    _thenFormalVerificationDidHappenWithFailure(
        os.path.join(
            "build-tests",
            f"{frameDescription}__{storyName}__behaviour",
        )
    )
