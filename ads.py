# coding: utf-8
from __future__ import print_function
import re
import urllib
import time
import sys
from multiprocessing import Pool
import pyperclip
import copy
from HTMLParser import HTMLParser
import unicodedata
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import numpy as np
import time



def get_content(url):
    response = urllib.urlopen(url)
    content = response.read()
    return content


def scrap_a(fauthor, author_list, year, exact='NO', direct=False):
    if fauthor.find(',') == -1 and fauthor.find(' ') >= 0 and direct is False:
        spl_lst = fauthor.split(' ')
        while True:
            try:
                spl_lst.remove('')
            except ValueError:
                break
        faut = spl_lst[-1] + ', ' + ' '.join(spl_lst[:-1])
    faut = '%2C'.join(fauthor.split(','))
    faut = '+'.join(faut.split(' '))
    if faut != '':
        faut = '%5E' + faut
    for i, aut in enumerate(author_list):
        if (aut.find(',') == -1 and aut.find(' ') >= 0):
            spl_lst = aut.split(' ')
            while True:
                try:
                    spl_lst.remove('')
                except ValueError:
                    break
            author_list[i] = spl_lst[-1].replace('.', '') + ', ' + ' '.join(spl_lst[:-1])
        else:
            author_list[i] = aut.replace('.,', ',')
    for i, aut in enumerate(author_list):
        aut_splited = aut.split(',')
        if aut_splited[-1] == '':
            author_list[i] = '%0D%0A' + aut_splited[0]
        else:
            temp = aut.replace(' ', '+')
            temp = temp.replace(',', '%2C')
            author_list[i] = '%0D%0A' + temp
    author = faut + ''.join(author_list)
    input_author = copy.deepcopy(author)
    input_author = input_author.replace('%5E', '')
    input_author = input_author.replace('%0D%0A', '; ')
    input_author = input_author.replace('%2C+', ', ')
    input_author = input_author.replace('+', ' ')
    input_author = input_author.replace('%2C', ', ')
    input_author = input_author.split('; ')
    if input_author[0] == '':
        input_author = input_author[1:]
    for idx, a in enumerate(input_author):
        ap = a.split(' ')
        while True:
            try:
                ap.remove('')
            except ValueError:
                break
        input_author[idx] = ' '.join(ap)
        input_author[idx] = input_author[idx].replace(' ', '')
        input_author[idx] = input_author[idx].replace(',', ', ')
        if input_author[idx][-1]==',':
            input_author[idx]=input_author[idx][:-1]
    
    
    url = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
          '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
          '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
          '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
          '&ned_query=YES&adsobj_query=YES&aut_xct=%s&aut_logic=AND&obj_logic=OR' \
          '&author=%s' \
          '&object=&start_mon=&start_year=%s&end_mon=&end_year=%s' \
          '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
          '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
          '&end_entry_mon=&end_entry_year=&min_score=' \
          '&sort=CITATIONS&data_type=%s&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
          '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
          '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (exact, author, year[0], year[1], 'SHORT')

    url_bib = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
              '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
              '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
              '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
              '&ned_query=YES&adsobj_query=YES&aut_xct=%s&aut_logic=AND&obj_logic=OR' \
              '&author=%s' \
              '&object=&start_mon=&start_year=%s&end_mon=&end_year=%s' \
              '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
              '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
              '&end_entry_mon=&end_entry_year=&min_score=' \
              '&sort=CITATIONS&data_type=%s&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
              '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
              '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (exact, author, year[0], year[1], 'BIBTEX')

    tik = time.time()
    if exact == 'YES':
        print('\033[1;35;48m Exactly\033[0m looking for:', end=' ')
    else:
        print('\033[1;32;48m Fuzzily\033[0m looking for:', end=' ')
    if len(input_author)>1:
        print(*input_author[:-1], sep='; ', end=' and ')
    print(*input_author[-1:], sep='')
    print(' loading...')
    p = Pool(processes=2)

    results = p.map(get_content, (url, url_bib))
    p.close()
    p.join()
    content, content_bib = results
    try:
        pattern1 = re.compile('</h3>(.*?)<h4>', re.S)
        match = re.search(pattern1, content)
        content_range = match.group(0)

        pattern_bib = re.compile('(@[\w]*?{.*?}\n})', re.S)
        items_bib = re.findall(pattern_bib, content_bib)

    except:
        print('\033[0;31;48m Retrived no result \033[0m')
        return 1
    try:
        tot = int(re.findall(re.compile('Total citations: <strong>(\d*?)</strong>', re.S), content_range)[0])
    except:
        tot = 0

    pattern2 = re.compile('nowrap>(.*?)colspan=6', re.S)
    items = re.findall(pattern2, content_range)
    tok = time.time()
    print(' retrieved in \033[0;31;48m %1.2f \033[0m sec' % (tok - tik))

    def inner_loop(p):
        if p is True:
            print(' %d' % len(items), end=',')
        order = raw_input(' continue\033[0;32;48m >>> \033[0m')
        orderlist.append(order)
        try:
            idx = int(order)
            pyperclip.copy(items_bib[idx-1])
            print("\033[0;33;48m citation of %d is copied to clipboard \033[0m" % idx)
            return inner_loop(False)
        except ValueError:
            if order == '':
                return 0
            elif order == 'url'[:len(order)]:
                print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % url)
                return inner_loop(False)
            elif order == 'stat'[:len(order)]:
                plot_statistic()
                return inner_loop(False)
            elif order == 'exit'[:len(order)] or order == '^[':
                return 1
            elif order == 'quit'[:len(order)]:
                os._exit(0)
            else:
                print('\033[0;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
                return 0

    def get_hindex():
        for idx, _ in enumerate(items):
            p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000', re.S)
            elements = re.findall(p, _)
            if not elements:
                continue
            num, cit = elements[0]
            if int(num) > int(cit):
                return int(num)-1
        return '> %d' % (int(num))

    def plot_statistic():

        year_list = []
        cite_list = []
        nsph_list = []
        ns_list = []
        for idx, _ in enumerate(items):
            p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)<',re.S)
            elements = re.findall(p, _)
            if not elements:
                continue
            num, cit, mm, yyyy, files, authors, title = elements[0]

            try:
                pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
                ele = re.findall(pf, files)
                F = ele[0]
                F = F.replace('&#160;', ' ')
                F = F.replace('#38', 'amp')
                F = F.replace('%26', '&')
                pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                j = re.findall(pj, F)[0]
                if j == 'Natur' or j == 'Sci' or j == 'ARA&A':
                    nsph_list.append(int(yyyy))
                    ns_list.append(int(yyyy))
                if j[0:4] == 'PhRv':
                    nsph_list.append(int(yyyy))
                year_list.append(int(yyyy))
                cite_list.append(int(cit))
            except:
                try:
                    pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                    ele = re.findall(pf, files)
                    F = ele[0]
                    F = F.replace('&#160;', ' ')
                    F = F.replace('#38', 'amp')
                    F = F.replace('%26', '&')
                    pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                    j = re.findall(pj, F)[0]
                    if j == 'Natur' or j == 'Sci' or j == 'ARA&A':
                        nsph_list.append(int(yyyy))
                        ns_list.append(int(yyyy))
                    if j[0:4] == 'PhRv':
                        nsph_list.append(int(yyyy))
                    year_list.append(int(yyyy))
                    cite_list.append(int(cit))
                except:
                    try:
                        pf = re.compile('arXiv(\d\d\d\d)\.*(\d*).*?type=PREPRINT', re.S)
                        ele = re.findall(pf, files)
                        if ele[0]:
                            year_list.append(int(yyyy))
                            cite_list.append(int(cit))
                    except:
                        pass


        year_list = np.array(year_list)
        cite_list = np.array(cite_list)
        idx = np.argsort(year_list)
        year_list = year_list[idx]
        cite_list = cite_list[idx]

        minyear = year_list[0]
        maxyear = year_list[-1]
        year_sq = np.arange(minyear, maxyear+1)
        cit_sq = np.zeros(len(year_sq))
        num_sq = np.zeros(len(year_sq))
        for idx, y in enumerate(year_list):
            cit_sq[y-minyear] += cite_list[idx]
            num_sq[y-minyear] += 1
        plt.figure(figsize=(30, 9))
        num_plot = host_subplot(111)
        cit_plot = num_plot.twinx()
        avg_cit = np.array([cit_sq[idx]/num_sq[idx] if num_sq[idx] > 0 else 0 for idx in np.arange(len(num_sq))])
        cit_plot.plot(year_sq, avg_cit, color='orange', lw=3)
        cit_plot.scatter(year_sq, avg_cit, color='orange', s=60)
        idx = np.argmax(avg_cit)
        _ = avg_cit[idx]
        cit_plot.scatter(year_sq[idx], _, s=100, color='orange')
        cit_plot.text(x=year_sq[idx], y=_*1.05, s='%d' % _, color='white', va='bottom', fontsize=20, ha='center')
        ab = num_plot.hist(year_list, bins=maxyear-minyear+1, range=(minyear-(1./2), maxyear+1./2), color=(45./255, 120./255, 225./255))
        num_plot.hist(nsph_list, bins=maxyear - minyear + 1, range=(minyear - (1./2), maxyear + 1./2), color='yellow')
        num_plot.hist(ns_list, bins=maxyear - minyear + 1, range=(minyear - (1./2), maxyear + 1./2), color='green')
        a = ab[0]
        b = ab[1]
        idx = np.argmax(a)
        _ = a[idx]
        num_plot.text(x=(b[idx]+b[idx+1])/2, y=_*1.05, s='%d' % _, color='white', fontsize=20, ha='center')
        font = {'color': 'white', 'size': 20}

        num_plot.set_ylim(0, )
        cit_plot.set_ylim(0, )

        if max(avg_cit) > 800:
            cit_plot.set_yticks([100, 200, 500])
            cit_plot.set_yticklabels([100, 200, 500], fontdict={'color': 'orange', 'size': 20})
        else:
            cit_plot.set_yticks([10, 50, 100, 200])
            cit_plot.set_yticklabels([10, 50, 100, 200], fontdict={'color': 'orange', 'size': 20})

        num_plot.set_yticks([5, 10])
        num_plot.set_yticklabels([5, 10], fontdict={'color': (45./255, 120./255, 225./255), 'size': 20})
        thisyear = int(time.localtime().tm_year)
        yearticks = list(np.arange(1950, thisyear, 10))
        if thisyear % 10 > 0:
            yearticks.append(thisyear)
        if year_list[0] % 10 > 0:
            yearticks.append(year_list[0])
        num_plot.set_xticks(yearticks)
        num_plot.set_xticklabels(yearticks, fontdict=font)
        plt.xlim(year_list[0]-0.5, thisyear+0.5)
        num_plot.spines['top'].set_color('none')
        num_plot.spines['bottom'].set_color('none')
        num_plot.spines['left'].set_color('none')
        num_plot.spines['right'].set_color('none')

        cit_plot.spines['top'].set_color('none')
        cit_plot.spines['bottom'].set_color('none')
        cit_plot.spines['left'].set_color('none')
        cit_plot.spines['right'].set_color('none')

        # cit_plot.axis('off')
        # num_plot.axis('off')
        plt.savefig('/Users/liyunyang/Documents/Work/ADS/temp.eps', transparent=True)
        os.system('imgcat ~/Documents/Work/ADS/temp.eps')
        if os.path.exists('/Users/liyunyang/Documents/Work/ADS/temp.eps') is True:
            os.system('rm /Users/liyunyang/Documents/Work/ADS/temp.eps')

    if len(author_list) == 1 and fauthor == '':
        print("\033[0;33;48m H-index = %s \033[0m" % get_hindex())
        print("\033[0;33;48m Total Cit = %s \033[0m" % tot)
        if year == ['1900', '2100']:
            response = inner_loop(False)
            if response == 0:
                pass
            elif response == 1:
                return 1
        else:
            pass
    else:
        print("\033[0;33;48m Total Cit = %s \033[0m" % tot)
    print("\033[0;33;48m num\033[0m \033[0;31;48mcit\033[0m date")

    def check_exist(aut):
        for inp_aut in input_author:
            inp_aut_c = inp_aut.title()
            inp_aut_c = unicodedata.normalize('NFKD', h.unescape(unicode(inp_aut_c, 'utf-8'))).encode('ASCII', 'ignore')
            aut = unicodedata.normalize('NFKD', h.unescape(unicode(aut,'utf-8'))).encode('ASCII', 'ignore')
            
            if aut[:len(inp_aut)] == inp_aut_c or aut[:len(inp_aut)] == inp_aut:
                return 1
            else:
                try:
                    idx = aut.find(',')
                    lim = min(idx+3, min(len(aut), len(inp_aut_c)))
                    if aut[:lim] == inp_aut_c[:lim]:
                        return 1
                except:
                    continue
        return 0


    for idx, _ in enumerate(items):
        p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)<', re.S)
        elements = re.findall(p, _)
        if not elements:
            continue
        num, cit, mm, yyyy, files, authors, title = elements[0]
        conum = 0
        try:
            pp = re.compile('<span style="color: red">and (\d*?) coauthors', re.S)
            conum = int(re.findall(pp, _)[0])

        except:
            pass
        num = int(num)
        authors = authors.replace('&#160;', ' ')
        if idx > 0:
            # print()
            pass
        print("\033[0;33;48m  %s \033[0m" % num, end='')
        print("\033[0;31;48m  %s \033[0m" % cit, end='')
        print("%s-%s" % (yyyy, mm))
        author_split = authors.split('; ')

        exist_print = 0
        for idx, aut in enumerate(author_split):
            toprint = h.unescape(aut)
            if idx == 0:
                print(" ", end='')
            if check_exist(aut):
                print("\033[1;35;48m%s\033[0m" % toprint, end='; ' if idx < len(author_split)-1 else '')
                if idx < len(author_split)-1:
                    exist_print += 1
            else:
                print("\033[0;34;48m%s\033[0m" % toprint, end='; ' if idx < len(author_split)-1 else '')
            if exist_print > len(input_author):
                exist_print = len(input_author)
            if aut == '':
                if exist_print == len(input_author):
                    print("etc.(%d)" % conum, end='')
                else:
                    print("\033[1;35;48metc.\033[0m(\033[1;35;48m%d\033[0m/%d)" % (len(input_author)-exist_print, conum), end='')

        print("\033[0;34;48m \033[0m")
        print("\033[0;32;48m %s \033[0m" % h.unescape(title))

        try:
            pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
            ele = re.findall(pf, files)
            F = ele[0]
            F = F.replace('&#160;', ' ')
            F = F.replace('#38', 'amp')
            F = F.replace('%26', '&')
            pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
            j = re.findall(pj, F)[0]
            if j == 'Natur': j='Nature'
            if j == 'Sci': j='Science'
            print(' ', end='')
            print(h.unescape(j), end=': ')
            print("\033[1;30;48m%s\033[0m" % F)

        except:
            try:
                pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                ele = re.findall(pf, files)
                E = ele[0]
                E = E.replace('&#160;', ' ')
                E = E.replace('#38', 'amp')
                E = E.replace('%26', '&')
                pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                j = re.findall(pj, E)[0]
                if j == 'Natur': j='Nature'
                if j == 'Sci': j='Science'
                print(' ', end='')
                print(h.unescape(j), end=': ')
                print("\033[1;30;48m%s\033[0m" % E)

            except:
                try:
                    pf = re.compile('arXiv(\d\d\d\d)\.*(\d*).*?type=PREPRINT', re.S)
                    ele = re.findall(pf, files)
                    a, b = ele[0]
                    X = "https://arxiv.org/pdf/%s.%s.pdf" % (a, b)
                    print("\033[0;31;48m X: \033[0m\033[1;30;48m%s\033[0m" % X)
                except:
                    pass

        if num % 5 == 0 and num != 0 and num < len(items):
            response = inner_loop(True)
            if response == 0:
                continue
            if response == 1:
                break
        if num == len(items):
            while True:
                if inner_loop(False) == 1:
                    break
    print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m"% url)
    return 1


