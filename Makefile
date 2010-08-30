
# organized generally from most to least composite

.SECONDARY:
.PRECIOUS:
.PRECIOUSSSSS:

all: \
		build/tiles \
		build/data.json \
		build/map-latin-1024.png \
		build/map-tengwar-1024.png
	# build/regions XXX

dev: \
		build/geography-4096.png \
		build/map-latin-4096.png \
		build/map-tengwar-4096.png \
		build/labels
	# the geography resize is used in labels-tengwar (and probably others soon)
	#  as a reference

# deployment cpio archive
build/deploy.cpio: build/www.cpio build/build.cpio
	cat $< > $@
build/www.cpio: www
	(cd www; find . | cpio -o) > $@
build/build.cpio: build/tiles build/labels build/regions build/data.json build/map-1024.png
	(cd build; find tiles labels regions data.json map-1024.png | cpio -o) > $@
www:
	touch $@

# 3.17 HOURS and
# 11.5 HOURS roughly
build/tiles: build/tiles/g build/tiles/t build/tiles/l

# generate resized and thumbnail labels from manually normalized labels
# 20 MINUTES
build/labels: labels.py locations.csv
	python labels.py

# generate regional thumbnails
build/regions: \
		regions_thumbnails.py \
		regions.svg \
		build/map-tengwar-16384.png
	python regions_thumbnails.py build/map-tengwar-16384.png

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
archives: \
		build/components.zip \
		build/sources.zip
build/components.zip:
	cat components.manifest | (cd archive; find `cat` | xargs zip build/components.zip)
build/sources.zip:
	(cd archive; find sources | xargs zip build/sources.zip)

# REGIONS

build/map-tengwar-16384.png:
	exit -1 # cannot generate 16384 yet.  need to do quadtree reduction
build/map-tengwar-%.png: build/geography-%.png build/labels-tengwar-%.png
	python over.py build/geography-$*.png build/labels-tengwar-$*.png build/map-tengwar-$*.png
build/map-latin-%.png: build/geography-%.png build/labels-latin-%.png
	python over.py build/geography-$*.png build/labels-latin-$*.png build/map-latin-$*.png

build/labels-tengwar-1024.png: build/labels-tengwar-export-1024.png
	python darken.py $< $@ .5
build/labels-tengwar-export-1024.png: labels-tengwar.svg
	inkscape -z -e $@ -w 1024 -h 1024 $<
build/labels-latin-1024.png: build/labels-latin-export-1024.png
	python darken.py $< $@ .5
build/labels-latin-export-1024.png: labels-latin.svg
	inkscape -z -e $@ -w 1024 -h 1024 $<

build/labels-tengwar-4096.png: build/labels-tengwar-export-4096.png
	python darken.py $< $@ .5
build/labels-tengwar-export-4096.png: labels-tengwar.svg
	inkscape -z -e $@ -w 4096 -h 4096 $<
build/labels-latin-4096.png: build/labels-latin-export-4096.png
	python darken.py $< $@ .5
build/labels-latin-export-4096.png: labels-latin.svg
	inkscape -z -e $@ -w 4096 -h 4096 $<

build/labels-tengwar-16384.png: build/labels-tengwar-export-16384.png
	python darken.py $< $@ .5
build/labels-tengwar-export-16384.png: labels-tengwar.svg
	inkscape -z -e $@ -w 16384 -h 16384 $<
build/labels-latin-16384.png: build/labels-latin-export-16384.png
	python darken.py $< $@ .5
build/labels-latin-export-16384.png: labels-latin.svg
	inkscape -z -e $@ -w 16384 -h 16384 $<

build/geography-%.png: build/geography-combined-%.png
	python darken.py $< $@ .5
build/geography-combined-%.png: build/coast-translucent-%.png build/geography-translucent-%.png
	python over.py build/coast-translucent-$*.png build/geography-translucent-$*.png build/geography-combined-$*.png
build/geography-translucent-%.png: build/geography-export-%.png
	(echo $<; echo $@) | bash c2a.bash
build/geography-export-%.png: geography.svg
	inkscape -z -e $@ -w $* -h $* $<
build/coast-translucent-%.png: build/coast-export-%.png
	(echo $<; echo $@) | bash c2a.bash
build/coast-export-%.png: coast.svg
	inkscape -z -e $@ -w $* -h $* $<

# LABELS
# SINDARIN TENGWAR

# tiles
# 1.81 HOURS
# 11.5 HOURS transitively
build/tiles/t: build/labels-tengwar-export-32768
	mkdir -p build/tiles
	python tiles_labels.py $< $@
	touch build/tiles/t

