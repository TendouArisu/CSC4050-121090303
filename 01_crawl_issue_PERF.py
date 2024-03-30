
'''
To use this script, changing the source file name/dir, and the output file name/dir are enough
'''


from github import Github, RateLimitExceededException
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re
import os
import requests
import sys

sys.path.append(os.path.abspath('../utils'))
print(os.path.abspath('../utils'))
from github_crawler import GitHubCrawler



if __name__ == "__main__":
    token_pool = ['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', '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', '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']
    # Repos needed to crawl, one at a time
    repos = ['pandas-dev/pandas']
    crawler = GitHubCrawler(token_pool)

    # Load already fetched PR numbers
    crawler.load_fetched_pr_numbers(f"merged_pull_requests_{repos[0].replace('/','_')}_in2years.json")

    # Read pr titles needed to be collected
    with open('../../data/issue_title4collection/pandas-dev_pandas_selected_issue_titles_linked:pr_closed:>2021-08-17_label:Performance.json','r') as j:
        titles = j.readlines()
    print(titles)



    data_str = ''.join(titles)

    data_dict = json.loads(data_str)

    titles = data_dict['pandas-dev/pandas']



    selected_num = [int(re.search(r' - (\d+)', item).group(1)) for item in titles]


    crawler.fetch_pull_requests(repos[0],selected_num)

    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     results = list(executor.map(crawler.fetch_pull_requests, repos, selected_num))

    crawler.save_to_file(f"merged_pull_requests_{repos[0].replace('/','_')}_in2years.json")