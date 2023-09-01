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

### local deps
from .Logger import *


class Story:
    def __init__(self, title, content):
        self.title = title
        self.content = content


class TestBench(Elaboratable):
    __test__ = False  # so that pytest does NOT try to collect it

    def __init__(self):
        self._ports = []
        self._loggers = {}

    def ports(self) -> List[Signal]:
        return self._ports

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        for l in self._loggers:
            m.submodules[f"{l}_log"] = self._loggers[l]
        return m

    def registerPort(self, signal):
        if signal.name == "$signal":
            signal.name = f"test_bench_{len(self._ports)}"
            print(f"register signal name : {signal.name}")
        self._ports.append(signal)
        return signal

    def givenStoryBook(self, *, participants, stories):
        self._stories = {story.title: story for story in stories}
        maxSize = max(
            [max([len(story.content[p]) for p in story.content]) for story in stories]
        )
        if maxSize == 0:
            raise ValueError("Stories have no length")
        self._loggers = {p: Logger(participants[p], maxSize - 1) for p in participants}

    def matchesStory(self, storyName):
        if storyName not in self._stories:
            raise KeyError(f"Story '{storyName}' not found.")
        print(f"Building story matcher for '{storyName}'...")
        story = self._stories[storyName]
        partials = []
        for p in story.content:
            print(f"* Processing '{p}' : {story.content[p]} ...")
            log = self._loggers[p]
            history = list(
                reversed(story.content[p])
            )  # because logs are sorted from the latest to the oldest
            print(f"* history = {history} ...")
            partials += [
                log.logs[i] == history[i] for i in range(0, len(story.content[p]))
            ]
        result = partials[0]
        for i in range(1, len(partials)):
            result = result & partials[i]
        return result
