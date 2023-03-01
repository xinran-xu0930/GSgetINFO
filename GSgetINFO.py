# coding: utf-8

import pandas as pd
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from colorama import Fore, Style, Back
from fake_useragent import UserAgent
from subprocess import call
import argparse
import requests
import difflib
import time
import re
import ssl

def print_logo():
    call("cat ./logo.txt | lolcat",shell=True)


#函数：获取目标qtl所有的title
def get_all_titles(start_page,key_words,start_year,end_year):
    all_df = pd.DataFrame(columns=['Title','Abstract','DOI','PMID'])
    for i in range(start_page,100000):
        page_df = get_titles_from_page(i,key_words,start_year,end_year)
        if len(page_df):
            print(f'page {i+1}')
            all_df = pd.concat([all_df,page_df])
            all_df.reset_index(drop=True, inplace=True)
        else:
            return all_df

#函数：获取单页上的title信息
def get_titles_from_page(start,key_words,start_year,end_year):
    res_df = pd.DataFrame(columns=['Title','Abstract','DOI','PMID'])
    url = f'https://xueshu.lanfanshu.cn/scholar?start={start*10}&q={key_words}&hl=zh-CN&as_sdt=0,5&as_ylo={start_year}&as_yhi={end_year}'
    res = requests.get(url)
    while 'So busy' in res.text:
        print('requestment so busy, wait 5s')
        time.sleep(5)
        res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    titles = [title.get_text() for title in soup.find_all('h3', {'class': 'gs_rt'})]
    if titles:
        #删除title前面[]的部分
        for i in range(len(titles)):
            del_part = re.findall(r'\[.*?\]\[.*?\] ',titles[i])
            if del_part:
                titles[i] = titles[i].replace(del_part[0],'')
        res_df['Title'] = titles
        return res_df
    else:
        return res_df

#函数：标题获取doi
def Title2Doi(title):
    url = "https://api.unpaywall.org/v2/search"
    payload = {"query":title,"email":"xinranxu0930@gmail.com"}
    headers= {'User-Agent':str(UserAgent().random)}
    a = requests.get(url,params=payload,headers=headers,timeout=10).json().get('results')
    if a:
        if 'response' in a[0].keys():
            if 'doi' in a[0]['response'].keys():
                return a[0]['response']['doi']
            else:
                return None
        else:
            return None
    else:
        return None

#函数：doi获取pmid
def Doi2Pmid(doi,title):
    url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
    headers= {'User-Agent':str(UserAgent().random)}
    payload = {'ids':doi,'format':'json','email':'xinranxu0930@gmail.com'}
    try:
        a = requests.get(url,params=payload,headers=headers,timeout=10).json().get('records')
    except json.JSONDecodeError:
        pmid,title = Doi2PmidfPubmed(doi,title)
        return pmid,title
    if a:
        if 'pmid' in a[0].keys():
            pmid = a[0]['pmid']
        else:
            pmid,title = Doi2PmidfPubmed(doi,title)
    else:
        pmid,title = Doi2PmidfPubmed(doi,title)
    return pmid,title

##函数：在pubmed中利用doi获取pmid，返回pmid和完整title
def Doi2PmidfPubmed(doi,title):
    doi = doi.replace('/','%',1)
    url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + doi
    headers= {'User-Agent':str(UserAgent().random)}
    res = requests.get(url,headers=headers,timeout=10)
    soup = BeautifulSoup(res.content, 'lxml')
    search_title = re.findall(r'<title>(.*?) - PubMed</title>',str(soup))[0]
    if ' - Search Results' in search_title:
        #匹配上，证明该doi在pubmed中确实没有收录
        return None,title
    similarity = difflib.SequenceMatcher(None,title,search_title).quick_ratio()#这里和原本找到的title进行比对，看一下字符串相似性
    if similarity<0.85:
        return None,title
    else:
        pmid = re.findall(r'"(\d*)" name="citation_pmid"',str(soup))[0]
        return pmid,search_title