def scrap_j(journal, year, volume, page):

    def get_citation(faut, author_list, year, mm):

        faut = faut.replace(' ', '+')
        faut = faut.replace(',', '%2C')
        faut = '%5E' + faut
        for i, aut in enumerate(author_list):
            temp = aut.replace(' ', '+')
            temp = temp.replace(',', '%2C')
            author_list[i] = '%0D%0A' + temp

        author = faut + ''.join(author_list)

        url_bib = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
                  '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
                  '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
                  '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
                  '&ned_query=YES&adsobj_query=YES&aut_logic=AND&obj_logic=OR' \
                  '&author=%s' \
                  '&object=&start_mon=%s&start_year=%s&end_mon=%s&end_year=%s' \
                  '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=100&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
                  '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
                  '&end_entry_mon=&end_entry_year=&min_score=' \
                  '&sort=CITATIONS&data_type=%s&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
                  '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
                  '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (author, mm, year, mm, year, 'BIBTEX')

        content_bib = get_content(url_bib)
        pattern_bib = re.compile('(@[\w]*?{.*?}\n})', re.S)
        items_bib = re.findall(pattern_bib, content_bib)
        return items_bib[0]

    url = "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?version=1&warnings=YES&partial_bibcd=YES&sort=BIBCODE" \
          "&db_key=ALL&bibstem=%s&year=%s&volume=%s&page=%s&nr_to_return=100&start_nr=1" % (journal, year, volume, page)
    tik = time.time()
    print(' loading...')
    content = get_content(url)

    try:
        pattern1 = re.compile('</h3>(.*?)<h4>', re.S)
        match = re.search(pattern1, content)
        content_range = match.group(0)

    except:
        print('\033[0;31;48m Retrived no result \033[0m')
        return 1

    pattern2 = re.compile('nowrap>(.*?)colspan=6', re.S)
    items = re.findall(pattern2, content_range)
    tok = time.time()

    print('retrieved in \033[0;31;48m %1.2f \033[0m sec' % (tok - tik))
    print("\033[0;33;48m num\033[0m  date")

    def inner_loop(p):
        if p is True:
            print(' %d' % len(items), end=',')
        order = raw_input(' continue\033[0;32;48m >>> \033[0m')
        orderlist.append(order)
        try:
            idx = int(order)
            authors, title, yyyy, mm = entries[idx-1]
            for i, a in enumerate(authors):
                if '&#' in a:
                    temp = a.split(',')[0]
                    if '&#' in temp:
                        temp = ''
                    authors[i] = temp
            while True:
                try:
                    authors.remove('')
                except ValueError:
                    break
            print(authors)
            fauthor = authors[0]
            authors = authors[1:]
            print('getting citation...')
            pyperclip.copy(get_citation(fauthor, authors, yyyy, mm))
            print("\033[0;33;48m citation of %d is copied to clipboard \033[0m" % idx)
            return inner_loop(False)
        except ValueError:
            if order == '':
                return 0
            elif order == 'url'[:len(order)]:
                print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % url)
                return inner_loop(False)
            elif order == 'exit'[:len(order)] or order == '^[':
                return 1
            elif order == 'quit'[:len(order)]:
                os._exit(0)
            else:
                print('\033[0;31;48m Unrecgonized command: %s \033[0m'%orderlist[-1])
                return 0

    entries = list()
    for idx, _ in enumerate(items):
        p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)<', re.S)
        elements = re.findall(p, _)
        if not elements:
            continue
        num, cit, mm, yyyy, files, authors, title = elements[0]
        num = int(num)
        authors = authors.replace('&#160;', ' ')
        if idx > 0:
            # print()
            pass
        print("\033[0;33;48m %s \033[0m" % num, ' %s-%s' % (yyyy, mm))
        author_split = authors.split('; ')

        for idx, aut in enumerate(author_split):
            toprint = h.unescape(aut)
            if idx == 0:
                print(" ", end='')
            print("\033[0;34;48m%s\033[0m" % toprint, end='; ' if idx<len(author_split)-1 else '')
            if aut == '':
                print("etc.", end='')
        print("\033[0;34;48m \033[0m")
        print("\033[0;32;48m %s \033[0m" % h.unescape(title))
        entries.append([authors.split('; '), title, yyyy, mm])
        try:
            pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
            ele = re.findall(pf, files)
            F = ele[0]
            F = F.replace('&#160;', ' ')
            F = F.replace('#38', 'amp')
            F = F.replace('%26', '&')
            pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
            j = re.findall(pj, F)[0]
            if j == 'Natur': j='Nature'
            if j == 'Sci': j='Science'
            print(' ', end='')
            print(h.unescape(j), end=': ')
            print("\033[1;30;48m%s\033[0m" % F)

        except:
            try:
                pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                ele = re.findall(pf, files)
                E = ele[0]
                E = E.replace('&#160;', ' ')
                E = E.replace('#38', 'amp')
                E = E.replace('%26', '&')
                pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                j = re.findall(pj, E)[0]
                if j == 'Natur': j='Nature'
                if j == 'Sci': j='Science'
                print(' ', end='')
                print(h.unescape(j), end=': ')
                print("\033[1;30;48m%s\033[0m" % E)
            except:
                try:
                    pf = re.compile('href="([^"]*?type=PREPRINT)"', re.S)
                    ele = re.findall(pf, files)
                    X = ele[0]
                    X = X.replace('&#160;', ' ')
                    X = X.replace('#38', 'amp')
                    print("\033[0;31;48m X:\033[0m\033[1;30;48m%s\033[0m" % X)
                except:
                    pass

        if num % 5 == 0 and num != 0 and num < len(items):
            response = inner_loop(True)
            if response == 0:
                continue
            if response == 1:
                break
        if num == len(items):
            while True:
                if inner_loop(False) == 1:
                    break
    print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % url)
    return 1


