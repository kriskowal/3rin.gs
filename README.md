
This is an online map of Middle Earth.  The front-end is entirely static on
[http://3rin.gs/](3rin.gs) posted from the www/ directory.  Most of the  static
content is generated from spreadsheets, hand drawn graphics, SVG layouts, and
assembled and processed with a variety of tools.

Setup
-----

It is dangerous to go alone.  Take these!

 * Python Imaging Library (PIL)
 * Numeric Python
 * Inkscape
 * Gimp
 * Python JSON library (json, simplejson, or the one in django will do)

    apt-get install inkscape gimp python-imaging python-numpy

The large graphical content is not in the git repository.  These can be
downloaded from http://3rin.gs.

    make archive/components

[http://3rin.gs/components.zip]() contains all of the manually
constructed bitmap components for the geography and label layers.

    make archive/sources

[http://3rin.gs/sources.zip]() contains all of the original scanes
from which the components were manually constructed.  these graphics
are not necessary for generating the site.  they exist if any of the
components need to be reconstructed from source material, or for new
projects.

