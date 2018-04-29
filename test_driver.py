#!/usr/bin/python3

"""Test Driver for Animator"""

from pathlib import Path
import numpy as np
from ash3d_animator import Animator, BasemapSettings

class AshData(object):
    """Test AshData object"""
    def __init__(self):
        self.data = {"foo": []}
        for dummy in range(10):
            self.data["foo"].append(np.random.random_integers(1, 100, (10, 10)))
        self.lats, self.lons = np.meshgrid(
            np.linspace(-45, 45, 10),
            np.linspace(-90, 90, 10)
        )
        self.length = len(self.data["foo"])

    def get_data(self, variable, index):
        """Test get_data method"""
        return self.data[variable][index]


class Tester(object):
    """Test driver class for Animator"""
    def __init__(self):
        self.data = AshData()
        self.variable = "foo"
        self.settings = BasemapSettings(
            colors=["#000066", "#0000CC", "#6666FF", "#9999FF", "#CCCCFF"],
            dpi=200,
            duration=500,
            levels=[0, 20, 40, 60, 80, 100],
            linewidth=0.75,
            loop=True,
            projection="cyl",
            resolution="l"
        )
        self.filename = Path("/home/puskarm/Ash3D/afoo.gif")

    def run(self):
        """Run the tester"""
        anim = Animator(self.data, self.variable, self.settings, self.filename)
        anim.start()
        anim.join()


def test():
    """Test program"""
    tester = Tester()
    tester.run()

if __name__ == "__main__":
    test()
