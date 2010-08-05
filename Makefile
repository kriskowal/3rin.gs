
# organized generally from most to least composite

# deployment cpio archive
build/deploy.cpio: www build/tiles build/labels build/regions build/data.json 
	(cd www; find . | cpio -o) > build/deploy.cpio
	(cd build; find data.json labels tiles regions | cpio -o) >> build/deploy.cpio

www:
	touch $@

build/tiles: \
		build/tiles/g \
		build/tiles/st

# generate resized and thumbnail labels from manually normalized labels
build/labels: labels.py locations.csv labels/*-normalized.png 
	python labels.py

# generate regional thumbnails
build/regions: \
		regions_thumbnails.py \
		regions.svg \
		build/labels-st-16384.png \
		build/geography-16384.png
	python regions_thumbnails.py

build/data.json: regions.svg
	python data.py

# LOCAL

# a cache of the regional information in CSV format
regions.csv: regions.svg
	python regions.py

# prepare a cross reference of regional data and label data
# for local debugging
index.html: regions.svg labels.csv
	python index.py

# ARCHIVES

# download archived images to set up
archive:
	mkdir -p archive
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

# LABELING
# SINDARIN TENGWAR

# used for the regions, so based on the translucently labeled label
# master
build/labels-st-16384.png:

# tiles
# 1.81 HOURS
build/tiles/st: build/labels-st-dark-32768
	mkdir -p build/tiles
	python tiles_labels.py $< $@

# 4.1 HOURS
build/labels-st-dark-32768:
	#build/labels-st-export-32768
	mkdir -p $@
	python tiles_darken.py build/labels-st-export-32768/1- $@/1-.5
	python tiles_darken.py build/labels-st-export-32768/2- $@/2-.5
	python tiles_darken.py build/labels-st-export-32768/3- $@/3-.5
	python tiles_darken.py build/labels-st-export-32768/4- $@/4-.5
	python tiles_darken.py build/labels-st-export-32768/5- $@/5-.5
	python tiles_darken.py build/labels-st-export-32768/6- $@/6-.5
	python tiles_darken.py build/labels-st-export-32768/7- $@/7-.5
	python tiles_darken.py build/labels-st-export-32768/8- $@/8-.5

# the master label level sources
# 4.72 HOURS
build/labels-st-export-32768: \
		build/labels-st-export-32768/1 \
		build/labels-st-export-32768/2 \
		build/labels-st-export-32768/3 \
		build/labels-st-export-32768/4 \
		build/labels-st-export-32768/5 \
		build/labels-st-export-32768/6 \
		build/labels-st-export-32768/7 \
		build/labels-st-export-32768/8

# quadtrees based on the master quads
build/labels-st-export-32768/%: \
		build/labels-st-export-16384/%-0.png \
		build/labels-st-export-16384/%-1.png \
		build/labels-st-export-16384/%-2.png \
		build/labels-st-export-16384/%-3.png
	mkdir -p build/labels-st-export-32768
	inkscape -z -e build/labels-st-export-32768/$*-.png -w 256 -h 256 -i layer$* -j build/labels-st-opaque.svg
	python tiles.py build/labels-st-export-16384/$*-0.png build/labels-st-export-32768/$*-0
	python tiles.py build/labels-st-export-16384/$*-1.png build/labels-st-export-32768/$*-1
	python tiles.py build/labels-st-export-16384/$*-2.png build/labels-st-export-32768/$*-2
	python tiles.py build/labels-st-export-16384/$*-3.png build/labels-st-export-32768/$*-3

# export master quads
build/labels-st-export-16384/%-0.png: build/labels-st-opaque.svg build/labels-st-export-16384
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 -i layer$* -j build/labels-st-opaque.svg
build/labels-st-export-16384/%-1.png: build/labels-st-opaque.svg build/labels-st-export-16384
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 -i layer$* -j build/labels-st-opaque.svg
build/labels-st-export-16384/%-2.png: build/labels-st-opaque.svg build/labels-st-export-16384
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 -i layer$* -j build/labels-st-opaque.svg
build/labels-st-export-16384/%-3.png: build/labels-st-opaque.svg build/labels-st-export-16384
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 -i layer$* -j build/labels-st-opaque.svg
build/labels-st-export-16384:
	mkdir -p $@

# a version of labels-st.svg wherein all of the labels are opaque
build/labels-st-opaque.svg: labels-st.svg labels_opaque.py
	python labels_opaque.py labels-st.svg $@


# GEOGRAPHY

# 40 MINUTES
build/tiles/g: build/geography-translucent-32768
	mkdir -p build/tiles
	python tiles_darken.py build/geography-translucent-32768/t $@ .5

# 1 HOURS
build/geography-translucent-32768:
	mkdir -p $@
	bash tiles_c2a.bash build/geography-export-32768/t build/geography-translucent-32768/t

build/geography-export-32768: \
		build/geography-export-16384.png \
		build/geography-export-16384-0.png \
		build/geography-export-16384-1.png \
		build/geography-export-16384-2.png \
		build/geography-export-16384-3.png
	mkdir -p build/geography-export-32768
	inkscape -z -e build/geography-export-32768/t.png -w 256 -h 256 geography.svg
	python tiles.py build/geography-export-16384-0.png build/geography-export-32768/t0
	python tiles.py build/geography-export-16384-1.png build/geography-export-32768/t1
	python tiles.py build/geography-export-16384-2.png build/geography-export-32768/t2
	python tiles.py build/geography-export-16384-3.png build/geography-export-32768/t3

build/geography-export-%.png: geography.svg
	inkscape -z -e $@ -w $* -h $* geography.svg
build/geography-export-16384-0.png: geography.svg
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 geography.svg
build/geography-export-16384-1.png: geography.svg
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 geography.svg
build/geography-export-16384-2.png: geography.svg
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 geography.svg
build/geography-export-16384-3.png: geography.svg
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 geography.svg

.PHONEY:

