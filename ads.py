import re
import urllib2
import time
import sys


def scrap(type, prmt):
    if type == 'a':
        fauthor, author_list, year = prmt
        faut = '%2C+'.join(fauthor.split(','))
        if faut != '':
            faut = '%5E' + faut
        for i, aut in enumerate(author_list):
            aut_splited = aut.split(',')
            if aut_splited[-1] == '':
                author_list[i] = '%0D%0A'+ aut_splited[0]
            else:
                author_list[i] = '%0D%0A'+'%2C+'.join(aut_splited)
        author = faut + ''.join(author_list)

        url = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
              '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
              '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
              '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
              '&ned_query=YES&adsobj_query=YES&aut_logic=AND&obj_logic=OR' \
              '&author=%s' \
              '&object=&start_mon=&start_year=%s&end_mon=&end_year=%s' \
              '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
              '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
              '&end_entry_mon=&end_entry_year=&min_score=' \
              '&sort=CITATIONS&data_type=SHORT&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
              '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
              '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (author, year[0], year[1])
    elif type == 'j':
        journal, year, volume, page = prmt
        url = "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?version=1&warnings=YES&partial_bibcd=YES&sort=BIBCODE" \
              "&db_key=ALL&bibstem=%s&year=%s&volume=%s&page=%s&nr_to_return=200&start_nr=1" % (journal, year, volume, page)
    tik = time.time()
    print 'loading...'
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read()
    try:
        pattern1 = re.compile('</h3>(.*?)<h4>', re.S)
        match = re.search(pattern1, content)
        content_range = match.group(0)
    except:
        print '\033[0;31;48m Retrived no result \033[0m'
        return 1

    pattern2 = re.compile('nowrap>(.*?)colspan=6', re.S)
    items = re.findall(pattern2, content_range)
    tok = time.time()

    print 'retrieved in \033[0;31;48m %1.2f \033[0m sec' % (tok-tik)
    if type == 'a':
        print "\033[0;33;48mnum\033[0m \033[0;31;48mcit\033[0m date"
    for idx, _ in enumerate(items):
        p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)<', re.S)
        elements = re.findall(p, _)
        if not elements:
            continue
        num, cit, mm, yyyy, files, authors, title = elements[0]
        num = int(num)

        authors = authors.replace('&#160;', ' ')
        if idx > 0:
            print
        print "\033[0;33;48m %s\033[0m" % num, "\033[0;31;48m %s\033[0m" % cit, '%s-%s' % (yyyy, mm)
        print "\033[0;34;48m %s\033[0m" % authors
        print "\033[0;32;48m %s\033[0m" % title

        try:
            pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
            ele = re.findall(pf, files)
            F = ele[0]
            F = F.replace('&#160;', ' ')
            F = F.replace('#38', 'amp')
            print "\033[0;36;48m F:\033[0m", F
        except:
            try:
                pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                ele = re.findall(pf, files)
                E = ele[0]
                E = E.replace('&#160;', ' ')
                E = E.replace('#38', 'amp')
                print "\033[0;32;48m E:\033[0m", E
            except:
                try:
                    pf = re.compile('href="([^"]*?type=PREPRINT)"', re.S)
                    ele = re.findall(pf, files)
                    X = ele[0]
                    X = X.replace('&#160;', ' ')
                    X = X.replace('#38', 'amp')
                    print "\033[0;31;48m X:\033[0m", X
                except:
                    pass

        if num % 5 == 0 and num != 0 and num < len(items):
            order = raw_input('%d entries in total, continue?' % len(items))
            print order
            if order == '':
                continue
            elif order == 'exit'[:len(order)] or order == 'quit'[:len(order)] or order == '^[':
                break
            else:
                continue

    print
    print url
    return 1


def get_ainfo():
    try:
        print "\033[0;34;48m Search by author and year:\033[0m"
        a_list = list()
        fauthor=''
        while True:
            get = raw_input('author \033[0;32;48m >>> \033[0m ')
            if get == '':
                break
            if get == 'exit'[:len(get)] or get == 'quit'[:len(get)]:
                return 1
            if get == '\x1b[A':
                a_list.pop()
                continue
            try:
                int(get[0])
                year = get.split('-')
            except:
                if get[0] == '^':
                    fauthor = ''.join(get[1:].split(' '))
                else:
                    a_list.append(''.join(get.split(' ')))

        if len(year) == 1:
            year *= 2

        scrap('a', (fauthor, a_list, year))
    except:
        return 1


def get_jinfo():
        print "\033[0;34;48m Search by publications:\033[0m"
        journal = raw_input("journal \033[0;32;48m >>> \033[0m ")
        if (journal == 'exit'[:len(journal)] or journal == 'quit'[:len(journal)]) and len(journal) > 0:
            return 1
        year = raw_input("year \033[0;32;48m >>> \033[0m")
        if (year == 'exit'[:len(year)] or year == 'quit'[:len(year)]) and len(year)>0:
            return 1
        volume = raw_input('volume \033[0;32;48m >>> \033[0m ')
        if (volume == 'exit'[:len(volume)] or volume == 'quit'[:len(volume)]) and len(volume) > 0:
            return 1
        page = raw_input('page \033[0;32;48m >>> \033[0m ')
        if (page == 'exit'[:len(page)] or page == 'quit'[:len(page)]) and len(page) > 0:
            return 1
        scrap('j', (journal, year, volume, page))


def standby(order):
    if order == '':
        standby(raw_input("\033[0;32;48m >>> \033[0m"))
    else:
        if (order == 'exit'[:len(order)] or order == 'quit'[:len(order)]) and len(order) > 0:
            sys.exit(0)
        try:
            if order == 'author'[:len(order)] and len(order) > 0:
                get_ainfo()
            elif order == 'journal'[:len(order)] and len(order) > 0:
                get_jinfo()
            else:
                prmt = str(order)
                prmt = prmt.replace('etal', ' ')
                prmt = prmt.replace('et al.,', ' ')
                prmt = prmt.replace('et al.', ' ')
                prmt = prmt.replace('et al,', ' ')
                prmt = prmt.replace('et al', ' ')

                prmt = prmt.replace('&', ' ')
                prmt = prmt.replace(',', ' ')
                p = re.compile('(.*?)\(?(\d{4})\)?', re.S)
                authors, year = re.findall(p, prmt)[0]
                authors = authors.split(' ')
                while True:
                    try:
                        authors.remove('')
                    except:
                        break
                year = [''.join(year)]
                scrap('a', (authors[0], authors[1:], year*2))
        except:
            print '\033[0;31;48m Unrecgonized command: %s \033[0m' % order
        standby(raw_input("\033[0;32;48m >>> \033[0m"))


if __name__ == '__main__':
    print "\033[0;31;48m This is the command line tool for SAO/NASA Astronomical Data System, version 1.0.5. \033[0m"
    print "User experiment is optimized with iterm2"
    print "Latest update on Oct-05-2017"
    # print "\033[0;32;48m Designed and maintained by Yunyang Li \033[0m"
    print "type a(uthor) for the (default) author-and-year based search (Last name, First name) or j(ournal) for a publication specified search"
    print "Alternatively, type the citation for a quick search: e.g., Li, et al., (2017)"
    print
    if len(sys.argv) == 1:
        standby(raw_input("\033[0;32;48m >>> \033[0m"))
    else:
        standby(sys.argv[1])
