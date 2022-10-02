### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

### test deps ###
from amaranth.sim import Simulator, Delay, Settle


class Demux(Elaboratable):
    def __init__(self, channelCount: int):
        if channelCount < 2:
            raise ValueError("Demux MUST have at least two channel")
        self.channelCount = channelCount
        self.input = Signal(range(0, channelCount))
        self.output = Signal(channelCount, reset=1)
        self.outOfRange = Signal()

    def ports(self) -> List[Signal]:
        return [self.input, self.output, self.outOfRange]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        previousInput = Signal(self.input.shape())
        with m.If(previousInput != self.input):
            m.d.sync += previousInput.eq(self.input)
            for i in range(0, self.channelCount):
                m.d.sync += self.output[i].eq(Mux(self.input == i, 1, 0))
            m.d.sync += self.outOfRange.eq(Mux(self.input < self.channelCount, 0, 1))

        return m
