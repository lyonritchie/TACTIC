############################################################
#
#    Copyright (c) 2010, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['DynamicListWdg']


from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg
from pyasm.widget import CheckboxWdg, HiddenWdg, IconWdg, IconButtonWdg


class DynamicListWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'show_enabled': 'determines whether or not to show enabled checkboxes'
    }

    def init(self):
        self.items = []
        self.template = None

        self.show_enabled = self.kwargs.get('show_enabled')
        if self.show_enabled in ['true', True]:
            self.show_enabled = True
        else:
            self.show_enabled = False


    def add_item(self, item):
        self.items.append(item)

    def add_template(self, template):
        self.template = template

    def get_display(self):
        #assert self.template


        top = DivWdg()
        top.add_class("spt_list_top")

        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            })

        callback = self.kwargs.get("callback") or ''
        top.add_behavior( {
            'type': 'load',
            'cbjs_action': callback
        } )

        remove_callback = self.kwargs.get("remove_callback") or '''
        spt.dynamic_list.set_top(bvr.src_el);
        spt.dynamic_list.remove_item(bvr.src_el);
        '''
        top.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_remove',
            'cbjs_action': remove_callback
        } )

        add_callback = self.kwargs.get("add_callback") or '''
        spt.dynamic_list.set_top(bvr.src_el);
        spt.dynamic_list.add_item();
        '''
        top.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_add',
            'cbjs_action': add_callback
        } )


        if self.template:
            template_wdg = self.get_item_wdg(self.template, is_template=True)
            template_wdg.add_class("SPT_TEMPLATE")
            top.add(template_wdg )

        for item in self.items:
            item_wdg = self.get_item_wdg(item)
            top.add( item_wdg )

        return top



    def get_item_wdg(self, item, is_template=False):
        item_div = DivWdg()
        item_div.add_style("margin-top: 3px")


        if is_template == True:
            item_div.add_style("display: none")
            #item_div.add_style("border: solid 1px blue")
            item_div.add_class("spt_list_template_item")
        else:
            item_div.add_class("spt_list_item")
            item_div.add_style("display: flex")


        item_div.add_style("align-items: center")

        outer = DivWdg()
        #outer.add_style("float: left")
        outer.add_style("text-align: left")
        outer.add(item)

        # for some reason, there is a spacing needed
        #outer.add_style("margin-right: 20px")


        if self.show_enabled:
            checkbox = CheckboxWdg("enabled")
            #checkbox.add_style("float: left")
            checkbox.set_checked()
        else:
            checkbox = HiddenWdg("enabled")
        item_div.add(checkbox)

        #item_div.add(item)
        item_div.add(outer)

        from tactic.ui.widget import IconButtonWdg

        add_wdg = DivWdg()
        add_wdg.add_class("hand")
        add_wdg.add_class("SPT_DTS")
        #add_wdg.add("(+)")
        add_wdg.add_class("spt_add")
        button = IconButtonWdg(title="Add Entry", icon="FA_PLUS", size=12)
        add_wdg.add(button)
        #add_wdg.add_style("float: left")
        add_wdg.add_style("opacity: 0.5")
        #add_wdg.add_style("margin: 3px")
        item_div.add(add_wdg)



        remove_wdg = DivWdg()
        remove_wdg.add_class("hand")
        remove_wdg.add_class("SPT_DTS")
        #remove_wdg.add("(-)")
        remove_wdg.add_class("spt_remove")
        button = IconButtonWdg(title="Remove Entry", icon="FA_TIMES", size=12)
        remove_wdg.add(button)
        #remove_wdg.add_style("float: left")
        remove_wdg.add_style("opacity: 0.5")
        #remove_wdg.add_style("margin: 3px")
        item_div.add(remove_wdg)
        item_div.add("<br clear='all'/>")

        return item_div


    def get_values_script(self):
        save_button = IconButtonWdg("Save Settings", IconWdg.SAVE)
        save_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            get_values = function() {
                var top = bvr.src_el.getParent(".spt_list_top");
                var elements = bvr.src_el.getElements(".spt_list_items");
                var data = [];
                for (var i=0; i<elements.length; i++) {
                    var values = spt.api.get_input_values(elements[i]);
                    data.push(values)
                }
                return data;
            }
            '''
        } )
        content_div.add(save_button)


    def get_onload_js(self):

        return '''

spt.dynamic_list = spt.dynamic_list || {};
spt.dynamic_list.top = bvr.src_el;

spt.dynamic_list.set_top = function(top) {
    if (top.hasClass("spt_list_top")) {
        spt.dynamic_list.top = top;
    } else if (top.getParent(".spt_list_top")) {
        spt.dynamic_list.top = top.getParent(".spt_list_top")
    } else {
        spt.exception.handler("Dynamic list top must have class 'spt_list_top'");
    }
}

spt.dynamic_list.get_top = function() {
    return spt.dynamic_list.top;
}

spt.dynamic_list.add_item = function(src_el) {

    if (src_el) {
        var top = src_el.getParent(".spt_list_top");
    }
    else {
        var top = spt.dynamic_list.top;
    }

    if (!top) {
        spt.alert("No top in dynamic list found");
        return;
    }


    var template = top.getElement(".spt_list_template_item");

    var new_item = spt.behavior.clone(template);
    new_item.removeClass("spt_list_template_item");
    new_item.addClass("spt_list_item")
    new_item.setStyle("display", "flex");

    if (src_el) {
        var item = src_el.getParent(".spt_list_item");
        new_item.inject(item, 'after');
    } else {
        top.appendChild(new_item);
    }

    return new_item;
}

spt.dynamic_list.remove_item = function(src_el) {
    var top = spt.dynamic_list.top;
    var items = top.getElements(".spt_list_item");
    if (items.length > 1) {
        var item = src_el.getParent(".spt_list_item");
        item.destroy();
    }
}

        '''











