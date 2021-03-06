(function () {

var SNAP_DELAY = 150;
var TILE_SIZE = 256;
var TILE_URL = "/tiles.22/";
var ARTICLE_URL = "/articles.8/";
var regions; // acquired via AJAX
var largeToSmall; // computed from regions
var show; // updated by the Map.onShow emitter
var article = "";
var letters = "l";
var mode = "article-index";

var layers = [
    {"name": "Geography", "prefix": "g", "visible": true},
    {"name": "English / Latin", "prefix": "l", "visible": true},
    {"name": "Sindarin / Tengwar", "prefix": "t", "visible": false}
];

var labels = {
    "l": layers[1],
    "t": layers[2]
};

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

setTimeout(function () {
    $.ajax({
        "url": "data.json",
        "dataType": "json",
        "success": function (data) {
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
                region.area = region.height * region.width;
                region.bottom = region.top + region.height;
                region.right = region.left + region.width;
                largeToSmall.push(region);
            }
            largeToSmall.sort(byArea);
            search(regions, largeToSmall);
            onShow();
        }
    });
}, 500);

function search(regions, ordered) {
    var names = [];
    $.each(ordered, function (i, that) {
        $.each(that.names || [], function (j, name) {
            names.push({
                "label": name,
                "value": that.name
            });
        });
    });
    $("#search-form").bind("submit", function (event) {
        event.preventDefault();
        event.stopPropagation();
        var name = $("#search").val();
        if (regions[name]) {
            go(name);
            $("#search").val("").focus();
        }
    });
    $("#search").autocomplete({
        "source": names,
        "select": function (event, ui) {
            go(ui.item.value);
            $("#search").val("").focus();
        }
    }).keydown(function (event) {
        if (event.charCode === 27 || event.keyCode === 27) {
            $(this).blur();
            event.stopPropagation();
            event.preventDefault();
        }
    }).keypress(function (event) {
        event.stopPropagation();
    });
}

$("#select-labels").change(function () {
    showLetters($(this).val());
});

$(window).keypress(function (event) {
    var key = event.keyCode || event.charCode;
    event.preventDefault();
    event.stopPropagation();
    if (key ==="l".charCodeAt())
        showLetters(letters === "l" ? "t" : "l");
    else if (key === "L".charCodeAt())
        showLetters("*");
    else if (key === "/".charCodeAt())
        $("#search").focus();
});

function showLetters(_letters) {
    letters = _letters;
    $("#select-labels").val(letters);
    labels.l.visible = false;
    labels.t.visible = false;
    if (labels[letters])
        labels[letters].visible = true;
    map.update();
}

function go(region) {
    if (typeof region === "string")
        region = regions[region];
    if (!region)
        return;
    showArticle(region.name);
    map.go(region);
}

function showArticle(_article) {
    article = _article;
    $("#article").scroll(0).hide("fast");
    $.ajax({
        "url": ARTICLE_URL + article + ".frag.html",
        "dataType": "text",
        "success": function (data, status, xhr) {
            var hider = $("<a>close</a>").attr({
                "href": "#"
            }).css({
                "float": "right",
                "padding": "1em"
            }).click(function () {
                hideArticle();
            });
            $(".article-control").animate({
                "width": "50ex"
            }, "fast");
            $("#articles-index").scroll(0).hide("fast");
            $("#article").html(data).prepend(hider).show("fast");
            mode = "article";
        }
    });
}

function hideArticle() {
    mode = "article-index";
    article = "";
    $(".article-control").css({
        "width": "30ex"
    });
    $("#article").scroll(0).hide("fast");
    $("#articles-index").show("fast");
    onShow();
}

function byArea(a, b) {
    return b.area - a.area;
}

function contains(a, b) {
    return a.top <= b.top &&
        a.left <= b.left &&
        a.bottom >= b.bottom &&
        a.right >= b.right;
}

$(window).resize(function () {
    map.update();
});

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
    if (!largeToSmall || !show)
        return;
    var containers = [], contents = [], i, ii;
    for (i = 0, ii = largeToSmall.length; i < ii; i++) {
        var region = largeToSmall[i];
        if (contains(region, show.region))
            containers.push(region);
        if (contains(show.region, region))
            contents.push(region);
    }
    report(containers, contents);
}