def scrap_arxiv(id):
    url = "https://arxiv.org/abs/%s" % id
    url_pdf = "https://arxiv.org/pdf/%s.pdf" % id
    print("\033[0;31;48m X:\033[0m\033[1;30;48m%s\033[0m" % url_pdf)

    def to_author_search():
        content1 = get_content(url)
        pattern1 = re.compile('Authors:</span>.*?</div>', re.S)
        match = re.search(pattern1, content1)
        content_range = match.group(0)

        pattern_name = re.compile('">(.*?)</a>', re.S)
        names = re.findall(pattern_name, content_range)
        for i, n in enumerate(names):
            n_split = n.split(' ')
            if len(n_split) >= 3 and (n_split[-3] == 'Van' and n_split[-2] == 'der') or (n_split[-3] == 'Van' and n_split[-2] == 'den'):
                last = ' '.join(n_split[-3:]) + ','
                first = n_split[:-3]
            elif len(n_split) >= 2 and (n_split[-2] == 'Le' or n_split[-2] == 'De' or n_split[-2] == 'Van' or n_split[-2] == 'Von'):
                last = ' '.join(n_split[-2:]) + ','
                first = n_split[:-2]
            else:
                last = n_split[-1]+','
                first = n_split[:-1]

            n_comb = last + ' '.join(first)
            temp = n_comb
            if '&#' in n_comb:
                temp = n_comb.split(',')[0]
                if '&#' in temp:
                    temp = ''
            names[i] = temp
        while True:
            try:
                names.remove('')
            except ValueError:
                break

        fauthor = names[0]
        authors = names[1:8]
        yy = int(id[:2])
        year = [str(2000+yy)]*2
        scrap_a(fauthor, authors, year)

    def inner_loop():
        order = raw_input(' continue\033[0;32;48m >>> \033[0m')
        orderlist.append(order)
        if order == '':
            return 0
        elif order == 'ads'[:len(order)]:
            to_author_search()
            return 1
        elif order == 'url'[:len(order)]:
            print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % url)
            return inner_loop()
        elif order == 'exit'[:len(order)] or order == '^[':
            return 1
        elif order == 'quit'[:len(order)]:
            os._exit(0)
        else:
            print('\033[0;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
            return 0

    while True:
        if inner_loop() == 1:
            break
    return 1


def get_ainfo():
    def format(s):
        splited = s.split(' ')
        while True:
            try:
                splited.remove('')
            except ValueError:
                break
        return ' '.join(splited)

    exact = 'NO'

    try:
        print("\033[0;34;48m Search by author and year:\033[0m")
        a_list = list()
        fauthor=''
        year = ['1900', '2100']
        while True:
            get = raw_input(' author \033[0;32;48m >>> \033[0m ')
            orderlist.append(get)
            if get.find('!') >= 0:
                get = get.replace('!', '')
                exact = 'YES'
            if get == '':
                break
            if get == 'exit'[:len(get)]:
                return 1
            if get == 'quit'[:len(get)]:
                os._exit(0)
            if get == '\x1b[A':
                a_list.pop()
                continue
            else:
                try:
                    int(get[0])
                    year = get.split('-')
                except:
                    if get[0] == '^':
                        fauthor = format(get[1:])
                    else:
                        a_list.append(format(get))
        if len(year) == 1:
            year *= 2
        if fauthor == '' and len(a_list) == 0:
            return 1
        scrap_a(fauthor, a_list, year, exact)

    except:
        return 1


def get_jinfo():
        print("\033[0;34;48m Search by journal:\033[0m")
        print(" hints: \033[1;35;48m ApJ\033[0m; \033[1;35;48m ApJS\033[0m; \033[1;35;48m MNRAS\033[0m; \033[1;35;48m A&A\033[0m; \033[1;35;48m ARA&A\033[0m; \033[1;35;48m Natur\033[0m;\033[1;35;48m NatAs\033[0m; \033[1;35;48m NatPh\033[0m; \033[1;35;48m Sci\033[0m; \033[1;35;48m PhRv(ABCDEFLMP)\033[0m; \033[1;35;48m A&ARv\033[0m; \033[1;35;48m RAA\033[0m")
        journal = raw_input(" journal \033[0;32;48m >>> \033[0m ")
        journal = journal.replace('&', '%26')
        orderlist.append(journal)
        if journal == 'exit'[:len(journal)] and len(journal) > 0:
            return 1
        if journal == 'quit'[:len(journal)] and len(journal) > 0:
            os._exit(0)

        year = raw_input(" year \033[0;32;48m >>> \033[0m")
        orderlist.append(year)
        if year == 'exit'[:len(year)] and len(year) > 0:
            return 1
        if year == 'quit'[:len(year)] and len(year) > 0:
            os._exit(0)

        volume = raw_input(' volume \033[0;32;48m >>> \033[0m ')
        orderlist.append(volume)
        if volume == 'exit'[:len(volume)]  and len(volume) > 0:
            return 1
        if volume == 'quit'[:len(volume)] and len(volume) > 0:
            os._exit(0)

        page = raw_input(' page \033[0;32;48m >>> \033[0m ')
        orderlist.append(page)
        if page == 'exit'[:len(page)] and len(page) > 0:
            return 1
        if page == 'quit'[:len(page)] and len(page) > 0:
            os._exit(0)
        scrap_j(journal, year, volume, page)


def standby(order):
    orderlist.append(order)
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
            elif order == 'help'[:len(order)] and len(order) > 0:
                help()
            else:
                prmt = str(order)
                try:
                    splited = prmt.split('.')
                    a = splited[0].replace(' ', '')
                    b = splited[1].replace(' ', '')
                    a = int(a)
                    b = int(b)
                    scrap_arxiv('%d.%d' % (a, b))
                except:
                    try:
                        p = re.compile('(.*?)\(?(\d{4})\)?', re.S)
                        prmt, year = re.findall(p, prmt)[0]
                        prmt = prmt.replace('etal', '')
                        prmt = prmt.replace('et.al.', '')
                        prmt = prmt.replace('et. al.', '')
                        prmt = prmt.replace('et al.,', '')
                        prmt = prmt.replace('et al.', '')
                        prmt = prmt.replace('et al,', '')
                        prmt = prmt.replace('et al', '')

                        prmt = prmt.replace('&', ';')
                        prmt = prmt.replace(' and ', ';')
                        prmt = prmt.replace(',', ';')
                        authors = prmt.split(';')
                        while True:
                            try:
                                authors.remove('')
                            except ValueError:
                                break
                        year = [''.join(year)]
                        scrap_a(authors[0], authors[1:], year*2, direct=True)
                    except:

                        if prmt.find('!') >= 0:
                            prmt = prmt.replace('!', '')
                            exact = 'YES'
                        else:
                            exact = 'NO'
                        authors = prmt.split(';')
                        year = ['1900', '2100']
                        scrap_a('', authors, year, exact)


        except:
            print('\033[0;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
        standby(raw_input("\033[0;32;48m >>> \033[0m"))


def help():
    print("Type the citation for a quick search (default): e.g., Li, et al., (2017).")
    print("Type a(uthor) for the author-and-year based search (Last name, First name).")
    print("Type j(ournal) for a publication specified search.")
    


if __name__ == '__main__':
    h = HTMLParser()
    # print("\033[0;31;48m This is the command line tool for SAO/NASA Astronomical Data System, version 3.2 \033[0m")
    # print(" User experience is optimized with iTerm2")
    # print(" Latest update on Nov-18-2017")
    # print(" Type h(elp) for instructions.")
    os.system('imgcat ~/Documents/Work/ADS/ads_logo_left.png')
    orderlist = list()
    if len(sys.argv) == 1:
        standby(raw_input("\033[0;32;48m >>> \033[0m"))
    else:
        orderlist.append(sys.argv[1])
        standby(sys.argv[1])


