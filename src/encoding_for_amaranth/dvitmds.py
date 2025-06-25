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
from amaranth.hdl import Cat, Elaboratable, Module, Mux, Signal, signed
from amaranth.build import Platform


class DviTmdsEncoder(Elaboratable):
    """An implementation of the TMDS encoding for DVI.
    ```
    See https://www.fpga4fun.com/HDMI.html and https://mjseemjdo.com/2021/04/02/tutorial-6-hdmi-display-output/

    ## Typical application

    ```python
    vde, hsync, vsync = (...) # 3 Signal() coming from a video arbiter
    red, green, blue = (...) # 3 Signal(8) coming from video RAM fifo

    # given pixelClock being a clock domain to fetch pixel data from (red,green,blue).
    blueTmds, greenTmds, redTmds = (
        DviTmdsEncoder(blue,vde,hsync,vsync),
        DviTmdsEncoder(green,vde,0,0),
        DviTmdsEncoder(red,vde,0,0),
    )

    # given dviLinkClock being a clock domain to send bits through the DVI link.
    channel0,channel1,channel2 = (
        ShiftRegisterTx(blueTmds.ports[-1]),
        ShiftRegisterTx(greenTmds.ports[-1]),
        ShiftRegisterTx(redTmds.ports[-1]),
    )
    ```

    ## Balance counter simplification

    The specification formula results in that the balance counter is always even :

    * For any given set of 8 bits, the number of zeros N0 = 8 - N1 ⇒ the difference N1-N0 = N1 - (8 - N1) = 2×N1 - 8 = 2×(N1 - 4)
      is an even number. Hence N1 > N0 ⇔ N1 - N0 > 0 ⇔ N1 - 4 > 0
    * When the balance counter is 0 (initial value), then the new balance counter is ±(N1-N0) = ±2×(N1 - 4), an even number
    * When the balance counter is a non-zero even number 2×K, then the new balance is 2×K±(2×(N1 - 4) - 2×(1 or 0))
      = 2×(K ±(N1 - 4 - (1 or 0), an even number.

    Thus one can compute the half balance counter, by computing (N1 - 4), looking at the sign bit as well as the sign bit of
    the counter when it is not 0 to decide the case.
    ```
    """

    def __init__(self, dataIn: Signal, vde: Signal, ctl0: Signal, ctl1: Signal):
        if len(dataIn) != 8 or dataIn.shape().signed == True:
            raise ValueError(
                f"dataIn(signed = {dataIn.shape().signed}, width = {len(dataIn)}) MUST be unsigned, 8-bits width."
            )
        if len(vde) != 1:
            raise ValueError(f"vde MUST have a width of 1 instead of {len(vde)}")
        if len(ctl0) != 1:
            raise ValueError(f"ctl0 MUST have a width of 1 instead of {len(ctl0)}")
        if len(ctl1) != 1:
            raise ValueError(f"ctl1 MUST have a width of 1 instead of {len(ctl1)}")

        self.dataIn = dataIn
        # when reset, vde is negated, as well as ctl[0:1], thus dataOut should be 0b0010101011.
        self.dataOut = Signal(10, init=0b0010101011)
        self.videoDisplayEnable = vde
        self.ctl0 = ctl0
        self.ctl1 = ctl1
        self.halfBalanceCounter = Signal(signed(4))

    def ports(self) -> list[Signal]:
        return [
            self.dataIn,
            self.videoDisplayEnable,
            self.ctl0,
            self.ctl1,
            self.dataOut,
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        # BEGIN all combinatorial part : prepare tmds encoded data for next clock

        din = self.dataIn
        dinCountOfOnes = Signal(3)
        m.d.comb += dinCountOfOnes.eq(
            ((din[0] + din[1]) + (din[2] + din[3]))
            + ((din[4] + din[5]) + (din[6] + din[7]))[0:3]
        )

        dmz = Signal(9)  # Data (transition) MinimeZed
        with m.If((dinCountOfOnes > 4) | ((dinCountOfOnes == 4) & (din[0] == 0))):
            # use XNOR
            m.d.comb += [dmz[8].eq(0), dmz[0].eq(din[0])] + [
                dmz[i].eq(~(dmz[i - 1] ^ din[i])) for i in range(1, 8)
            ]
        with m.Else():
            # use XOR
            m.d.comb += [dmz[8].eq(1), dmz[0].eq(din[0])] + [
                dmz[i].eq(dmz[i - 1] ^ din[i]) for i in range(1, 8)
            ]

        dmzBalance = Signal(signed(4))
        m.d.comb += dmzBalance.eq(
            (
                (
                    ((dmz[0] + dmz[1]) + (dmz[2] + dmz[3]))
                    + ((dmz[4] + dmz[5]) + (dmz[6] + dmz[7]))
                )
                - 4
            )[0:4]
        )

        statusQuo = Signal()
        m.d.comb += statusQuo.eq((self.halfBalanceCounter == 0) | (dmzBalance == 0))

        out = Signal(10)
        halfBalanceCounterNew = Signal.like(self.halfBalanceCounter)

        with m.If(statusQuo):
            with m.If(dmz[8]):
                # source bits were XOR-ed, keep result as is
                m.d.comb += [
                    out.eq(Cat(dmz, 0)),
                    halfBalanceCounterNew.eq(
                        (self.halfBalanceCounter + dmzBalance)[0:4]
                    ),
                ]
            with m.Else():
                # source bits were XNOR-ed, inverse the result
                m.d.comb += [
                    out.eq(Cat(~dmz[0:8], dmz[8], 1)),
                    halfBalanceCounterNew.eq(
                        (self.halfBalanceCounter - dmzBalance)[0:4]
                    ),
                ]
        with m.Else():
            greaterImbalance = Signal()
            m.d.comb += greaterImbalance.eq(self.halfBalanceCounter[3] == dmzBalance[3])

            with m.If(greaterImbalance):
                # inverse data bits
                m.d.comb += [
                    out.eq(Cat(~dmz[0:8], dmz[8], 1)),
                    halfBalanceCounterNew.eq(
                        (self.halfBalanceCounter + dmz[8] - dmzBalance)[0:4]
                    ),
                ]
            with m.Else():
                # keep data bits as is
                m.d.comb += [
                    out.eq(Cat(dmz, 0)),
                    halfBalanceCounterNew.eq(
                        (self.halfBalanceCounter - (~dmz[8]) + dmzBalance)[0:4]
                    ),
                ]

        # BEGIN synchronized part
        with m.If(self.videoDisplayEnable):
            # send out tmds encoded data, update balance counter
            m.d.sync += [
                self.halfBalanceCounter.eq(halfBalanceCounterNew),
                self.dataOut.eq(out),
            ]
        with m.Else():
            # send out control data, reset balance counter
            m.d.sync += [
                self.halfBalanceCounter.eq(0),
                self.dataOut.eq(
                    Mux(
                        self.ctl0,
                        Mux(self.ctl1, 0b1101010101, 0b0010101010),  # 11  # 10
                        Mux(self.ctl1, 0b1101010100, 0b0010101011),  # 01  # 00
                    )
                ),
            ]

        return m
