from __future__ import print_function
import re
import urllib
import time
from multiprocessing import Pool
from HTMLParser import HTMLParser
import unicodedata
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import numpy as np
from wordcloud import WordCloud
from scipy import interpolate


def get_content(url):
    response = urllib.urlopen(url)
    content = response.read()
    return content


class ARecord:
    def __init__(self, input_author, num, cit, mm, yyyy, files, authors, title, conum, bib):
        self.input_author = input_author
        self.num = int(num)
        self.cit = int(cit)
        self.mm = int(mm)
        self.yyyy = int(yyyy)
        self.authors = authors
        self.author_split = authors.split('; ')
        self.title = title
        self.journal = None
        self.journal_url = None
        self.conum = conum
        self.bib = bib
        self.idx_seq = None
        try:
            pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
            ele = re.findall(pf, files)
            F = ele[0]
            F = F.replace('&#160;', ' ')
            F = F.replace('#38', 'amp')
            F = F.replace('%26', '&')
            pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
            self.journal = re.findall(pj, F)[0]
            self.journal_url = F
        except:
            try:
                pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                ele = re.findall(pf, files)
                F = ele[0]
                F = F.replace('&#160;', ' ')
                F = F.replace('#38', 'amp')
                F = F.replace('%26', '&')
                pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                self.journal = re.findall(pj, F)[0]
                self.journal_url = F

            except:
                try:
                    pf = re.compile('arXiv(\d\d\d\d)\.*(\d*).*?type=PREPRINT', re.S)
                    ele = re.findall(pf, files)
                    a, b = ele[0]
                    X = "https://arxiv.org/pdf/%s.%s.pdf" % (a, b)
                    self.journal = 'arXiv'
                    self.journal_url = X
                except:
                    pass
        if self.journal == 'Natur': self.journal = 'Nature'
        if self.journal == 'Sci': self.journal = 'Science'
        if self.check_exist(self.author_split[0]):
            self.is_first = True
        else:
            self.is_first = False

    def check_exist(self, aut):
        for inp_aut in self.input_author:
            inp_aut_c = inp_aut.title()
            inp_aut_c = unicodedata.normalize('NFKD', HTMLParser().unescape(unicode(inp_aut_c, 'utf-8'))).encode(
                'ASCII', 'ignore')
            aut = unicodedata.normalize('NFKD', HTMLParser().unescape(unicode(aut, 'utf-8'))).encode('ASCII', 'ignore')
            if aut[:len(inp_aut)] == inp_aut_c or aut[:len(inp_aut)] == inp_aut:
                return 1
            else:
                try:
                    idx = aut.find(',')
                    lim = min(idx + 3, min(len(aut), len(inp_aut_c)))
                    if aut[:lim] == inp_aut_c[:lim]:
                        return 1
                except:
                    continue
        return 0

    def display(self, seq_index):

        print("\033[0;33;48m %3d\033[0m" % int(seq_index + 1), end='')
        print("\033[0;31;48m %5d\033[0m" % int(self.cit), end=' ')
        print("%s-%02d" % (self.yyyy, int(self.mm)), end=' | ')
        if self.journal is not None:
            print('{:<5s}'.format(self.journal))
        else:
            print()

        exist_print = 0
        for idx, aut in enumerate(self.author_split):
            toprint = HTMLParser().unescape(aut)
            if idx == 0:
                print(" ", end='')
            if self.check_exist(aut):
                print("\033[1;35;48m%s\033[0m"%toprint, end='; ' if idx < len(self.author_split) - 1 else '')
                if idx < len(self.author_split) - 1:
                    exist_print += 1
            else:
                print("\033[0;34;48m%s\033[0m" % toprint, end='; ' if idx < len(self.author_split) - 1 else '')
            if exist_print > len(self.input_author):
                exist_print = len(self.input_author)
            if aut == '':
                if exist_print == len(self.input_author):
                    print("etc.(%d)" % self.conum, end='')
                else:
                    print("\033[1;35;48metc.\033[0m(\033[1;35;48m%d\033[0m/%d)" %
                          (len(self.input_author) - exist_print, self.conum), end='')

        print("\033[0;34;48m \033[0m")
        print("\033[0;32;48m %s \033[0m" % HTMLParser().unescape(self.title))
        if self.journal is not None:
            if self.journal == 'arXiv':
                print("\033[0;30;48m X: \033[0m\033[1;30;48m%s\033[0m" % self.journal_url)
            else:
                print("\033[0;30;48m %s: \033[0m\033[1;30;48m%s\033[0m" % (HTMLParser().unescape(self.journal), self.journal_url))


