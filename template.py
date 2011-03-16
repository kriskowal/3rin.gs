
from django.template import loader, Context
from os import environ as env
from os.path import basename, dirname, join
import sys
env["DJANGO_SETTINGS_MODULE"] = "settings"

template_name = basename(sys.argv[1])
template = loader.get_template(template_name)
content = template.render(Context({}))
open(join(dirname(__file__), 'www', template_name), 'w').write(content)