# the master label level sources
# 4.72 HOURS
build/labels-tengwar-export-32768: \
		build/labels-tengwar-export-32768/1 \
		build/labels-tengwar-export-32768/2 \
		build/labels-tengwar-export-32768/3 \
		build/labels-tengwar-export-32768/4 \
		build/labels-tengwar-export-32768/5 \
		build/labels-tengwar-export-32768/6 \
		build/labels-tengwar-export-32768/7 \
		build/labels-tengwar-export-32768/8

# quadtrees based on the master quads
build/labels-tengwar-export-32768/%: \
		build/labels \
		build/labels-tengwar-export-16384/%-0.png \
		build/labels-tengwar-export-16384/%-1.png \
		build/labels-tengwar-export-16384/%-2.png \
		build/labels-tengwar-export-16384/%-3.png
	mkdir -p build/labels-tengwar-export-32768
	inkscape -z -e build/labels-tengwar-export-32768/$*-.png -w 256 -h 256 -i layer$* -j build/labels-tengwar-opaque.svg
	python tiles.py build/labels-tengwar-export-16384/$*-0.png build/labels-tengwar-export-32768/$*-0
	python tiles.py build/labels-tengwar-export-16384/$*-1.png build/labels-tengwar-export-32768/$*-1
	python tiles.py build/labels-tengwar-export-16384/$*-2.png build/labels-tengwar-export-32768/$*-2
	python tiles.py build/labels-tengwar-export-16384/$*-3.png build/labels-tengwar-export-32768/$*-3

# export master quads
build/labels-tengwar-export-16384/%-0.png: build/labels build/labels-tengwar-opaque.svg build/labels-tengwar-export-16384
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 -i layer$* -j build/labels-tengwar-opaque.svg
build/labels-tengwar-export-16384/%-1.png: build/labels build/labels-tengwar-opaque.svg build/labels-tengwar-export-16384
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 -i layer$* -j build/labels-tengwar-opaque.svg
build/labels-tengwar-export-16384/%-2.png: build/labels build/labels-tengwar-opaque.svg build/labels-tengwar-export-16384
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 -i layer$* -j build/labels-tengwar-opaque.svg
build/labels-tengwar-export-16384/%-3.png: build/labels build/labels-tengwar-opaque.svg build/labels-tengwar-export-16384
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 -i layer$* -j build/labels-tengwar-opaque.svg
build/labels-tengwar-export-16384:
	mkdir -p $@

# a version of labels-tengwar.svg wherein all of the labels are opaque
build/labels-tengwar-opaque.svg: labels-tengwar.svg labels_opaque.py
	python labels_opaque.py labels-tengwar.svg $@

# ENGLISH LATIN LABELS

build/tiles/l: build/labels-latin-export-32768
	mkdir -p build/tiles
	python tiles_labels.py $< $@
	touch build/tiles/l

# the master label level sources
# 4.72 HOURS
build/labels-latin-export-32768: \
		build/labels-latin-export-32768/1 \
		build/labels-latin-export-32768/2 \
		build/labels-latin-export-32768/3 \
		build/labels-latin-export-32768/4 \
		build/labels-latin-export-32768/5 \
		build/labels-latin-export-32768/6 \
		build/labels-latin-export-32768/7 \
		build/labels-latin-export-32768/8

# quadtrees based on the master quads
build/labels-latin-export-32768/%: \
		build/labels \
		build/labels-latin-export-16384/%-0.png \
		build/labels-latin-export-16384/%-1.png \
		build/labels-latin-export-16384/%-2.png \
		build/labels-latin-export-16384/%-3.png
	mkdir -p build/labels-latin-export-32768
	inkscape -z -e build/labels-latin-export-32768/$*-.png -w 256 -h 256 -i layer$* -j build/labels-latin-opaque.svg
	python tiles.py build/labels-latin-export-16384/$*-0.png build/labels-latin-export-32768/$*-0
	python tiles.py build/labels-latin-export-16384/$*-1.png build/labels-latin-export-32768/$*-1
	python tiles.py build/labels-latin-export-16384/$*-2.png build/labels-latin-export-32768/$*-2
	python tiles.py build/labels-latin-export-16384/$*-3.png build/labels-latin-export-32768/$*-3