function report(containers, contents) {
    var report = [];
    var j, jj,
        lists = [containers, contents],
        element = $("<div></div>");
    for (j = 0, jj = lists.length; j < jj; j++) {
        var i, ii, location, locations = lists[j];
        if (j === 1 && locations.length > 0)
            $("<hr>").appendTo(element);
        for (i = 0, ii = locations.length; i < ii; i++) {
            (function (location) {
                if (j === 0 && i === ii - 1)
                    document.title = location.names.join(" / ");
                $.each(location.names, function (k, name) {
                    $("<a></a>").attr({
                        "href": "#" + [
                            location.width.toFixed(7),
                            location.height.toFixed(7),
                            location.left.toFixed(7),
                            location.top.toFixed(7)
                        ].join(",")
                    }).click(function () {
                        go(location);
                    }).html("&laquo;" + name + "&raquo;").appendTo($("<nobr></nobr>").appendTo($("<div></div>").appendTo(element)));
                    $("<span>  </span>").appendTo(element);
                });
            })(locations[i]);
        }
    }
    if (mode === "article-index") {
        $("#articles-index").empty().append(element).css({
            "width": 0
        });
        $(".article-control").animate({
            "width": $("#articles-index").attr("scrollWidth") + 20 + "px"
        }, "fast");
        $("#articles-index").css({
            "width": "100%"
        });
    }
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
                        "left": parts[3],
                        "letters": parts[4],
                        "name": parts[5]
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
            updateLayers(scale);
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
                    "display": j === scale && layer.visible ? "block" :"none"
                }).appendTo(layer.control);
            }
        }

    }

    // when the scale factor changes, the scale containers
    // for each layer have to be either shown or hidden.
    // there is one scale div for each scale in each layer div.
    // - it might be possible to do this with a single css selector
    // instead of tracking the divs.
    function updateLayers(_scale) {
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
                "display": layer.visible ? "block" : "none"
            });
        }
        scale = _scale;
    }

    // fills the visible region with the correct tiles, garbage
    // collecting the tiles that are no longer visible
    function show(viewport) {
        var x, y, i, ii, layer, showing = [];
        calculateBounds(viewport);
        collect(); // garbage tiles

        $(el).css({
            "background-position":
                viewport.left + "px" +
                " " +
                viewport.top + "px"
        });

        setTimeout(function () { // yield to invoke redraw
            for (i = 0, ii = layers.length; i < ii; i++) {
                layer = layers[i];
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
        }, 0);

        if (hashHandle)
            clearTimeout(hashHandle);
        hashHandle = setTimeout(function () {
            var at = navigator.at();
            location.replace(
                '#' + at.height.toFixed(7) +
                ',' + at.width.toFixed(7) +
                ',' + at.top.toFixed(7) +
                ',' + at.left.toFixed(7) + 
                ',' + letters +
                ',' + article
            );
            if (onShow) {
                onShow({
                    "viewport": viewport, 
                    "region": region,
                    "bounds": bounds, 
                    "scale": scale
                });
            }

            hashHandle = undefined;
        }, 250);

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
            if ( // in bounds
                scale === _scale &&
                top >= bounds.top &&
                top <= bounds.bottom &&
                left >= bounds.left &&
                left <= bounds.right
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
        tile.unbind();
        tile.bind('load', function () {
            $(tile).css({
                "top": y * TILE_SIZE,
                "left": x * TILE_SIZE
            }).appendTo(layer.scales[scale]);
        });
    }

    return navigator;
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

    var navigator = {
        // window coordinates are from a normal square
        "go": function (top, left, height, width, letters, name) {
            var normal, _scale, window, mapSize;
            if (typeof top === "number") {
                normal = {
                    "top": top,
                    "left": left,
                    "height": height,
                    "width": width,
                    "letters": letters,
                    "name": name
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
            if (normal.name)
                showArticle(normal.name);
            if (normal.letters)
                showLetters(normal.letters);
            else {
                update();
                onZoom(scale, viewport);
            }
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
        },
        "update": function () {
            navigator.go(navigator.at());
        }
    };

    return navigator;

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
    var el = $(el).get(0);
    el.addEventListener && el.addEventListener("touchstart", function (event) {
        event.stopPropagation();
        event.preventDefault();
        var x = 0, y = 0, d = 0, i, ii = event.touches.length;
        for (i = 0; i < ii; i++) {
            var touch = event.touches[i];
            x += touch.pageX;
            y += touch.pageY;
        }
        x /= ii;
        y /= ii;
        for (i = 0; i < ii; i++) {
            var touch = event.touches[i];
            d += Math.sqrt(Math.pow(touch.pageX - x, 2) + Math.pow(touch.pageY - y, 2));
        }
        d /= ii;
        left = x;
        top = y;
        scroll = d;
    });
    el.addEventListener && el.addEventListener("touchmove", function (event) {
        event.stopPropagation();
        event.preventDefault();
        var x = 0, y = 0, d = 0, i, ii = event.touches.length;
        for (i = 0; i < ii; i++) {
            var touch = event.touches[i];
            x += touch.pageX;
            y += touch.pageY;
        }
        x /= ii;
        y /= ii;
        for (i = 0; i < ii; i++) {
            var touch = event.touches[i];
            d += Math.sqrt(Math.pow(touch.pageX - x, 2) + Math.pow(touch.pageY - y, 2));
        }
        d /= ii;
        onMove && onMove(event, {
            "left": x - left,
            "top": y - top
        });
        onScroll && onScroll(event, d - scroll, {
            "left": x,
            "top": y
        });
        left = x;
        top = y;
        scroll = d;
    });
    el = undefined;
}

})();
