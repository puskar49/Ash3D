"""PIL-based animated GIF generator for Ash3D contour maps"""

from collections import namedtuple
from io import BytesIO
from multiprocessing import Process
from PIL import Image

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

BasemapSettings = namedtuple(
    "BasemapSettings",
    ["colors", "dpi", "duration", "levels", "linewidth", "loop", "projection", "resolution"]
)

class Animator(Process):
    """
    Primary object for generating animated GIFs from NetCDF data.
    Expects a formatted AshData object, the desired variable,
    and the associated MATPLOTLIB parameters.
    """
    def __init__(self, data, variable, basemap_settings, filename):
        super().__init__()
        self.data = data
        self.variable = variable
        self.settings = basemap_settings
        self.filename = filename
        self.lon_bounds = (self.data.lons.min(), self.data.lons.max())
        self.lat_bounds = (self.data.lats.min(), self.data.lats.max())

    def run(self):
        """Executed by calling start() on process"""
        fig, size, bmap = self._init_basemap()
        gif = GIFGenerator(size, self.settings.duration, self.settings.loop)
        for index in range(self.data.length):
            buf = BytesIO()
            plt.title("Frame {}".format(index))
            contour = bmap.contourf(
                self.data.lons,
                self.data.lats,
                self.data.get_data(self.variable, index),
                levels=self.settings.levels,
                colors=self.settings.colors
            )
            fig.savefig(buf, dpi=self.settings.dpi, format="rgba")
            gif.add(buf)
            for cs_item in contour.collections:
                cs_item.remove()
            buf.close()
        gif.save(self.filename)

    def _init_basemap(self):
        """Generate a figure, size, and basemap"""
        fig = plt.figure()
        width, height = [int(x) for x in fig.get_size_inches() * self.settings.dpi]
        bmap = Basemap(
            projection=self.settings.projection,
            resolution=self.settings.resolution,
            llcrnrlon=self.lon_bounds[0],
            llcrnrlat=self.lat_bounds[0],
            urcrnrlon=self.lon_bounds[1],
            urcrnrlat=self.lat_bounds[1]
        )
        bmap.drawcoastlines(linewidth=self.settings.linewidth)
        bmap.drawcountries(linewidth=self.settings.linewidth)
        # add the meridians and whatnot
        return fig, (int(width), int(height)), bmap


class GIFGenerator(object):
    """Makes animated GIFs from PIL-based image frames"""
    def __init__(self, size, duration, loop):
        self.duration = duration
        self.loop = loop
        self.size = size
        self._frames = []

    def add(self, buf, mode="RGBA"):
        """Get a PIL-image object from IO buffer and add it to the generator"""
        image = Image.frombytes(mode, self.size, buf.getvalue())
        self._frames.append(image)

    def save(self, filename):
        """Generate the animated GIF"""
        kwargs = {
            "append_images": self._frames[1:],
            "duration": self.duration,
            "save_all": True
        }
        if self.loop:
            kwargs["loop"] = 0
        self._frames[0].save(filename, **kwargs)
