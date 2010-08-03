#!/bin/bash
while read input; read output; do
    gimp -i -b "
        (let*
            (
                (in-filename "'"'"$input"'"'")
                (out-filename "'"'"$output"'"'")
                (color "'"'"#ffffff"'"'")
                (image (car (gimp-file-load RUN-NONINTERACTIVE in-filename in-filename)))
                (drawable (car (gimp-image-get-active-layer image)))
            )
            (plug-in-colortoalpha RUN-NONINTERACTIVE image drawable color)
            (gimp-file-save RUN-NONINTERACTIVE image drawable out-filename out-filename)
            (gimp-image-delete image)
            (gimp-quit 0)
        )
    "
done
