from github import Github, RateLimitExceededException
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import re
import os
import requests


class GitHubCrawler:
    def __init__(self, token_pool, fetched_pr_numbers=set()):
        self.token_pool = token_pool
        self.current_token_index = 0
        self.github = Github(self.token_pool[self.current_token_index])
        self.data = []
        self.fetched_pr_numbers = fetched_pr_numbers
        self.lock = Lock()

    def switch_token(self):
        with self.lock:
            self.current_token_index = (self.current_token_index + 1) % len(self.token_pool)
            self.github = Github(self.token_pool[self.current_token_index])

    def fetch_pull_requests(self, repo_name, prnum):
        try:
            print(f"Starting to fetch data for repo: {repo_name}")
            repo = self.github.get_repo(repo_name)
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

            for pr in pulls:

                if pr.number not in self.fetched_pr_numbers and pr.number in prnum:
                    comments = []
                    for comment in pr.get_issue_comments():
                        comment_body = comment.body if comment.body else "No comment"
                        comments.append({
                            'commenter': comment.user.login if comment.user else "Unknown",
                            'body': comment_body
                        })


                    print("PAUSE")
                    print(f"Fetching PR number: {pr.number}")

                    body = pr.body if pr.body else "None"

                    changed_files = []
                    for pr_file in pr.get_files():
                        patch = pr_file.patch if pr_file.patch else "No changes"
                        changed_files.append({
                            'filename': pr_file.filename,
                            'patch': patch
                        })

                    pr_data = {
                        'repo': repo_name,
                        'pr_number': pr.number,
                        'body': body,
                        'comments': comments,
                        'changed_files': changed_files,
                    }
                    self.data.append(pr_data)

                    if len(self.data) >= 1:
                        self.save_to_file(f"merged_pull_requests_{repo_name.replace('/', '_')}_in2years.json")
                else:
                    continue



        except RateLimitExceededException:
            print("Rate limit exceeded. Switching token.")
            self.switch_token()

    def load_fetched_pr_numbers(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                for pr in data:
                    self.fetched_pr_numbers.add(pr['pr_number'])
        except FileNotFoundError:
            print("No existing data found. Starting fresh.")

    def save_to_file(self, filename):
        existing_data = []
        try:
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            open(filename, 'w').close()
            pass

        existing_data.extend(self.data)

        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)

        self.data = []

    def fetch_issues(self, repo_name, issuenum):
        try:
            print(f"Starting to fetch data for repo: {repo_name}")
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state='closed', sort='updated', direction='desc')

            for issue in issues:
                if issue.number not in self.fetched_pr_numbers and issue.number in issuenum:
                    comments = []
                    for comment in issue.get_comments():
                        comment_body = comment.body if comment.body else "No comment"
                        comments.append({
                            'commenter': comment.user.login if comment.user else "Unknown",
                            'body': comment_body
                        })

                    print("PAUSE")
                    print(f"Fetching issue number: {issue.number}")

                    body = issue.body if issue.body else "None"

                    issue_data = {
                        'repo': repo_name,
                        'issue_number': issue.number,
                        'body': body,
                        'comments': comments,
                    }
                    self.data.append(issue_data)

                    if len(self.data) >= 1:
                        self.save_to_file(f"closed_issues_{repo_name.replace('/', '_')}_in2years.json")
                else:
                    continue

        except RateLimitExceededException:
            print("Rate limit exceeded. Switching token.")
            self.switch_token()
