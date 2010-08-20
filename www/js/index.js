(function () {

var SNAP_DELAY = 200;
var TILE_SIZE = 256;
var TILE_URL = "http://3rin.gs/tiles.8/";
var regions; // acquired via AJAX
var largeToSmall; // computed from regions
var show; // updated by the Map.onShow emitter

var scaleSizes = [
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
    32768
];

var layers = [
    {"name": "Geography", "prefix": "g"},
    {"name": "English / Latin", "prefix": "l"},
    {"name": "Sindarin / Tengwar", "prefix": "t", "visible": false}
];

$("select-labels").mousedown(function (event) {
    console.log('here');
    event.stopPropagation();
});

$.ajax({
    "url": "data.json",
    "dataType": "json",
    "success": function (data) {
        console.log(data);
        regions = data.regions;
        largeToSmall = [];
        for (var name in regions) {
            var region = regions[name];
            // transport numbers
            region.name = name;
            region.top = +region.y;
            region.left = +region.x;
            region.height = +region.h;
            region.width = +region.w;
            delete region.y;
            delete region.x;
            delete region.h;
            delete region.w;
            // computed numbers
            region.centerTop = region.top + region.height / 2;
            region.centerLeft = region.left + region.width / 2;
            region.area = region.height * region.width;
            region.bottom = region.top + region.height;
            region.right = region.left + region.width;
            largeToSmall.push(region);
        }
        largeToSmall.sort(byArea);
        onShow();
    }
});

function byArea(a, b) {
    return b.area - a.area;
}

function contains(a, b) {
    return a.top <= b.top &&
        a.left <= b.left &&
        a.bottom >= b.bottom &&
        a.right >= b.right;
}

var map = Map("#map", layers, scaleSizes, function (layer, scale, position, div) { // getTile
    if (!div)
        div = $("<img>");
    position.scale = scale;
    var quadkey = QuadKey(position);
    return div.attr({
        "src":
            TILE_URL +
            layer.prefix +
            quadkey +
            ".png",
        "class": "tile"
    });
}, function (_show) { // onShow
    show = _show;
    onShow();
});

// discover the most relevant visible regions when new tiles
// are shown
function onShow() {
    if (!regions || !show)
        return;
    var containers = [], contents = [], i, ii;
    for (i = 0, ii = largeToSmall.length; i < ii; i++) {
        var region = largeToSmall[i];
        if (contains(region, show.region))
            containers.unshift(region);
        if (contains(show.region, region))
            contents.push(region);
    }
    // XXX
}

// computes a quadkey, as used to name tiles, based on
// the position, including the scale, of the tile.
function QuadKey(position) {
    var path = [];
    for (var i = 0, ii = position.scale; i < ii; i++) {
        var y = position.top & (1 << i) && 1;
        var x = position.left & (1 << i) && 1;
        path.unshift("0123".charAt(y << 1 | x));
    }
    return path.join("")
}

function Map(el, layers, scales, getTile, onShow) {
    var freeList = [];
    var tiles = {};
    var bounds = {}; // the visible region in tile coordinates rounded outward
    var region = {}; // the visible region in normalized map coordinates
    var scale = 0;
    var hashHandle;

    // erase the javascript support warning
    $(el).html("");

    // the viewport control is a movable and resizable container
    // for all of the scales, layers, and tiles
    var viewportControl = $("<div></div>").attr({
        "class": "viewport"
    }).appendTo(el);

    var zoomControl = $("<div></div>").attr({
        "class": "control navigation-control"
    }).appendTo(el);

    // the navigator observes all clicking, dragging, and
    // scrolling events inside the map and manages the
    // viewports and zoom controls accordingly.  it delegates
    // the init, drag, and zoom events back to us so we can
    // adjust the *content* of the viewport control while
    // it adjusts the size and position.  it informs us
    // of the visible bounds of the viewport and the current
    // scale when that changes.
    var navigator = ZoomAndDrag(el, zoomControl, scales,
        function (viewport) { // init
            init();
            show(viewport);
            $(viewportControl).css(viewport);
            setTimeout(function () {
                window.map = navigator; // for debugging
                if (window.location.hash) {
                    var parts = window.location.hash.substring(1).split(/,/g);
                    navigator.go({
                        "height": parts[0],
                        "width": parts[1],
                        "top": parts[2],
                        "left": parts[3]
                    });
                } else {
                    navigator.go({
                        "top": .2,
                        "left": .2,
                        "height": .6,
                        "width": .6
                    });
                }
            }, 0);
        },
        function (viewport) { // drag
            show(viewport);
            $(viewportControl).css(viewport);
        },
        function (scale, viewport) { // zoom
            updateScale(scale);
            show(viewport);
            $(viewportControl).css(viewport);
        }
    );

    // constructs the containers for the layers and scales
    // with appropriate css classes and nesting.
    function init() {

        var i, ii, layer, j, jj;
        for (i = 0, ii = layers.length; i < ii; i++) {
            layer = layers[i];
            layer.scales = [];
            layer.control = $("<div></div>").attr({
                "class": "layer layer-" + layer.prefix
            }).appendTo(viewportControl);
            for (j = 0, jj = scales.length; j < jj; j++) {
                layer.scales[j] = $("<div></div>").attr({
                    "class": "scale scale-" + j
                }).css({
                    "display": j === scale && layer.visible ? 
                        "block" : "none"
                }).appendTo(layer.control);
            }
        }

    }

    // when the scale factor changes, the scale containers
    // for each layer have to be either shown or hidden.
    // there is one scale div for each scale in each layer div.
    // it might be possible to do this with a single css selector
    // instead of tracking the divs.
    function updateScale(_scale) {
        var i, ii, layer, scales;
        for (i = 0, ii = layers.length; i < ii; i++) {
            layer = layers[i];
            scales = layer.scales;
            if (!scales[_scale])
                throw new Error("No such scale: " + _scale);
            scales[scale].css({
                "display": "none"
            });
            scales[_scale].css({
                "display": "block"
            });
        }
        scale = _scale;
    }

    // fills the visible region with the correct tiles, garbage
    // collecting the tiles that are no longer visible
    function show(viewport) {
        var x, y, i, ii, layer; 
        calculateBounds(viewport);
        collect(); // garbage tiles
        if (hashHandle)
            clearTimeout(hashHandle);
        setTimeout(function () { // redraw

            for (i = 0, ii = layers.length; i < ii; i++) {
                layer = layers[i];
                if (!layer.visible)
                    continue;
                for (y = bounds.top; y <= bounds.bottom; y++) {
                    for (x = bounds.left; x <= bounds.right; x++) {
                        if (
                            y >= 0 &&
                            x >= 0 &&
                            y < viewport.height / TILE_SIZE &&
                            x < viewport.width / TILE_SIZE
                        ) {
                            showTile(layer, y, x);
                        }
                    }
                }
            }

            $(el).css({
                "background-position":
                    viewport.left + "px" +
                    " " +
                    viewport.top + "px"
            });

            if (onShow) {
                onShow({
                    "viewport": viewport, 
                    "region": region,
                    "bounds": bounds, 
                    "scale": scale
                });
            }

            hashHandle = setTimeout(function () {
                var at = navigator.at();
                location.replace(
                    '#' + at.height +
                    ',' + at.width +
                    ',' + at.top +
                    ',' + at.left
                );
                hashHandle = undefined;
            }, 250);

        }, 0);

    }

    // computes the range of tile numbers that are in the viewable
    // region of the map
    function calculateBounds(viewport) {
        var size = {
            "height": $(el).height(),
            "width": $(el).width()
        };
        bounds.left = Math.floor((-viewport.left - TILE_SIZE) / TILE_SIZE) + 1;
        bounds.right = Math.floor((-viewport.left + size.width + TILE_SIZE) / TILE_SIZE) - 1;
        bounds.top = Math.floor((-viewport.top - TILE_SIZE) / TILE_SIZE) + 1;
        bounds.bottom = Math.floor((-viewport.top + size.height + TILE_SIZE) / TILE_SIZE) - 1;
        region.left = -viewport.left / viewport.width;
        region.top = -viewport.top / viewport.height;
        region.width = size.width / viewport.width;
        region.height = size.height / viewport.height;
        region.bottom = region.top + region.height;
        region.right = region.left + region.width;
    }

    // removes all tiles that are not in the visible region and
    // puts them onto the free list so that the DOM elements
    // can be re-used.
    function collect() {
        var hash, layer, _scale, top, left;
        for (hash in tiles) {
            hash = hash.split(",");
            layer = hash[0];
            _scale = +hash[1];
            top = +hash[2];
            left = +hash[3];
            if (
                // in bounds
                scale === _scale &&
                top >= bounds.top &&
                top <= bounds.bottom &&
                left >= bounds.left &&
                left <= bounds.right &&
                layers[layer].visible
            ) {
                continue;
            }
            freeList.push($(tiles[hash]).remove());
            delete tiles[hash];
        }
    }

    // displays a single tile unless it's already visible
    function showTile(layer, y, x) {
        var hash = layer.prefix + "," + scale + "," + y + "," + x;
        if (tiles[hash])
            return;
        var tile = getTile(layer, scale, {
            "top": y,
            "left": x
        }, freeList.shift());
        tiles[hash] = tile;
        $(tile).css({
            "top": y * TILE_SIZE,
            "left": x * TILE_SIZE
        }).appendTo(layer.scales[scale]);
    }

}

// a controller for dragging and zooming a region.  the zoom and
// drag controller emits events for drag and zoom, providing
// the "viewport" (a description of the visible region of the map)
// and scale size to each event handler when they change.  the
// controller internally handles the position and size of the
// viewport control and the delegates manage the content of the
// control.
function ZoomAndDrag(map, control, scales, onInit, onDrag, onZoom) {
    var scale = 0,
        lock = false,
        viewport = {
            "left": 0,
            "top": 0,
            "height": scales[scale],
            "width": scales[scale]
        },
        handle;

    onInit(viewport);

    $("<span>Zoom:</span>").appendTo(control);
    var zoomRadios = [];
    for (var i = 0, ii = scales.length; i < ii; i++) {
        (function (i) {
            $("<br>").appendTo(control);
            var radio = $("<input>").attr({
                "name": "zoom",
                "id": "zoom-" + i,
                "type": "radio",
                "checked": i == scale
            }).click(function (event) {
                zoom(i, {
                    "top": $(map).height() / 2,
                    "left": $(map).width() / 2
                });
            }).appendTo(control);
            $("<label>" + i + "</label>").attr({
                "for": "zoom-" + i
            }).appendTo(control);
            zoomRadios.push(radio);
        })(i);
    }

    $(map).mousewheel(scroll);
    $(map).dblclick(dblclick);

    Drag(
        map,
        function (event, delta) { // onMove
            viewport.left += delta.left;
            viewport.top += delta.top;
            onDrag(viewport);
        },
        null, // onDown
        null, // onUp
        scroll
    );

    return {
        // window coordinates are from a normal square
        "go": function (top, left, height, width) {
            var normal, _scale, window, mapSize;
            if (typeof top === "number") {
                normal = {
                    "top": top,
                    "left": left,
                    "height": height,
                    "width": width
                }
            } else {
                normal = top;
            }
            mapSize = {
                "height": $(map).height(),
                "width": $(map).width()
            };
            // find the highest resolution that fits in the map view
            for (_scale = scales.length - 1; _scale > 0; _scale--) {
                // the considered scale
                // the normal, projected into the scale under consideration
                window = {
                    "top": normal.top * scales[_scale],
                    "left": normal.left * scales[_scale],
                    "height": normal.height * scales[_scale],
                    "width": normal.width * scales[_scale]
                };
                // if the window size fits in the map view, use this scale
                if (window.height <= mapSize.height && window.width <= mapSize.width)
                    break;
            }
            window = {
                "top": normal.top * scales[_scale],
                "left": normal.left * scales[_scale],
                "height": normal.height * scales[_scale],
                "width": normal.width * scales[_scale]
            };
            scale = _scale;
            viewport.top = - window.top - window.height / 2 + mapSize.height / 2;
            viewport.left = - window.left - window.width / 2 + mapSize.width / 2;
            viewport.height = scales[_scale];
            viewport.width = scales[_scale];
            update();
            onZoom(scale, viewport);
        },
        "at": function () {
            var mapSize = {
                "height": $(map).height(),
                "width": $(map).width()
            };
            return {
                "top": -viewport.top / scales[scale],
                "left": -viewport.left / scales[scale],
                "height": mapSize.height / scales[scale],
                "width": mapSize.width / scales[scale]
            };
        }
    };

    function dblclick(event) {
        var mapPosition = $(map).position();
        var mapSize = {
            "width": $(map).width(),
            "height": $(map).height()
        };
        viewport.top = (
            mapSize.height / 2
            - (event.pageY - mapPosition.top)
            + viewport.top
        );
        viewport.left = (
            mapSize.width / 2
            - (event.pageX - mapPosition.left)
            + viewport.left
        );
        onDrag(viewport);
    }

    function scroll(event, delta, about) {
        var _scale;

        // if using the scroll wheel, the focus position is the current cursor.
        // if click and drag with shift key, the focus position is provided by
        // the Drag control
        if (!about) {
            about = {
                "top": event.pageY,
                "left": event.pageX
            }
        }

        // rather than normalizing the delta between browsers (since
        // some of them appear to not be properly accounted for by 
        // the mousewheel module), only permit one halving or doubling
        // of the scale until mousewheel events have settled for
        // the duration of one snap delay.
        if (handle) {
            delay();
            return;
        }
        delay();

        delta = delta / Math.abs(delta); // normalize the delta to +/- 1
        // calculate the next scale, bounded by the scale range
        _scale = Math.min(Math.max(scale + delta, 0), scales.length - 1);
        if (isNaN(_scale))
            return;

        zoom(_scale, about);
    }

    function zoom(_scale, about) {
        var mapPosition, factor;
        // compute the scaling factor from the sizes of the old and new
        // scales.  this algorithm is general enough to handle changes
        // between any two real scale sizes, although we snap to integer
        // scale sizes presently.
        mapPosition = $(map).position();
        factor = scales[_scale] / scales[scale];

        // adjust the viewport position such that the cursor remains
        // at the same geographic location before and after the scale
        // change
        viewport.left += (about.left - mapPosition.left - viewport.left) * (1 - factor);
        viewport.top += (about.top - mapPosition.top - viewport.top) * (1 - factor);
        viewport.height = scales[_scale];
        viewport.width = scales[_scale];

        // reify the scale state
        scale = _scale;
        update();
        onZoom(_scale, viewport);

    }

    function update() {
        zoomRadios[scale].attr({
            "checked": true
        });
    }

    function delay () {
        if (handle)
            clearTimeout(handle);
        handle = setTimeout(function () {
            handle = undefined;
        }, SNAP_DELAY);
    }

}

// the drag controller consumes all the clicking
// events in the given region and emits the position
// deltas to mouse move, down, and up observers.
function Drag(el, onMove, onDown, onUp, onScroll) {
    var isDown, left, top, scroll, start;
    $(el).mousedown(function (event) {
        isDown = true;
        scroll = event.shiftKey;
        left = event.pageX;
        top = event.pageY;
        start = {
            "left": left,
            "top": top
        }
        onDown && onDown(event);
        event.stopPropagation();
        event.preventDefault();
    });
    $(window).mousemove(function (event) {
        if (isDown) {
            if (scroll) {
                var delta = (event.pageX - left) + (top - event.pageY);
                left = event.pageX;
                top = event.pageY;
                onScroll && onScroll(event, delta, start);
            } else {
                var dx = event.pageX - left;
                var dy = event.pageY - top;
                left = event.pageX;
                top = event.pageY;
                onMove && onMove(event, {"left": dx, "top": dy});
            }
        }
    });
    $(window).mouseup(function (event) {
        isDown = false;
        onUp && onUp(event);
    });
}

})();
