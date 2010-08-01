
# download archived images to set up
archive:
	mkdir archive
archive/components.zip: archive
	(cd archive; curl -O http://3rin.gs/components.zip)
archive/components: archive/components.zip
	(cd archive; unzip components.zip)
archive/sources.zip: archive
	(cd archive; curl -O http://3rin.gs/sources.zip)
archive/sources: archive/sources.zip
	(cd archive; unzip sources.zip)

# prepare archived images for upload
build/components.zip: .PHONEY
	cat components.manifest | (cd archive; find `cat` | xargs zip build/components.zip)
build/sources.zip: .PHONEY
	(cd archive; find sources | xargs zip build/sources.zip)

build/deploy.cpio: build/data.json build/labels build/regions .PHONEY
	(cd www; find . | cpio -o) > build/deploy.cpio
	(cd build; find data.json labels regions | cpio -o) >> build/deploy.cpio

# prepare a cross reference of regional data and label data
# for local debugging
index.html: regions.svg labels.csv
	python index.py

build/labels: labels.py locations.csv labels/*-normalized.png 
	python labels.py

build/ennorath-geography-16000-export.png: geography.svg
	echo this is presently a manual step in Inkscape
	echo export the full page of ennorath.svg with no visible reference layers
	echo at 16000x16000px
	exit -1

build/ennorath-labels-16000-export: labels.svg
	echo this is presently a manual step in Inkscape
	echo export the full page of ennorath.svg with no visible reference layers
	exit -1

build/ennorath-geography-16000-translucent.png: build/ennorath-geography-16000-export.png
	echo this is presently a manual step in The GIMP
	echo use the Color to Alpha tool to remove the white background color
	exit -1

build/ennorath-geography-16000.png: build/ennorath-geography-16000-translucent.png
	echo this is presently a manual step in The GIMP
	echo use the HSL tool to drop the lightness by -100
	exit -1
	# this could be automated with PIL now

build/ennorath-labels-16000.png: build/ennorath-labels-16000-export.png
	echo this is presently a manual step in The GIMP
	echo use the HSL tool to drop the lightness by -100
	exit -1
	# this could be automated with PIL now

build/tiles: build/ennorath-labels-16000.png build/ennorath-geography-16000.png
	python tiles.py

build/regions: regions.svg build/ennorath-labels-16000.png build/ennorath-geography-16000.png
	python regions-thumbnails.py

build/regions.json: regions.svg
	python regions-json.py

regions.csv: regions.svg
	python regions.py

build/ennorath-labels-8000.png: build/ennorath-labels-16000.png
	python samples.py
build/ennorath-labels-4000.png: build/ennorath-labels-16000.png
	python samples.py
build/ennorath-labels-2000.png: build/ennorath-labels-16000.png
	python samples.py
build/ennorath-labels-1000.png: build/ennorath-labels-16000.png
	python samples.py
build/ennorath-geography-8000.png: build/ennorath-geography-16000.png
	python samples.py
build/ennorath-geography-4000.png: build/ennorath-geography-16000.png
	python samples.py
build/ennorath-geography-2000.png: build/ennorath-geography-16000.png
	python samples.py
build/ennorath-geography-1000.png: build/ennorath-geography-16000.png
	python samples.py

.PHONEY:

