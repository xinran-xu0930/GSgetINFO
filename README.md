# GSgetINFO

**Through the mirror of Google Scholar, using keywords to search for literature of limited years, the title, abstract, doi and pmid of the literature are finally returned**

# Table of content

- Installation and Requirement

- Example and Usage

- Result file

- Maintainers and Contributing

- Licences

# Installation and Requirement

## Install

GSgetINFO-tools is written in Python3 and is executed from the command line. To install GSgetINFO-tools simply download the code and extract the files into a GSgetINFO-tools installation folder.

## GSgetINFO-tools needs the following python package to be installed:

pandas;bs4;colorama;lolcat;fake_useragent;subprocess;argparse;requests;difflib;time;re;ssl

Among them, colorama, lolcat, bs4 and fake_useragent need to be additionally downloaded by users through the following command line; the other python packages are python3's own

```Shell
pip install colorama
pip install lolcat
pip install fake-useragent
pip install beautifulsoup4
```

# Example and Usage

## Usage

|||
|-|-|
|-h,--help|show this help message and exit|
|-s,--start|start year|
|-e,--end|end year|
|-o,--outdir|Result storage directory|
|-k,--key|keywords|
|-p,--page|Start page (you can get literature information from the specific page number returned by Google Academic, which starts from the first page by default)|

## Example

Search all literature information with the keyword "eqtl variables" throughout 2022

```Shell
cd ~/GSgetINFO
python GSgetINFO.py -s 2022 -e 2022 -o ~/res_outdir -k "eqtl varients"
```

# Result file

The final result file named key_word_google.csv will be obtained (key_word is the keyword entered by the user)

|Title|Abstract|DOI|PMID|
|-|-|-|-|
|　|　|　|　|

# Maintainers and Contributing

- GSgetINFO-tools is developed and maintained by Xinran Xu (xinranxu0930@gmail.com).

# Licences

- Released under MIT license

