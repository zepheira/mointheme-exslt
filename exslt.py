# -*- coding: iso-8859-1 -*-
"""
    MoinMoin exslt theme
    
    based on the ubuntu theme
    @copyright: (c) 2003-2004 by Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.

    Borrows heavily from modern, a bit from Classic, and has a few 
    things of its own.
"""

from MoinMoin.theme import ThemeBase
from MoinMoin import wikiutil
from MoinMoin.Page import Page
import re

class Theme(ThemeBase):

    name = 'exslt'

# Overriding theme/__init__.py #########################################

    # fake _ function to get gettext recognize those texts:
    _ = lambda x: x

    icons = {
        # key         alt                        icon filename      w   h
        # ------------------------------------------------------------------
        # navibar
        'help':       ("%(page_help_contents)s", "s-help.png",         20, 20),
        'find':       ("%(page_find_page)s",     "s-search.png",       20, 20),
        'diff':       (_("Diffs"),               "diff.png",         22, 22),
        'info':       (_("Info"),                "info.png",         22, 22),
        'edit':       (_("Edit"),                "edit.png",         20, 20),
        'unsubscribe':(_("Unsubscribe"),         "unsubscribe.png",  23, 21),
        'subscribe':  (_("Subscribe"),           "subscribe_dk.png", 23, 21),
        'raw':        (_("Raw"),                 "raw.png",          21, 23),
        'xml':        (_("XML"),                 "moin-xml2.png",      36, 14),
        'print':      (_("Print"),               "print.png",        20, 20),
        'view':       (_("View"),                "show.png",         20, 20),
        'home':       (_("Home"),                "home.png",         20, 20),
        'up':         (_("Up"),                  "parent.png",       20, 20),
        # FileAttach
        'attach':     ("%(attach_count)s",       "moin-attach.png",  7, 15),
        # RecentChanges
        'rss':        (_("[RSS]"),               "moin-rss.png",    36, 14),
        'deleted':    (_("[DELETED]"),           "deleted.png",      22, 22),
        'updated':    (_("[UPDATED]"),           "updated.png",      22, 22),
        'renamed':    (_("[RENAMED]"),           "moin-inter.png",      22, 22),
        'conflict':   (_("[CONFLICT]"),          "info.png",        22, 22),
        'new':        (_("[NEW]"),               "new.png",          22, 22),
        'diffrc':     (_("[DIFF]"),              "diff.png",         22, 22),
        # General
        'bottom':     (_("[BOTTOM]"),            "bottom.png",       14, 10),
        'top':        (_("[TOP]"),               "top.png",          14, 10),
        'www':        ("[WWW]",                  "www.png",          16, 16),
        'mailto':     ("[MAILTO]",               "email.png",        23, 13),
        'news':       ("[NEWS]",                 "news.png",         16, 16),
        'telnet':     ("[TELNET]",               "telnet.png",       16, 16),
        'ftp':        ("[FTP]",                  "ftp.png",          16, 16),
        'file':       ("[FILE]",                 "ftp.png",          16, 16),
        # search forms
        'searchbutton': ("[?]",                  "s-search.png",       20, 20),
        'interwiki':  ("[%(wikitag)s]",          "inter.png",        16, 16),
    }
    del _

# Public functions #####################################################

    def header(self, d, **kw):
        """ Assemble wiki header
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),
            
            # Header
            u'<div id="header">',
            u'<div id="mastwrap"><div id="masthead">',
            #self.logo(),
            self.searchform(d),
            self.username(d),
            u'</div></div>',
            self.msg(d),
            self.navibar(d),
            self.trail(d),
            self.extranav(d),
            self.editbar(d),
            u'</div>',
            
            # Post header custom html (not recommended)
            #self.emit_custom_html(self.cfg.page_header2),
            
            # Start of page
            self.startPage(),
            self.title(d),
        ]
        return u'\n'.join(html)


    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            # End of page
            u'</div>',
            #self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'<div id="footer">',
            self.footerlinks(),
            #self.showversion(d, **keywords),
            u'</div>',
            
            # Post footer custom html
            #self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)

    def extranav(self, d):
        """ Assemble the helpful extra navigation

	Of course in a normal theme these come from wikiconfig.py 
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: extranav html
        """
        request = self.request
        _ = request.getText
        changesPage = wikiutil.getLocalizedPage(request, 'RecentChanges')
        findPage = wikiutil.getLocalizedPage(request, 'FindPage')
        
        extralinks = []
        # Set page to localized RC page
        title = changesPage.split_title(request)
        extralinks.append(changesPage.link_to(request, text=title))
        # Set page to localized find page
        title = findPage.split_title(request)
        extralinks.append(findPage.link_to(request, text=title))
            
        extralinks = [u'<li>%s</li>\n' % link for link in extralinks]
        html = u'<ul class="extranav">\n%s</ul>' % ''.join(extralinks)
        return html

    def navibar(self, d):
        """ Assemble the navibar

        @param d: parameter dictionary
        @rtype: unicode
        @return: navibar html
        """
        request = self.request
        found = {} # pages we found. prevent duplicates
        items = [] # navibar items
        item = u'<li class="%s">%s</li>'
        current = d['page_name']

        # Add user links to wiki links, eliminating duplicates.
        userlinks = request.user.getQuickLinks()
        for text in userlinks:
            # Split text without localization, user know what she wants
            pagename, link = self.splitNavilink(text, localize=0)
            if not pagename in found:
                cls = 'userlink'
                if pagename == current:
                    cls = 'userlink current'
                items.append(item % (cls, link))
                found[pagename] = 1

        # Assemble html
        items = u'\n'.join(items)
        html = u'''
<ul id="navibar">
%s
</ul>
''' % items
        return html

    def footerlinks(self):
        """ Copyright notices and local links """
        html = u'''
     Powered by <a href="http://moinmoin.wikiwikiweb.de">MoinMoin</a>
'''
	return html

def execute(request):
    """
    Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

