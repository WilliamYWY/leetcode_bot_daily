from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import datetime
import argparse


def get_lc_problem():
    # Set up the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")  # Maximize the window on open
    options.add_argument("--disable-extensions")  # Disable any extensions
    options.add_argument("--headless")  # Run in headless mode (without GUI)
    driver = webdriver.Chrome(options=options)

    # Navigate to the LeetCode main page
    driver.get("https://leetcode.com/problemset/all/")
    ls = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@class='-mx-4 md:mx-0']",
            )
        )
    )
    problems = WebDriverWait(ls, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@class='odd:bg-layer-1 even:bg-overlay-1 dark:odd:bg-dark-layer-bg dark:even:bg-dark-fill-4']",
            )
        )
    )

    daily_problem = WebDriverWait(problems, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[@class='h-5 hover:text-blue-s dark:hover:text-dark-blue-s']",
            )
        )
    )
    title = daily_problem.text
    link = daily_problem.get_attribute("href")
    driver.get(link)
    info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "_1l1MA"))
    )
    text = info.text
    driver.quit()

    return title, text, link


def send_message(title, text, link):
    content = text + "\n\n" + link
    body = {"content": content, "thread_name": title}
    result = requests.post(WEBHOOK_URL, json=body)


def send_alert(content, dev_url):
    body = {"content": content}
    result = requests.post(dev_url, json=body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-hk", "--hook", help="Webhook url", required=True)
    parser.add_argument(
        "-t", "--time", help="Time to update every day (hours only 0-23)", default=7
    )
    parser.add_argument("-d", "--dev", help="additional hook for info", default=None)
    args = parser.parse_args()
    WEBHOOK_URL = args.hook
    hour = int(args.time)
    if args.dev:
        send_alert("Start LC daily service!!!", args.dev)

    try:
        while True:
            now = datetime.datetime.now()
            target_datetime = datetime.datetime(
                now.year, now.month, now.day + 1, hour, 0, 0
            )
            time_diff = (target_datetime - now).total_seconds()
            time.sleep(time_diff)
            retried = 0
            while retried < 5:
                try:
                    title, text, link = get_lc_problem()
                    send_message(title, text, link)
                    break
                except:
                    retried += 1
                    continue
    finally:
        if args.dev:
            send_alert("LC daily service is down!!!", args.dev)
