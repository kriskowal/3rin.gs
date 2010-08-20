
import xml.dom.minidom as dom

def walk(node):
    if node.nodeType != 1:
        return

    if node.tagName == 'image':
        style = node.getAttribute("style")
        style = dict(
            pair.split(":", 1)
            for pair in style.split(";")
            if pair
        )
        style["opacity"] = "1";
        node.setAttribute("style", ";".join(
            ":".join(pair)
            for pair in style.items()
        ))

    child = node.firstChild
    while child:
        walk(child)
        child = child.nextSibling

def command(source, target):
    doc = dom.parse(source)
    walk(doc.documentElement)
    doc.writexml(open(target, "w"))

def main():
    import sys
    command(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()

