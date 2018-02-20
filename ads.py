# coding: utf-8
from __future__ import print_function
import re
import time
import sys
import pyperclip
import os
import dataclass as dc


def format_author(author):
    """
    :param author: a sting of name 
    :return: name in the format: "last, first"
    """
    author = re.sub('\s+', ' ', author)
    p1 = re.compile('\S.*\S', re.S)
    fullname = re.search(p1, author).group(0)
    splitted = fullname.split(',')
    if len(splitted) == 2:
        # input=last, first or last,
        lastname = re.search(p1, splitted[0]).group(0)
        firstname = re.search(p1, splitted[1]).group(0) if splitted[1] != '' else ''
    else:
        # input=first last or last
        space_splitted = splitted[0].split(' ')
        if len(space_splitted) == 1:
            # input=last
            lastname = space_splitted[0]
            firstname = ''
        else:
            # input = first last
            if len(space_splitted) >= 3 and ((space_splitted[-3] == 'Van' and space_splitted[-2] == 'der') or (space_splitted[-3] == 'Van' and space_splitted[-2] == 'den')):
                lastname = ' '.join(space_splitted[-3:])
                firstname = ' '.join(space_splitted[:-3])
            elif len(space_splitted) >= 2 and ((space_splitted[-2] == 'Le' or space_splitted[-2] == 'De' or space_splitted[-2] == 'Van' or space_splitted[-2] == 'Von')):
                lastname = ' '.join(space_splitted[-2:])
                firstname = ' '.join(space_splitted[:-2])
            else:
                lastname = space_splitted[-1]
                firstname = ' '.join(space_splitted[:-1])

    return ', '.join((lastname, firstname))


