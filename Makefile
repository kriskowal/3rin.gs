
# deployment cpio archive
build/deploy.cpio: build/data.json build/labels build/regions .PHONEY
	(cd www; find . | cpio -o) > build/deploy.cpio
	(cd build; find data.json labels regions | cpio -o) >> build/deploy.cpio

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

# prepare a cross reference of regional data and label data
# for local debugging
index.html: regions.svg labels.csv
	python index.py

build/labels: labels.py locations.csv labels/*-normalized.png 
	python labels.py

build/ennorath-geography-translucent-32768: .PHONEY
	mkdir -p build/ennorath-geography-translucent-32768
	bash tiles_c2a.bash build/ennorath-geography-export-32768/t build/ennorath-geography-translucent-32768/t

build/ennorath-geography-export-32768: \
		build/ennorath-geography-export-16384.png \
		build/ennorath-geography-export-16384-0.png \
		build/ennorath-geography-export-16384-1.png \
		build/ennorath-geography-export-16384-2.png \
		build/ennorath-geography-export-16384-3.png
	mkdir -p build/ennorath-geography-export-32768
	inkscape -e build/ennorath-geography-export-32768/t.png -w 256 -h 256 geography.svg
	python tiles.py build/ennorath-geography-export-16384-0.png build/ennorath-geography-export-32768/t0
	python tiles.py build/ennorath-geography-export-16384-1.png build/ennorath-geography-export-32768/t1
	python tiles.py build/ennorath-geography-export-16384-2.png build/ennorath-geography-export-32768/t2
	python tiles.py build/ennorath-geography-export-16384-3.png build/ennorath-geography-export-32768/t3

build/ennorath-geography-export-%.png: geography.svg
	inkscape -e $@ -w $* -h $* geography.svg
build/ennorath-geography-export-16384-0.png: geography.svg
	inkscape -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 geography.svg
build/ennorath-geography-export-16384-1.png: geography.svg
	inkscape -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 geography.svg
build/ennorath-geography-export-16384-2.png: geography.svg
	inkscape -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 geography.svg
build/ennorath-geography-export-16384-3.png: geography.svg
	inkscape -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 geography.svg

build/ennorath-geography-translucent-%.png: build/ennorath-geography-export-%.png
	@echo $@
	@echo this is presently a manual step in The GIMP
	@echo use the Color to Alpha tool to remove the white background color
	@exit -1

build/ennorath-labels-%-export-32768: \
		build/ennorath-labels-%-export-16384.png \
		build/ennorath-labels-%-export-16384-0.png \
		build/ennorath-labels-%-export-16384-1.png \
		build/ennorath-labels-%-export-16384-2.png \
		build/ennorath-labels-%-export-16384-3.png
	mkdir -p build/ennorath-labels-%-export-32768
	inkscape -e build/ennorath-labels-%-export-32768/t.png -w 256 -h 256 -i layer% -j labels.svg
	python tiles.py build/ennorath-labels-%-export-16384-0.png build/ennorath-labels-%-export-32768/t0
	python tiles.py build/ennorath-labels-%-export-16384-1.png build/ennorath-labels-%-export-32768/t1
	python tiles.py build/ennorath-labels-%-export-16384-2.png build/ennorath-labels-%-export-32768/t2
	python tiles.py build/ennorath-labels-%-export-16384-3.png build/ennorath-labels-%-export-32768/t3

build/ennorath-labels-%-16000-export.png: labels.svg
	@echo $@
	@echo this is presently a manual step in Inkscape
	@echo export the full page of ennorath.svg with only layer %
	@exit -1

build/ennorath-labels-%-16000.png: build/ennorath-labels-%-16000-export.png 
	python darken.py $< .5 $@

labels-%-export: build/ennorath-labels-%-16000-export.png
	mkdir -p build/labels-export/$*
	python tiles.py $< build/labels-export/$*-

labels-%-dark: .PHONEY
	mkdir -p build/labels-dark
	python tiles_darken.py build/labels-export/$* build/labels-dark/$* .5

labels-%-fade:
	mkdir -p build/labels-fade
	python tiles_fade.py build/labels-dark/$* build/labels-fade/$*

build/tiles: build/ennorath-labels-16000.png build/ennorath-geography-16000.png
	python tiles.py

build/regions: regions_thumbnails.py regions.svg
	# build/ennorath-labels-16000.png build/ennorath-geography-16000.png
	python regions_thumbnails.py

build/data.json: regions.svg
	python data.py

regions.csv: regions.svg
	python regions.py

.PHONEY:

