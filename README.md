# ADS-command-line
An interactive command line tool desigened for [Astronomical Data System](http://www.adsabs.harvard.edu)

## System requirement
Python2 (and packages including re and urlib2), [iTerm2](http://www.iterm2.com) (Best operating environment to enable terminal-based url request)

## Search modes
The software allows three modes of searching.
1. Citation based (default)
![img](https://github.com/LiYunyang/ADS-command-line/blob/master/cmod.png)
   type the citation, e.g., Li, at al., (2017); Li & Bregman 2017, etc.
2. Author-year based
    ![img](https://github.com/LiYunyang/ADS-command-line/blob/master/amod.png)
   type a(uthor) to enter this search mode. 
   Use the coventional ^ before the first author, the form of the author goes as Last; Last, First; or Last, F. The search is case insensitive.
   
   The year is **required**. Can be a single year as 2017 or two years concatenated by '-' for a search within the range.
3. Publication based
![img](https://github.com/LiYunyang/ADS-command-line/blob/master/jmode.png)
   type j(ournal) to enter this search mode.
   Type the abbreviations of the journal, year, volume and pages as indiated. Either of the term can be omitted.
   
## Search output
The results of the search is list in a citation-descending order. 

The link to the article is given in the F(ull), E(journal), X(arXiv) order unless neither of these term is availiable.

Click the url lind to acess to the PDF version of the article.

## Ciation
type the **num** to get the bibTeX ciation, which is copied to the clipboard.