class ASearchResult:

    def __init__(self, first_author, author_list, year, exact='NO', direct=False):
        self.first_author = first_author
        if self.first_author is not None:
            self.all_author = [first_author] + author_list
        else:
            self.all_author = author_list
        self.author_request_str = self.get_author_request(first_author, author_list)
        self.exact = exact
        self.year = year
        self.url, self.url_bib = self.get_search_url()
        self.all_record = list()
        self.title_list = list()
        self.year_list = list()
        self.mm_list = list()
        self.cite_list = list()
        self.cite_seq_idx = list()
        self.year_seq_idx = list()
        self.time_seq_idx = list()
        self.phys_list = list()
        self.nsaa_list = list()
        self.astr_list = list()
        self.arxv_list = list()
        self.othr_list = list()
        self.f_au_list = list()
        self.retrieve_status = self.retrieve()

    def get_author_request(self, first_author, author_list):
        if first_author is None:
            request = ''
        else:
            request = '%5E' + '+'.join('%2C'.join(first_author.split(',')).split(' '))

        for _ in author_list:
            request += '%0D%0A' + '+'.join('%2C'.join(_.split(',')).split(' '))
        return request

    def get_search_url(self):
        url = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
              '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
              '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
              '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
              '&ned_query=YES&adsobj_query=YES&aut_xct=%s&aut_logic=AND&obj_logic=OR' \
              '&author=%s' \
              '&object=&start_mon=&start_year=%s&end_mon=&end_year=%s' \
              '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=300&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
              '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
              '&end_entry_mon=&end_entry_year=&min_score=' \
              '&sort=CITATIONS&data_type=%s&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
              '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
              '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (
               self.exact, self.author_request_str, self.year[0], self.year[1], 'SHORT')

        url_bib = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PRE&qform=AST&arxiv_sel' \
                  '=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat' \
                  '&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel' \
                  '=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&sim_query=YES' \
                  '&ned_query=YES&adsobj_query=YES&aut_xct=%s&aut_logic=AND&obj_logic=OR' \
                  '&author=%s' \
                  '&object=&start_mon=&start_year=%s&end_mon=&end_year=%s' \
                  '&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=300&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL' \
                  '&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=' \
                  '&end_entry_mon=&end_entry_year=&min_score=' \
                  '&sort=CITATIONS&data_type=%s&aut_syn=YES&ttl_syn=YES&txt_syn=YES' \
                  '&aut_wt=1.0&obj_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES' \
                  '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (
                   self.exact, self.author_request_str, self.year[0], self.year[1], 'BIBTEX')
        return url, url_bib

    def retrieve(self):
        tik = time.time()
        if self.exact == 'YES':
            print('\033[1;35;48m Exactly\033[0m looking for:', end=' ')
        else:
            print('\033[1;32;48m Fuzzily\033[0m looking for:', end=' ')
        if len(self.all_author) > 1:
            print(*self.all_author[:-1], sep='; ', end=' and ')
            print(*self.all_author[-1:], sep='')
            print(' loading...', end='')
        else:
            print(self.all_author[0])
            print(' loading...', end='')
        p = Pool(processes=2)
        results = p.map(get_content, (self.url, self.url_bib))
        p.close()
        p.join()
        content, content_bib = results
        print('', end='\r')
        try:
            pattern1 = re.compile('</h3>(.*?)<h4>', re.S)
            match = re.search(pattern1, content)
            content_range = match.group(0)
            pattern_bib = re.compile('(@[\w]*?{.*?}\n})', re.S)
            self.items_bib = re.findall(pattern_bib, content_bib)
        except:
            print('\033[0;31;48m Retrived no result \033[0m')
            return 1
        try:
            self.tot_cit = int(re.findall(re.compile('Total citations: <strong>(\d*?)</strong>', re.S), content_range)[0])
        except:
            self.tot_cit = 0
        pattern2 = re.compile('nowrap>(.*?)colspan=6', re.S)
        self.items = re.findall(pattern2, content_range)
        tok = time.time()
        self.reduce()
        print(' %d entries retrieved in \033[0;31;48m%1.2f\033[0m sec' % (len(self.all_record), tok - tik))
        return 0

    def reduce(self):
        for idx, _ in enumerate(self.items):
            p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)</td></tr>', re.S)
            elements = re.findall(p, _)
            if not elements:
                continue
            num, cit, mm, yyyy, files, authors, title = elements[0]
            try:
                pp = re.compile('<span style="color: red">and (\d*?) coauthors', re.S)
                conum = int(re.findall(pp, _)[0])
            except:
                conum = 0

            title = title.replace('<SUP>', '')
            title = title.replace('</SUP>', '')
            title = title.replace('<SUB>', '')
            title = title.replace('</SUB>', '')
            title = HTMLParser().unescape(title)

            self.title_list.append(title)
            self.cite_seq_idx.append(idx)
            self.time_seq_idx.append(int(yyyy) + (float(mm)-1)/12)
            new_record = ARecord(self.all_author, num, cit, mm, yyyy, files, authors.replace('&#160;', ' '), title, conum, self.items_bib[idx])

            self.all_record.append(new_record)
            if new_record.journal is not None:
                if new_record.is_first:
                    self.f_au_list.append(new_record.yyyy)
                if new_record.journal in ['Nature', 'Science', 'ARA&A']:
                    self.nsaa_list.append(new_record.yyyy)
                elif new_record.journal[0:4] == 'PhRv':
                    self.phys_list.append(new_record.yyyy)
                elif new_record.journal in ['ApJ', 'A&A', 'MNRAS', 'ApJS']:
                    self.astr_list.append(new_record.yyyy)
                elif new_record.journal == 'arXiv':
                    self.arxv_list.append(new_record.yyyy)
                else:
                    self.othr_list.append(new_record.yyyy)
                self.year_list.append(int(yyyy))
                self.cite_list.append(int(cit))
                self.mm_list.append(int(mm))

        self.year_seq_idx = np.argsort(np.array(self.year_list)*100 + np.array(self.mm_list))
        self.time_seq_idx = np.argsort(self.time_seq_idx)
        if len(self.year_list) > 0:
            self.titletext = ' '.join(self.title_list)
            self.year_list = np.array(self.year_list)
            self.cite_list = np.array(self.cite_list)

            year_y_seq = self.year_list[self.year_seq_idx]
            cite_y_seq = self.cite_list[self.year_seq_idx]
            self.minyear = min(self.year_list)
            self.maxyear = max(self.year_list)
            self.year_sq = np.arange(self.minyear, self.maxyear + 1)
            self.cit_sq = np.zeros(len(self.year_sq))
            self.num_sq = np.zeros(len(self.year_sq))

            for idx, y in enumerate(year_y_seq):
                self.cit_sq[y - self.minyear] += cite_y_seq[idx]
                self.num_sq[y - self.minyear] += 1

    def get_hindex(self):
        for idx in self.cite_seq_idx:
            if self.all_record[idx].num > self.all_record[idx].cit:
                return self.all_record[idx].num - 1
        return '> %d' % self.all_record[idx].num

    def plot_statistic(self):
        if len(self.year_list) < 1:
            return 0
        plt.figure(figsize=(30, 9))
        num_plot = host_subplot(111)
        cit_plot = num_plot.twinx()
        avg_cit = np.array([self.cit_sq[idx]/self.num_sq[idx] if self.num_sq[idx] > 0 else 0 for idx in np.arange(len(self.num_sq))])

        try:
            x_ = np.arange(self.minyear, self.maxyear + 0.05, 0.05)
            y_ = interpolate.interp1d(x=self.year_sq, y=avg_cit, kind=2)(x_)
            cit_plot.plot(x_, y_, color='orange', lw=3)
        except ValueError:
            cit_plot.plot(self.year_sq, avg_cit, color='orange', lw=3)
        cit_plot.scatter(self.year_sq, avg_cit, color='orange', s=60)
        idx = np.argmax(avg_cit)
        _ = avg_cit[idx]
        cit_plot.scatter(self.year_sq[idx], _, s=100, color='orange')
        cit_plot.text(x=self.year_sq[idx], y=_*1.05, s='%d' % _, color='white', va='bottom', fontsize=20, ha='center')

        ab = np.histogram(self.year_list, bins=self.maxyear - self.minyear + 1, range=(self.minyear - (1./2), self.maxyear+1./2))
        if self.astr_list:
            num_plot.hist(list(self.nsaa_list + self.phys_list + self.arxv_list + self.othr_list + self.astr_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color=(45./255, 120./255, 225./255), label='ApJ, ApJS, MNRAS, A&A ({:d})'.format(len(self.astr_list)))
        if self.arxv_list:
            num_plot.hist(list(self.nsaa_list + self.phys_list + self.othr_list + self.arxv_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color='red', label='arXiv ({:d})'.format(len(self.arxv_list)))
        if self.othr_list:
            num_plot.hist(list(self.nsaa_list + self.phys_list + self.othr_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color='white', label='other ({:d})'.format(len(self.othr_list)))
        if self.phys_list:
            num_plot.hist(list(self.nsaa_list + self.phys_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color='yellow', label='PhRv ({:d})'.format(len(self.phys_list)))
        if self.nsaa_list:
            num_plot.hist(list(self.nsaa_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color='green', label='Nature, Science, ARA&A ({:d})'.format(len(self.nsaa_list)))
        if self.f_au_list:
            num_plot.hist(list(self.f_au_list),
                          bins=(self.maxyear - self.minyear + 1), range=(self.minyear - (1./2), self.maxyear + 1./2),
                          color='black', histtype='step', linewidth=4, linestyle='dashed',
                          label='First-author ({:d})'.format(len(self.f_au_list)))



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
        elif max(avg_cit) > 100:
            cit_plot.set_yticks([10, 50, 100, 200])
            cit_plot.set_yticklabels([10, 50, 100, 200], fontdict={'color': 'orange', 'size': 20})
        else:
            cit_plot.set_yticks([5, 10, 20, 50])
            cit_plot.set_yticklabels([5, 10, 20, 50], fontdict={'color': 'orange', 'size': 20})

        num_plot.set_yticks([5, 10])
        num_plot.set_yticklabels([5, 10], fontdict={'color': (45./255, 120./255, 225./255), 'size': 20})
        thisyear = int(time.localtime().tm_year)
        yearticks = list(np.arange(1950, thisyear, 10))
        if thisyear % 10 > 0:
            yearticks.append(thisyear)
        if self.minyear % 10 > 0:
            yearticks.append(self.minyear)
        num_plot.set_xticks(yearticks)
        num_plot.set_xticklabels(yearticks, fontdict=font)
        plt.xlim(self.minyear-0.5, thisyear+0.5)
        num_plot.spines['top'].set_color('none')
        num_plot.spines['bottom'].set_color('none')
        num_plot.spines['left'].set_color('none')
        num_plot.spines['right'].set_color('none')

        cit_plot.spines['top'].set_color('none')
        cit_plot.spines['bottom'].set_color('none')
        cit_plot.spines['left'].set_color('none')
        cit_plot.spines['right'].set_color('none')

        legend = plt.legend(loc=2, fontsize=15)
        frame = legend.get_frame()
        plt.setp(legend.get_texts(), color='white')
        frame.set_facecolor('none')
        plt.subplots_adjust(bottom=0.05, left=0.03, right=0.97)
        plt.savefig('/Users/liyunyang/Documents/Work/ADS/temp.eps', transparent=True)
        os.system('imgcat ~/Documents/Work/ADS/temp.eps')
        if os.path.exists('/Users/liyunyang/Documents/Work/ADS/temp.eps') is True:
            os.system('rm /Users/liyunyang/Documents/Work/ADS/temp.eps')

    def plot_wordcloud(self):
        font_path = '/Library/Fonts/Optima.ttc'
        # font_path = '/System/Library/Fonts/Helvetica.dfont'
        wordcloud = WordCloud(font_path=font_path, width=1200, height=500, max_words=300, colormap='YlOrRd').generate(self.titletext)
        plt.figure(figsize=(12, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.savefig('/Users/liyunyang/Documents/Work/ADS/wctemp.png', transparent=True)
        os.system('imgcat ~/Documents/Work/ADS/wctemp.png')
        if os.path.exists('/Users/liyunyang/Documents/Work/ADS/wctemp.png') is True:
            os.system('rm /Users/liyunyang/Documents/Work/ADS/wctemp.png')


class JRecord:
    def __init__(self, num, mm, yyyy, files, authors, title):
        self.num = int(num)
        self.mm = mm
        self.yyyy = yyyy
        self.authors = authors
        self.author_split = authors.split('; ')
        self.title = title
        self.journal = None
        self.journal_url = None
        self.bib = None
        self.idx_seq = None

        try:
            pf = re.compile('href="([^"]*?type=ARTICLE)"', re.S)
            ele = re.findall(pf, files)
            F = ele[0]
            F = F.replace('&#160;', ' ')
            F = F.replace('#38', 'amp')
            F = F.replace('%26', '&')
            pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
            self.journal = re.findall(pj, F)[0]
            self.journal_url = F
        except:
            try:
                pf = re.compile('href="([^"]*?type=EJOURNAL)"', re.S)
                ele = re.findall(pf, files)
                F = ele[0]
                F = F.replace('&#160;', ' ')
                F = F.replace('#38', 'amp')
                F = F.replace('%26', '&')
                pj = re.compile('\d\d\d\d(.*?)(?:\.|\d)', re.S)
                self.journal = re.findall(pj, F)[0]
                self.journal_url = F

            except:
                try:
                    pf = re.compile('arXiv(\d\d\d\d)\.*(\d*).*?type=PREPRINT', re.S)
                    ele = re.findall(pf, files)
                    a, b = ele[0]
                    X = "https://arxiv.org/pdf/%s.%s.pdf" % (a, b)
                    self.journal = 'arXiv'
                    self.journal_url = X
                except:
                    pass

        if self.journal == 'Natur': self.journal = 'Nature'
        if self.journal == 'Sci': self.journal = 'Science'

    def get_citation(self):
        for i, a in enumerate(self.author_split):
            if '&#' in a:
                temp = a.split(',')[0]
                if '&#' in temp:
                    temp = ''
                self.author_split[i] = temp
        while True:
            try:
                self.author_split.remove('')
            except ValueError:
                break
        print(self.author_split)
        fauthor = self.author_split[0]
        author_list = self.author_split[1:]
        faut = fauthor.replace(' ', '+')
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
                  '&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1' % (author, self.mm, self.yyyy, self.mm, self.yyyy, 'BIBTEX')

        content_bib = get_content(url_bib)
        pattern_bib = re.compile('(@[\w]*?{.*?}\n})', re.S)
        items_bib = re.findall(pattern_bib, content_bib)
        self.bib = items_bib[0]

    def display(self, seq_index):
        print("\033[0;33;48m %3d \033[0m" % int(seq_index + 1), end='')
        print("%s-%02d" % (self.yyyy, int(self.mm)), end=' | ')
        if self.journal is not None:
            print('{:<5s}'.format(self.journal))
        else:
            print()
        for idx, aut in enumerate(self.author_split):
            toprint = HTMLParser().unescape(aut)
            if idx == 0:
                print(" ", end='')
            print("\033[0;34;48m%s\033[0m" % toprint, end='; ' if idx < len(self.author_split) - 1 else '')
            if aut == '':
                print("etc.", end='')
        print("\033[0;34;48m \033[0m")
        print("\033[0;32;48m %s \033[0m" % HTMLParser().unescape(self.title))
        if self.journal is not None:
            if self.journal == 'arXiv':
                print("\033[0;30;48m X: \033[0m\033[1;30;48m%s\033[0m" % self.journal_url)
            else:
                print("\033[0;30;48m %s: \033[0m\033[1;30;48m%s\033[0m" % (HTMLParser().unescape(self.journal), self.journal_url))


class JSearchResult:

    def __init__(self, journal, year, volume, page):
        self.journal = journal
        self.year = year
        self.volume = volume
        self.page = page
        self.url = "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?version=1&warnings=YES&partial_bibcd=YES&sort=BIBCODE&db_key=ALL&bibstem=%s&year=%s&volume=%s&page=%s&nr_to_return=300&start_nr=1" % (journal, year, volume, page)
        self.all_record = list()
        self.title_list = list()
        self.year_list = list()
        self.mm_list = list()
        self.year_seq_idx = list()
        self.time_seq_idx = list()
        self.retrieve_status = self.retrieve()

    def retrieve(self):
        tik = time.time()
        print(' loading...', end='')
        content = get_content(self.url)
        print('', end='\r')
        try:
            pattern1 = re.compile('</h3>(.*?)<h4>', re.S)
            match = re.search(pattern1, content)
            content_range = match.group(0)

        except:
            print('\033[0;31;48m Retrived no result \033[0m')
            return 1
        pattern2 = re.compile('nowrap>(.*?)colspan=6', re.S)
        self.items = re.findall(pattern2, content_range)
        tok = time.time()
        self.reduce()
        print(' %d entries retrieved in \033[0;31;48m%1.2f\033[0m sec' % (len(self.all_record), tok - tik))
        return 0

    def reduce(self):
        for idx, _ in enumerate(self.items):
            p = re.compile('(\d*?)</td><td.*?"baseline">(\d*?)\.000.*?"baseline">(\d\d)/(\d{4})(.*?)width="25%">(.*?)<.*?colspan=3>(.*?)<', re.S)
            elements = re.findall(p, _)
            if not elements:
                continue
            num, cit, mm, yyyy, files, authors, title = elements[0]
            num = int(num)

            title = title.replace('<SUP>', '')
            title = title.replace('</SUP>', '')
            title = title.replace('<SUB>', '')
            title = title.replace('</SUB>', '')
            title = HTMLParser().unescape(title)

            self.title_list.append(title)
            self.time_seq_idx.append(int(yyyy) + (float(mm) - 1)/12)
            new_record = JRecord(num, mm, yyyy, files, authors.replace('&#160;', ' '), title)

            self.all_record.append(new_record)
            if new_record.journal is not None:
                self.year_list.append(int(yyyy))
                self.mm_list.append(int(mm))
        self.year_seq_idx = np.argsort(np.array(self.year_list)*100 + np.array(self.mm_list))
        self.time_seq_idx = np.argsort(self.time_seq_idx)
        if len(self.year_list) > 0:
            self.titletext = ' '.join(self.title_list)
            self.year_list = np.array(self.year_list)

    def plot_wordcloud(self):
        font_path = '/Library/Fonts/Optima.ttc'
        # font_path = '/System/Library/Fonts/Helvetica.dfont'
        wordcloud = WordCloud(font_path=font_path, width=1200, height=500, max_words=300, colormap='YlOrRd').generate(self.titletext)
        plt.figure(figsize=(12, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.savefig('/Users/liyunyang/Documents/Work/ADS/wctemp.png', transparent=True)
        os.system('imgcat ~/Documents/Work/ADS/wctemp.png')
        if os.path.exists('/Users/liyunyang/Documents/Work/ADS/wctemp.png') is True:
            os.system('rm /Users/liyunyang/Documents/Work/ADS/wctemp.png')

