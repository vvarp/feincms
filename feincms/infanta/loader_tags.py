from django import template
from django.core.exceptions import ImproperlyConfigured

from feincms.module.page.models import Page


register = template.Library()

class BoxNode(template.Node):
    def __init__(self, nodelist, region):
        self.nodelist = nodelist
        self.region = region
        self.feincms_page = None
        self.block_registered = None

    def register_view_content(self, id, content):
        self.feincms_page.vc_manager[id] = content
        self.block_registered = None
    
    def is_registered(self, id):
        return id in self.feincms_page.vc_manager

    """
    looks for a ViewContent in the page tree
    if we're lucky to find one corresponding the region, store the content in the feincms_page vc_manager
    if we got no luck, just attach it to the according region
    """    
    def render(self, context):
        try:
            self.feincms_page = context['feincms_page']
        except KeyError:
            request = context.get('request')
            if not request:
                raise ImproperlyConfigured('One of the following context processors must be activated: django.core.context_processors.request, feincms.context_processors.add_page_if_missing')
            self.feincms_page = request._feincms_page
               
        if not self.region in [v.key for v in Page._feincms_all_regions]:
            """
            the named region was not found
            what shall i do?
            """
            return
        
        region = self.feincms_page.template.regions_dict[self.region]
        from infanta.models import ViewContent
        for content in self.feincms_page._content_for_region(region):
            if isinstance(content, ViewContent) and not self.is_registered(content.id):
                self.register_view_content(content.id, self.nodelist.render(context))                
                break
        if not self.block_registered:
            """
            no ViewContent found to attach the content
            what shall i do?
            """
            return
        return

'''
usage:
        {% box region_name %}
        
        region name must be one of your defined region
'''
@register.tag(name="box")
def do_box(parser, token):
    nodelist = parser.parse(('endbox',))
    parser.delete_first_token()
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, region = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly 1 argument" % token.contents.split()[0]
    return BoxNode(nodelist, region)

from django.template.loader_tags import ExtendsNode, do_extends

class NewExtendsNode(ExtendsNode):
    
    def __init__(self, extends_node):
        super(NewExtendsNode,self).__init__(extends_node.nodelist, extends_node.parent_name, extends_node.parent_name_expr, template_dirs = extends_node.template_dirs)
        
    def render(self, context):
        for box in self.nodelist.get_nodes_by_type(BoxNode):
            box.render(context)
        return super(NewExtendsNode,self).render(context)

@register.tag(name="extends")
def new_do_extends(parser, token):
    extends_node = do_extends(parser, token)
    return NewExtendsNode(extends_node)