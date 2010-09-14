#!/bin/bash -x
xargs -n 512 | while read ARGS; do
    # this is a crime against humanity, and I know it.
    FILE_NAMES=$(echo $ARGS | xargs -n 1 | while read line; do echo '"'"$line"'"'; done)
    echo $FILE_NAMES
    gimp -i -d --stack-trace-mode always -b "
        (let*
            (
                (file-names '($FILE_NAMES))
            )
            (while (not (null? file-names))
                (let*
                    (
                        (in-filename (car file-names))
                        (out-filename (car (cdr file-names)))
                        (color "'"'"#ffffff"'"'")
                        (image (car (gimp-file-load RUN-NONINTERACTIVE in-filename in-filename)))
                        (drawable (car (gimp-image-get-active-layer image)))
                    )
                    (plug-in-colortoalpha RUN-NONINTERACTIVE image drawable color)
                    (gimp-file-save RUN-NONINTERACTIVE image drawable out-filename out-filename)
                    (gimp-image-delete image)
                )
                (set! file-names (cdr (cdr file-names)))
            )
        )
    " -b "(gimp-quit 0)" || exit -1
done