#函数：pmid获取abstract
def Pmid2Abstract(pmid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    payload = {'db': 'pubmed','id': pmid,'retmode':'xml'}
    headers= {'User-Agent':str(UserAgent().random)}
    r = requests.get(url,params=payload,headers=headers,timeout=10)
    soup = BeautifulSoup(r.content,"xml")#唯一支持解析xml的解析器
    abstract = soup.find('AbstractText')#获取bs4.element.Tag AbstractText标签 返回的是<AbstractText xx>XX</AbstractText>
    if abstract:
        return abstract.text#获取bs4.element.Tag中的内容，<a>内容</a>
    else:
        return None

###函数：获取xqtl每篇文章的doi pmid abstract
def xqtl_info(t_df):
    for i in t_df.index:
        print(f"\nTitle: {t_df.loc[i,'Title']}")
        doi = Title2Doi(t_df.loc[i,'Title'])
        print(f"doi:{doi}")
        if doi == None:
            print(Fore.YELLOW + f'{i+1}/{len(t_df)} ' + Style.RESET_ALL + 'has finished processing')
            continue
        else:
            t_df.loc[i,'DOI'] = doi
            pmid,t_df.loc[i,'Title'] = Doi2Pmid(doi,t_df.loc[i,'Title'])
            print(f"pmid:{pmid}")
            if pmid == None:
                print(Fore.YELLOW + f'{i+1}/{len(t_df)} ' + Style.RESET_ALL + 'has finished processing')
                continue
            else:
                t_df.loc[i,'PMID'] = pmid
                abstract = Pmid2Abstract(pmid)
                if abstract != None:
                    t_df.loc[i,'Abstract'] = abstract
                print(Fore.YELLOW + f'{i+1}/{len(t_df)} ' + Style.RESET_ALL + 'has finished processing')
    t_df.dropna(axis=0, how='any', inplace=True)
    t_df.drop_duplicates(subset=['DOI'], keep='first', inplace=True)
    t_df.reset_index(drop=True, inplace=True)
    return t_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--start', type=str,help='start year')
    parser.add_argument('-e','--end', type=str,help='end year')
    parser.add_argument('-o','--outdir', type=str,help='Result output directory')
    parser.add_argument('-k','--key', type=str,help='key word')
    parser.add_argument('-p','--page', type=int,default=0,required=False,help='Get the literature information from the user-defined starting page number, starting from the first page by default')
    args = parser.parse_args()

    ssl._create_default_https_context = ssl._create_unverified_context
    print_logo()

    #当关键词为多个单词时，修改
    key_word = filename = args.key
    if ' ' in args.key:
        key_word = args.key.replace(' ','+')
        filename = args.key.replace(' ','_')
    #判断输入的start year和end year是否符合逻辑关系#
    if int(args.start) > int(args.end):
        print(Fore.RED + "Error: Start year must be less than or equal to end year!" + Style.RESET_ALL)
        exit(1)
    #处理结果存放目录
    if args.outdir[-1] != '/':
        outdir = args.outdir+"/"
    else:
        outdir = args.outdir
    res_file_name = outdir+filename+"_google.csv"
    #下载文献title
    print(Back.YELLOW + Fore.BLACK + f'now downloading information about {args.key}' + Style.RESET_ALL)
    t_df = get_all_titles(args.page,key_word,args.start,args.end)
    if len(t_df)==0:
        print(Fore.RED + f'{args.key} ' + Style.RESET_ALL + 'unable to find relevant documents')
    else:
        xqtl_df = xqtl_info(t_df)
        if len(xqtl_df)==0:
            print(Fore.RED + f'{args.key} ' + Style.RESET_ALL + 'unable to find relevant documents')
        else:
            xqtl_df.to_csv(res_file_name,index=False)
            print(f"{args.key}'s info was downloaded")


