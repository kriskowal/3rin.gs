#!/bin/bash
python tiles_walk.py $3 | while read quadkey; do
    echo $1$quadkey.png
    echo $2$quadkey.png
done | bash c2a.bash
