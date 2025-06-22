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

### amaranth -- main deps
from amaranth.hdl import Elaboratable, Module, Signal
from amaranth.build import Platform

### amaranth -- test deps
from amaranth.hdl import Assert

### local deps
from .Logger import Logger
from .Story import Story


class TestBench(Elaboratable):
    __test__ = False  # so that pytest does NOT try to collect it

    def __init__(self):
        self._ports = []
        self._loggers = {}
        self.requiredDepth = 0

    def ports(self) -> list[Signal]:
        return self._ports

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        for l in self._loggers:
            m.submodules[f"{l}_log"] = self._loggers[l]
        return m

    def registerPort(self, signal: Signal):
        if signal.name == "$signal":
            signal.name = f"test_bench_{len(self._ports)}"
            print(f"register signal name : {signal.name}")
        self._ports.append(signal)
        return signal

    def givenStoryBook(self, *, participants: dict[str, Signal], stories: list[Story]):
        self._stories = {story.title: story for story in stories}
        maxSize = max(
            [max([len(story.content[p]) for p in story.content]) for story in stories]
        )
        if maxSize == 0:
            raise ValueError("Stories have no length")
        self.requiredDepth = maxSize + 3
        self._loggers = {p: Logger(participants[p], maxSize - 1) for p in participants}

    def matchesStory(self, storyName: str):
        if storyName not in self._stories:
            raise KeyError(f"Story '{storyName}' not found.")
        print(f"Building story matcher for '{storyName}'...")
        story = self._stories[storyName]
        partials = []
        for p in story.given:
            print(f"* Processing '{p}' : {story.content[p]} ...")
            logger = self._loggers[p]
            history = list(
                reversed(story.content[p])
            )  # because logs are sorted from the latest to the oldest
            print(f"* history = {history} ...")
            sizeOfLogs = len(logger.logs)
            sizeOfHistory = len(history)
            sizeOfPartials = sizeOfLogs if sizeOfLogs < sizeOfHistory else sizeOfHistory
            partials += [logger.logs[i] == history[i] for i in range(0, sizeOfPartials)]
        result = partials[0]
        for i in range(1, len(partials)):
            result = result & partials[i]
        return result

    def _buildAssertList(self, logger: Logger, history):
        return [Assert(logger.logs[i] == history[i]) for i in range(0, len(history))]

    def verifyLogs(self, participantName: str, logs: list) -> list:
        """
        ```
        Build a list of statements to verify the content of the named logger.

        ## Args:
        *    `participantName` (str): the participant name, referenced when calling `givenStoryBook(...)`
        *    `logs` (list): the list of values, in chronological order, the last element is compared to `logger.logs[0]`

        ## Raises:
        *    `KeyError`: the participant name is not found.

        ## Returns:
        A list of statement to assert the content of the logger.
        ```
        """
        if participantName not in self._loggers:
            raise KeyError(f"Logger '{participantName}' not found")
        print(f"Verify logs for '{participantName}'...")
        logger = self._loggers[participantName]
        history = list(reversed(logs))  # same as matchesStory
        print(f"* history = {history}")
        return self._buildAssertList(logger, history)

    def verifyLogsAndNow(self, participantName: str, logs: list) -> list:
        """
        ```
        Build a list of statements to verify the content of the named logger.

        ## Args:
        *    `participantName` (str): the participant name, referenced when calling `givenStoryBook(...)`
        *    `logs` (list): the list of values, in chronological order, the last element is compared to `logger.source`, the
             previous element is compared to `logger.logs[0]`.

        ## Raises:
        *    `KeyError`: the participant name is not found.

        ## Returns:
        A list of statement to assert the content of the logger.
        ```
        """
        if participantName not in self._loggers:
            raise KeyError(f"Logger '{participantName}' not found")
        print(f"Verify logs and now for '{participantName}'...")
        logger = self._loggers[participantName]
        history = list(reversed(logs))  # same as matchesStory
        print(f"* history = {history}")
        return [Assert(logger.source == history[0])] + self._buildAssertList(
            logger, history[1:]
        )

    def fail(self, participantName: str) -> list:
        logger = self._loggers[participantName]
        return [Assert(logger.source != logger.source)]