# export master quads
build/labels-latin-export-16384/%-0.png: build/labels build/labels-latin-opaque.svg build/labels-latin-export-16384
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 -i layer$* -j build/labels-latin-opaque.svg
build/labels-latin-export-16384/%-1.png: build/labels build/labels-latin-opaque.svg build/labels-latin-export-16384
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 -i layer$* -j build/labels-latin-opaque.svg
build/labels-latin-export-16384/%-2.png: build/labels build/labels-latin-opaque.svg build/labels-latin-export-16384
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 -i layer$* -j build/labels-latin-opaque.svg
build/labels-latin-export-16384/%-3.png: build/labels build/labels-latin-opaque.svg build/labels-latin-export-16384
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 -i layer$* -j build/labels-latin-opaque.svg
build/labels-latin-export-16384:
	mkdir -p $@

# a version of labels-latin.svg wherein all of the labels are opaque
build/labels-latin-opaque.svg: labels-latin.svg labels_opaque.py
	python labels_opaque.py labels-latin.svg $@

# GEOGRAPHY

# 40 MINUTES
build/tiles/g: build/geography-combined-32768
	mkdir -p build/tiles
	python tiles_darken.py $</t $@ .5
	touch build/tiles/g

build/geography-combined-32768: \
		build/geography-translucent-32768 \
		build/coast-translucent-32768
	mkdir -p $@
	python tiles_over.py \
		build/coast-translucent-32768/t \
		build/geography-translucent-32768/t \
		$@/t

build/geography-translucent-32768: build/geography-export-32768
	mkdir -p $@
	bash tiles_c2a.bash build/geography-export-32768/t build/geography-translucent-32768/t

build/geography-export-32768: \
		build/geography-export-16384/q0.png \
		build/geography-export-16384/q1.png \
		build/geography-export-16384/q2.png \
		build/geography-export-16384/q3.png
	mkdir -p build/geography-export-32768
	inkscape -z -e build/geography-export-32768/t.png -w 256 -h 256 geography.svg
	python tiles.py build/geography-export-16384/q0.png $@/t0
	python tiles.py build/geography-export-16384/q1.png $@/t1
	python tiles.py build/geography-export-16384/q2.png $@/t2
	python tiles.py build/geography-export-16384/q3.png $@/t3

build/geography-export-%/q.png: geography.svg
	inkscape -z -e $@ -w $* -h $* geography.svg
build/geography-export-16384/q0.png: geography.svg
	mkdir -p build/geography-export-16384
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 geography.svg
build/geography-export-16384/q1.png: geography.svg
	mkdir -p build/geography-export-16384
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 geography.svg
build/geography-export-16384/q2.png: geography.svg
	mkdir -p build/geography-export-16384
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 geography.svg
build/geography-export-16384/q3.png: geography.svg
	mkdir -p build/geography-export-16384
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 geography.svg

# COAST

# 1 HOUR
build/coast-translucent-32768: build/coast-export-32768
	mkdir -p $@
	bash tiles_c2a.bash build/coast-export-32768/t build/coast-translucent-32768/t

build/coast-export-32768: \
		build/coast-export-16384/q0.png \
		build/coast-export-16384/q1.png \
		build/coast-export-16384/q2.png \
		build/coast-export-16384/q3.png
	mkdir -p build/coast-export-32768
	inkscape -z -e build/coast-export-32768/t.png -w 256 -h 256 coast.svg
	python tiles.py build/coast-export-16384/q0.png build/coast-export-32768/t0
	python tiles.py build/coast-export-16384/q1.png build/coast-export-32768/t1
	python tiles.py build/coast-export-16384/q2.png build/coast-export-32768/t2
	python tiles.py build/coast-export-16384/q3.png build/coast-export-32768/t3

build/coast-export-%/q.png: coast.svg
	mkdir -p build/coast-export-$*
	inkscape -z -e $@ -w $* -h $* coast.svg
build/coast-export-16384/q0.png: coast.svg
	mkdir -p build/coast-export-16384
	inkscape -z -e $@ -a 0000:3600:3600:7200 -w 16384 -h 16384 coast.svg
build/coast-export-16384/q1.png: coast.svg
	mkdir -p build/coast-export-16384
	inkscape -z -e $@ -a 3600:3600:7200:7200 -w 16384 -h 16384 coast.svg
build/coast-export-16384/q2.png: coast.svg
	mkdir -p build/coast-export-16384
	inkscape -z -e $@ -a 0000:0000:3600:3600 -w 16384 -h 16384 coast.svg
build/coast-export-16384/q3.png: coast.svg
	mkdir -p build/coast-export-16384
	inkscape -z -e $@ -a 3600:0000:7200:3600 -w 16384 -h 16384 coast.svg


# Article Data
build/crawl/encyclopedia-arda.html:
	mkdir -p build/crawl
	curl http://www.glyphweb.com/ARDA/placland.html > $@

