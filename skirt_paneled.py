import json
from pathlib import Path
from datetime import datetime

# Custom
import pypattern as pyp
from customconfig import Properties

class SkirtPanel(pyp.Panel):
    """One panel for a panel skirt"""

    def __init__(self, name) -> None:
        super().__init__(name)

        # define edge loop
        self.edges = [pyp.LogicalEdge((0,0), (20, 70))]   # TODO SequentialObject?
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, (55, 70)))
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, (75, 0)))
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, self.edges[0].start))

        # define interface
        self.interfaces.append(pyp.InterfaceInstance(self, 0))
        self.interfaces.append(pyp.InterfaceInstance(self, 1))
        self.interfaces.append(pyp.InterfaceInstance(self, 2))

        # DRAFT
        # self.interfaces.append(pyp.ConnectorEdge(self.edges[0], self.edges[0]))
        # self.interfaces.append(pyp.ConnectorEdge(self.edges[2], self.edges[2]))

class Skirt2(pyp.Component):
    """Simple 2 panel skirt"""
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

        self.front = SkirtPanel('front')
        self.front.translate([-40, -75, 20])
        self.front.swap_right_wrong()

        self.back = SkirtPanel('back')
        self.back.translate([-40, -75, -15])

        self.stitching_rules = [
            (self.front.interfaces[0], self.back.interfaces[0]),
            (self.front.interfaces[2], self.back.interfaces[2])
        ]

        # TODO use dict for interface references?
        # Reusing interfaces of sub-panels as interfaces of this component
        self.interfaces = [
            self.front.interfaces[1],
            self.back.interfaces[1]
        ]  


# With waistband
class WBPanel(pyp.Panel):
    """One panel for a panel skirt"""

    def __init__(self, name) -> None:
        super().__init__(name)

        # define edge loop
        self.edges = [pyp.LogicalEdge((0,0), (0, 10))]   # TODO SequentialObject?
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, (35, 10)))
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, (35, 0)))
        self.edges.append(pyp.LogicalEdge(self.edges[-1].end, self.edges[0].start))

        # define interface
        self.interfaces.append(pyp.InterfaceInstance(self, 0))
        self.interfaces.append(pyp.InterfaceInstance(self, 1))
        self.interfaces.append(pyp.InterfaceInstance(self, 2))
        self.interfaces.append(pyp.InterfaceInstance(self, 3))


class WB(pyp.Component):
    """Simple 2 panel waistband"""
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

        self.front = WBPanel('wb_front')
        self.front.translate([-20, -2, 20])
        self.front.swap_right_wrong()
        self.back = WBPanel('wb_back')
        self.back.translate([-20, -2, -15])

        self.stitching_rules = [
            (self.front.interfaces[0], self.back.interfaces[0]),
            (self.front.interfaces[2], self.back.interfaces[2])
        ]

        self.interfaces = [
            self.front.interfaces[3],
            self.back.interfaces[3]
        ]


class SkirtWB(pyp.Component):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

        self.wb = WB()
        self.skirt = Skirt2()

        self.stitching_rules = [
            (self.wb.interfaces[0], self.skirt.interfaces[0]),
            (self.wb.interfaces[1], self.skirt.interfaces[1])
        ]


if __name__ == '__main__':

    test_garments = [
        SkirtWB(),
        # WB(),
        # Skirt2()
    ]

    test_garments[0].translate([2, 0, 0])

    for piece in test_garments:
        pattern = piece()

        # DEBUG 
        # print(json.dumps(pattern, indent=2, sort_keys=True))

        # Save as json file
        sys_props = Properties('./system.json')
        filename = pattern.serialize(
            Path(sys_props['output']), 
            tag=datetime.now().strftime("%y%m%d-%H-%M-%S"), 
            to_subfolder=False)

        print(f'Success! {piece.name} saved to {filename}')