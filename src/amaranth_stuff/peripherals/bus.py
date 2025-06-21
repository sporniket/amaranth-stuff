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
from amaranth.build import Platform
from amaranth.lib.wiring import In, Out, Signature


class SignatureOfSimpleDataBus(Signature):
    """A simple model for a system bus
    ```
    ## Signature

    _**Given** `widthD` is the data width_

    _**Given** `widthA` is the address width_

    |Member|Definition|Description|
    |---|---|---|
    |`toCentral`|In(widthD)|Data sent by a peripheral to the CPU|
    |`toPeripheral`|Out(widthD)|Data sent by the CPU to a peripheral|
    |`dataStrobe`|Out(1)|Cpu signal to notify a peripheral that data is ready (write cycle) or has been received|
    |`address`|Out(widthA)|The address targeted by the CPU|
    |`write`|Out(1)|Cpu assert this signal when initiating a write cycle|


    ## Protocol

    * **First step** : _at the time of asserting `dataStrobe`_, the CPU has set up `write`, `address`, and if `write` is asserted it has set up `toPeripheral` too
    * **Second step** : _if `write` was not asserted at the time of latching `dataStrobe`_ the peripheral sets up `toCentral`

    ### Timings

    > In these timing diagrams, a signal being undefined at one point in time means that its value has no effect on the exchange at that point.

    #### Read cycle
    ![read-cycle](https://github.com/sporniket/amaranth-stuff/assets/5870528/440726b7-e7e0-4f55-80c8-8ac11d60efba)

    ```json
    {
        "signal":[
            [
                "Central",
                [
                    "Control",
                    {
                        "name":"write",
                        "wave":"x0.."
                    },
                    {
                        "name":"dataStrobe",
                        "wave":"010."
                    }
                ],
                {
                    "name":"address",
                    "wave":"x2x.",
                    "data":[
                        "addr"
                    ]
                },
                {
                    "name":"toPeripheral",
                    "wave":"x..."
                }
            ],
            [
                "P.",
                {
                    "name":"toCentral",
                    "wave":"x.2x",
                    "data":[
                        "data"
                    ]
                }
            ]
        ],
        "head":{
            "text":"Read cycle"
        }
    }
    ```

    #### Write cycle

    ![write_cycle](https://github.com/sporniket/amaranth-stuff/assets/5870528/ccfc3edb-30a0-4c95-9dd4-00f060f9863b)

    ```json
    {
        "signal":[
            [
                "Central",
                [
                    "Control",
                    {
                        "name":"write",
                        "wave":"x1x"
                    },
                    {
                        "name":"dataStrobe",
                        "wave":"010"
                    }
                ],
                {
                    "name":"address",
                    "wave":"x2x",
                    "data":[
                        "addr"
                    ]
                },
                {
                    "name":"toPeripheral",
                    "wave":"x2x",
                    "data":[
                        "data"
                    ]
                }
            ],
            [
                "P.",
                {
                    "name":"toCentral",
                    "wave":"x.."
                }
            ]
        ],
        "head":{
            "text":"Write cycle"
        }
    }
    ```
    ```
    """

    def __init__(self, widthOfData: int, widthOfAddress: int):
        self.widthOfData = 1 if widthOfData < 1 else widthOfData
        self.widthOfAddress = 1 if widthOfAddress < 1 else widthOfAddress
        super().__init__(
            {
                "toCentral": In(self.widthOfData),
                "toPeripheral": Out(self.widthOfData),
                "address": Out(self.widthOfAddress),
                "dataStrobe": Out(1, init=0),
                "write": Out(1, init=0),
            }
        )
