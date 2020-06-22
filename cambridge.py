#!/usr/bin/env python
from httplib import HTTPSConnection
from parsel import Selector
from HTMLParser import HTMLParser

class ExtractTEXT(HTMLParser):
    content = ''
    def handle_data(self, data):
        self.content = self.content + data
        pass
    pass

def to_plaintext(html):
    extract = ExtractTEXT()
    extract.feed(html)
    return extract.content.encode('utf-8').strip()

class CambridgeWord(object):
    def __init__(self, doc):
        super(CambridgeWord, self).__init__()

        sel = Selector(text=doc)
        ipa_elm = sel.css('span.uk > span.pron span.ipa').extract_first()
        self.ipa = to_plaintext(ipa_elm)

        self.entries = []
        entries = sel.css('div.entry-body__el')
        existing_definitions = set()
        for entry in entries:
            posgram_elm = entry.css('div.posgram').extract_first()
            if posgram_elm:
                posgram = to_plaintext(posgram_elm)
            else:
                posgram = '...'
                pass
            defblocks = []
            for defblock in entry.css('div.def-block'):
                alldefs = defblock.css('div.def')
                if len(alldefs):
                    onedef = alldefs[0]
                    definition = to_plaintext(onedef.extract()).strip(':')
                    if definition in existing_definitions:
                        continue
                    existing_definitions.add(definition)
                else:
                    definition = '...'
                    pass
                egs = []
                for eg_elm in defblock.css('span.eg'):
                    eg = to_plaintext(eg_elm.extract())
                    egs.append(eg)
                    pass
                defblocks.append({'definition': definition, 'egs': egs})
                pass
            if defblocks:
                self.entries.append({'posgram': posgram, 'defblocks': defblocks})
                pass
            pass

        try:
            self.audio = sel.css('span.uk span.daud source')[0].xpath('@src').extract_first()
        except:
            self.audio = sel.css('span.us span.daud source')[0].xpath('@src').extract_first()
            pass
        pass
    pass

def get_word(word):
    url = 'https://dictionary.cambridge.org/dictionary/english/%s' % (word)
    con = HTTPSConnection('dictionary.cambridge.org')
    con.connect()
    con.request('GET', url)
    con.send('')
    resp = con.getresponse()
    resp.begin()
    doc = resp.read().decode('utf-8')

    word = CambridgeWord(doc)
    return word

def replace(txt, src, dst):
    while txt.find(src) >= 0:
        idx = txt.find(src)
        txt = txt[:idx] + dst + txt[idx+len(src):]
        pass
    return txt

def ascii_ipa(ipa):
    while ipa.find('\xcb\x88') >= 0:
        idx = ipa.find('\xcb\x88')
        ipa = ipa[:idx] + '\'' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\x9c') >= 0:
        idx = ipa.find('\xc9\x9c')
        ipa = ipa[:idx] + '3' + ipa[idx+2:]
        pass
    while ipa.find('\xcb\x90') >= 0:
        idx = ipa.find('\xcb\x90')
        ipa = ipa[:idx] + ':' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\x99') >= 0:
        idx = ipa.find('\xc9\x99')
        ipa = ipa[:idx] + '(e)' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\xaa') >= 0:
        idx = ipa.find('\xc9\xaa')
        ipa = ipa[:idx] + 'I' + ipa[idx+2:]
        pass
    while ipa.find('\xcb\x8c') >= 0:
        idx = ipa.find('\xcb\x8c')
        ipa = ipa[:idx] + ',' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\x92') >= 0:
        idx = ipa.find('\xc9\x92')
        ipa = ipa[:idx] + '(o)' + ipa[idx+2:]
        pass
    while ipa.find('\xca\x83') >= 0:
        idx = ipa.find('\xca\x83')
        ipa = ipa[:idx] + 'S' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\x94') >= 0:
        idx = ipa.find('\xc9\x94')
        ipa = ipa[:idx] + '(c)' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\xa1') >= 0:
        idx = ipa.find('\xc9\xa1')
        ipa = ipa[:idx] + 'g' + ipa[idx+2:]
        pass
    while ipa.find('\xc9\x91') >= 0:
        idx = ipa.find('\xc9\x91')
        ipa = ipa[:idx] + 'a' + ipa[idx+2:]
        pass
    while ipa.find('\xca\x8c') >= 0:
        idx = ipa.find('\xca\x8c')
        ipa = ipa[:idx] + '(v)' + ipa[idx+2:]
        pass
    ipa = replace(ipa, '\xce\xb8', '8')
    ipa = replace(ipa, '\xc3\xa6', 'ae')
    ipa = replace(ipa, '\xca\x8a', 'U')
    ipa = replace(ipa, '\xca\x92', '5')
    ipa = replace(ipa, '\xc2\xb7', '.')
    ipa = replace(ipa, '\xc5\x8b', '9')
    ipa = replace(ipa, '\xc3\xb0', '6')
    #print repr(ipa)
    return ipa

def break_lines(txt, line_width=70):
    words = txt.split()
    lines = []
    line = ''
    for word in words:
        new_len = len(line) + len(word)
        if len(line):
            new_len = new_len + 1
            pass
        if new_len > line_width:
            lines.append(line)
            line = ''
            pass
        line = line + ' ' + word
        line = line.strip()
        pass
    lines.append(line)
    return lines

def show_definition(definition, blines=break_lines):
    lines = blines(definition)
    for line in lines:
        print '%s' % line
        pass
    pass

def show_eg(eg, blines=break_lines):
    lines = blines(eg)

    print '   - %s' % (lines[0])
    for line in lines[1:]:
        print '     %s' % (line)
        pass
    pass

def print_word(word_txt, blines=break_lines):
    word = get_word(word_txt)
    print '%s /%s/' % (word_txt, ascii_ipa(word.ipa))
    print
    for entry in word.entries:
        posgram = entry['posgram']
        print ':%s' % (posgram)
        print
        defblocks = entry['defblocks']
        for defblock in defblocks:
            show_definition(defblock['definition'], blines)
            for eg in defblock['egs']:
                show_eg(eg, blines)
                pass
            print
            pass
        pass
    print word.audio
    pass

def print_definitions(word_txt, blines=break_lines):
    word = get_word(word_txt)
    print '%s /%s/' % (word_txt, ascii_ipa(word.ipa))
    print
    for entry in word.entries:
        posgram = entry['posgram']
        defblocks = entry['defblocks']
        for defblock in defblocks:
            show_definition(defblock['definition'], blines)
            pass
        pass
    pass

if __name__ == '__main__':
    import sys
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], "d")
    word = args[0]
    do_show_definitions = False
    for opt, value in opts:
        if opt == '-d':
            do_show_definitions = True
            pass
        pass

    if do_show_definitions:
        print_definitions(word)
    else:
        print_word(word)
        pass
    pass
