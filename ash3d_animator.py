"""PIL-based animated GIF generator for Ash3D contour maps"""

from collections import namedtuple
from io import BytesIO
from multiprocessing import Process
from PIL import Image

#pylint: disable=wrong-import-position
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
#pylint: enable=wrong-import-position

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
        self._frames = []

    def run(self):
        """Executed by calling start() on process"""
        fig, size, bmap = self._init_basemap()
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
            fig.savefig(buf, dpi=self.settings.dpi, format="RGBA")
            image = Image.frombytes("RGBA", size, buf.getvalue())
            self._frames.append(image)
            for cs_item in contour.collections:
                cs_item.remove()
            buf.close()
        self._save()

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

    def _save(self):
        """Generate the animated GIF"""
        kwargs = {
            "append_images": self._frames[1:],
            "duration": self.settings.duration,
            "save_all": True
        }
        if self.settings.loop:
            kwargs["loop"] = 0
        self._frames[0].save(self.filename, **kwargs)