def get_sr_object(order):
    try:
        # author mode
        if order == 'author'[:len(order)] and len(order) > 0:
            sr = get_ainfo()
        # journal mode
        elif order == 'journal'[:len(order)] and len(order) > 0:
            sr = get_jinfo()
        # direct search
        else:
            # arxiv mode
            prmt = str(order)
            try:
                splited = prmt.split('.')
                a = splited[0].replace(' ', '')
                b = splited[1].replace(' ', '')
                id = '%d.%d' % (int(a), int(b))
                url = "https://arxiv.org/abs/%s" % id
                url_pdf = "https://arxiv.org/pdf/%s.pdf"%id
                print("\033[0;31;48m X: \033[0m\033[1;30;48m%s\033[0m" % url_pdf)
                sr = None
            # direct author/citation mode
            except:
                # direct citation mode
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
                    prmt = prmt.replace('(', '')
                    prmt = prmt.replace(')', '')
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
                    for idx, _ in enumerate(authors):
                        authors[idx] = format_author(_)
                    sr = dc.ASearchResult(first_author=authors[0], author_list=authors[1:], year=year*2, exact='NO')

                # direct author mode
                except:
                    if prmt.find('!') >= 0:
                        prmt = prmt.replace('!', '')
                        exact = 'YES'
                    else:
                        exact = 'NO'
                    authors = prmt.split(';')
                    for idx, _ in enumerate(authors):
                        authors[idx] = format_author(_)
                    year = ['1900', '%d' % int(time.localtime().tm_year)]
                    sr = dc.ASearchResult(first_author=None, author_list=authors, year=year, exact=exact)


    except:
        print('\033[0;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
        sr = None
    return sr


def outer_loop():
    while True:
        order = raw_input("\033[0;32;48m >>> \033[0m")
        orderlist.append(order)
        if order != '':
            break
    if (order == 'exit'[:len(order)] or order == 'quit'[:len(order)]) and len(order) > 0:
        sys.exit(0)
    elif order == 'help'[:len(order)] and len(order) > 0:
        help()
    else:
        sr = get_sr_object(order)
        if sr is None:
            pass
        else:
            inner_loop(sr)
    outer_loop()


def inner_loop(sr):
    if sr.__class__ is dc.ASearchResult:
        def scroll(scroll_order):
            if scroll_order == 'cite':
                sr.idx_seq = sr.cite_seq_idx
            if scroll_order == 'rcite':
                sr.idx_seq = sr.cite_seq_idx[::-1]
            elif scroll_order == 'year':
                sr.idx_seq = sr.year_seq_idx
            elif scroll_order == 'ryear':
                sr.idx_seq = sr.year_seq_idx[::-1]

            print("\033[0;33;48m num\033[0m \033[0;31;48mcit\033[0m date")
            for i, idx in enumerate(sr.idx_seq):
                sr.all_record[idx].display(i)
                num = i + 1
                if num % 5 == 0 and num != 0 and num < len(sr.all_record):
                    yield 0
        if len(sr.all_author) == 1 and sr.first_author is None:
            print("\033[0;33;48m H-index = %s \033[0m" % sr.get_hindex())
            print("\033[0;33;48m Total Cit = %s \033[0m" % sr.tot_cit)
        else:
            print("\033[0;33;48m Total Cit = %s \033[0m" % sr.tot_cit)
        scroller = scroll('cite')
        if len(sr.all_author) == 1 and sr.first_author is None and sr.year == ['1900', '%d' % int(time.localtime().tm_year)]:
            pass
        else:
            try:
                scroller.next()
            except:
                pass
        while True:
            order = raw_input(' continue\033[0;32;48m >>> \033[0m')
            orderlist.append(order)
            if len(order) > 0 and order[0] == 'c':
                try:
                    idx = int(order[1:])
                    pyperclip.copy(sr.all_record[sr.idx_seq[idx - 1]].bib)
                    print("\033[0;33;48m citation of %d is copied to clipboard \033[0m" % idx)
                except:
                    pass
                continue
            try:
                idx = int(order)
                j_url = sr.all_record[sr.idx_seq[idx-1]].journal_url
                print("\033[1;30;48m%s: %s\033[0m" % (sr.all_record[sr.idx_seq[idx - 1]].journal, sr.all_record[sr.idx_seq[idx - 1]].title))
                os.system("open '%s'" % j_url)
            except ValueError:
                if order == '':
                    try:
                        scroller.next()
                    except:
                        pass
                elif order == 'url'[:len(order)]:
                    print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % sr.url)
                elif order == 'stat'[:len(order)]:
                    sr.plot_statistic()
                elif order == 'wc'[:len(order)]:
                    sr.plot_wordcloud()
                elif order == 'exit'[:len(order)] or order == '^[':
                    break
                elif order == 'quit'[:len(order)]:
                    os._exit(0)
                else:
                    if_in = False
                    for _ in ['cite', 'year', 'ryear', 'rcite']:
                        if order == _[:len(order)]:
                            if_in = True
                            scroller = scroll(_)
                            try:
                                scroller.next()
                            except:
                                pass
                            break
                    if if_in is False:
                        print('\033[0 ;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
                        continue
        print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % sr.url)

    elif sr.__class__ is dc.JSearchResult:
        print(len(sr.all_record))

        def scroll(scroll_order):
            if scroll_order == 'year':
                sr.idx_seq = sr.year_seq_idx
            elif scroll_order == 'ryear':
                sr.idx_seq = sr.year_seq_idx[::-1]
            print("\033[0;33;48m num\033[0m  date")
            for i, idx in enumerate(sr.idx_seq):
                sr.all_record[idx].display(i)
                num = i + 1
                if num % 5 == 0 and num != 0 and num < len(sr.all_record):
                    yield 0

        scroller = scroll('ryear')
        try:
            scroller.next()
        except:
            pass
        while True:
            order = raw_input(' continue\033[0;32;48m >>> \033[0m')
            orderlist.append(order)
            if len(order) > 0 and order[0] == 'c':

                idx = int(order[1:])
                sr.all_record[sr.idx_seq[idx - 1]].get_citation()
                pyperclip.copy(sr.all_record[sr.idx_seq[idx - 1]].bib)
                print("\033[0;33;48m citation of %d is copied to clipboard \033[0m" % idx)


                continue
            try:
                idx = int(order)
                j_url = sr.all_record[sr.idx_seq[idx - 1]].journal_url
                print("\033[1;30;48m%s: %s\033[0m" % (sr.all_record[sr.idx_seq[idx - 1]].journal, sr.all_record[sr.idx_seq[idx - 1]].title))
                os.system("open '%s'" % j_url)
            except ValueError:
                if order == '':
                    try:
                        scroller.next()
                    except:
                        pass
                elif order == 'url'[:len(order)]:
                    print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % sr.url)
                elif order == 'wc'[:len(order)]:
                    sr.plot_wordcloud()
                elif order == 'exit'[:len(order)] or order == '^[':
                    break
                elif order == 'quit'[:len(order)]:
                    os._exit(0)
                else:
                    if_in = False
                    for _ in ['year', 'ryear']:
                        if order == _[:len(order)]:
                            if_in = True
                            scroller = scroll(_)
                            try:
                                scroller.next()
                            except:
                                pass
                            break
                    if if_in is False:
                        print('\033[0 ;31;48m Unrecgonized command: %s \033[0m' % orderlist[-1])
                        continue
        print("\033[0;32;48m URL: \033[0m\033[1;30;48m%s\033[0m" % sr.url)


def get_ainfo():
    try:
        print("\033[0;34;48m Search by author and year:\033[0m")
        a_list = list()
        fauthor = None
        exact = 'NO'
        year = ['1900', '%d' % int(time.localtime().tm_year)]
        while True:
            get = raw_input(' author \033[0;32;48m >>> \033[0m ')
            orderlist.append(get)
            if get.find('!') >= 0:
                get = get.replace('!', '')
                exact = 'YES'
            if get == '' or get.isspace():
                break
            if get == 'exit'[:len(get)]:
                return None
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
                        fauthor = format_author(get[1:])
                    else:
                        a_list.append(format_author(get))
        if len(year) == 1:
            year *= 2
        if fauthor is None and len(a_list) == 0:
            return None
        sr = dc.ASearchResult(first_author=fauthor, author_list=a_list, year=year, exact=exact)
        return sr
    except:
        return None


def get_jinfo():
    print("\033[0;34;48m Search by journal:\033[0m")
    print(" hints: \033[1;35;48m ApJ\033[0m; \033[1;35;48m ApJS\033[0m; \033[1;35;48m MNRAS\033[0m; \033[1;35;48m A&A\033[0m; \033[1;35;48m ARA&A\033[0m; \033[1;35;48m Natur\033[0m;\033[1;35;48m NatAs\033[0m; \033[1;35;48m NatPh\033[0m; \033[1;35;48m Sci\033[0m; \033[1;35;48m PhRv(ABCDEFLMP)\033[0m; \033[1;35;48m A&ARv\033[0m; \033[1;35;48m RAA\033[0m")
    journal = raw_input(" journal \033[0;32;48m >>> \033[0m ")
    journal = journal.replace('&', '%26')
    orderlist.append(journal)

    if journal == 'exit'[:len(journal)] and len(journal) > 0:
        return None
    if journal == 'quit'[:len(journal)] and len(journal) > 0:
        os._exit(0)

    year = raw_input(" year \033[0;32;48m >>> \033[0m")
    orderlist.append(year)
    if year == 'exit'[:len(year)] and len(year) > 0:
        return None
    if year == 'quit'[:len(year)] and len(year) > 0:
        os._exit(0)

    volume = raw_input(' volume \033[0;32;48m >>> \033[0m ')
    orderlist.append(volume)
    if volume == 'exit'[:len(volume)] and len(volume) > 0:
        return None
    if volume == 'quit'[:len(volume)] and len(volume) > 0:
        os._exit(0)

    page = raw_input(' page \033[0;32;48m >>> \033[0m ')
    orderlist.append(page)
    if page == 'exit'[:len(page)] and len(page) > 0:
        return None
    if page == 'quit'[:len(page)] and len(page) > 0:
        os._exit(0)
    sr = dc.JSearchResult(journal=journal, year=year, volume=volume, page=page)
    return sr


def help():
    print("Type the citation for a quick search (default): e.g., Li, et al., (2017).")
    print("Type a(uthor) for the author-and-year based search (Last name, First name).")
    print("Type j(ournal) for a publication specified search.")


if __name__ == '__main__':
    os.system('imgcat ~/Documents/Work/ADS/logo/ads_logo_left.png')
    orderlist = list()
    outer_loop()