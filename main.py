import datetime
import os
import random
from urllib.parse import urlencode
from dataclasses import dataclass

import click
import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.select import Select


def send_tg_message(text: str):
    bot_token = os.environ.get("API_TOKEN")
    channel_id = os.environ.get("NOTIFICATIONS_CHANNEL_ID")
    notification_text = urlencode({"text": text})
    requests.post(
        f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={channel_id}&{notification_text}'
    )


def payload(driver: WebDriver, log_to_tg: bool):
    driver.get(
        "https://armenia.blsspainvisa.com/book_appointment.php"
    )

    driver.implicitly_wait(2.0)
    driver \
        .find_element(By.CSS_SELECTOR, "#centre > option:nth-child(2)") \
        .click()

    driver \
        .find_element(By.XPATH, '//*[@id="category"]')\
        .click()
    driver\
        .find_element(By.XPATH, '//select/option[@value="Normal"]') \
        .click()

    driver \
        .find_element(By.CSS_SELECTOR, "#phone") \
        .send_keys("43" + str(random.randint(0, 100000)))

    driver \
        .find_element(By.XPATH, '//*[@id="email"]') \
        .send_keys(f"Ralinazh{random.randint(0, 100)}@gmail.com")

    driver \
        .find_element(By.XPATH,
                      '/html/body/div[1]/form/section[1]/div/div/div[3]/div[2]/div[8]/div[2]/input') \
        .click()

    driver.implicitly_wait(2.0)

    agree_to_terms_xpath = "/html/body/div[1]/form/section/div/div/div/div[3]/div[1]/button"
    driver \
        .find_element(By.XPATH, agree_to_terms_xpath) \
        .click()

    driver \
        .find_element(By.XPATH, '//*[@id="app_date"]') \
        .click()

    cal = driver \
        .find_element(By.CSS_SELECTOR,
                      ".datepicker-days > table:nth-child(1)")

    calendar_days = cal.find_elements(By.CLASS_NAME, "day")

    open_days = [x for x in calendar_days if
                 "disabled" not in x.get_attribute("class").split(" ")]

    if len(open_days) > 0 and log_to_tg:
        bot_token = os.environ.get("API_TOKEN")[:-1]
        channel_id = os.environ.get("NOTIFICATIONS_CHANNEL_ID")
        notification_text = urlencode({
            "text": "There is a new appoitment slot open! https://armenia.blsspainvisa.com/appointment.php"
        })
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={channel_id}&{notification_text}'
        )


@click.command()
@click.option("--selenium_url", default="http://localhost:4444",
              help="in the format http://host:port.")
@click.option("--log-to-tg", "log_to_tg", is_flag=True, show_default=True,
              default=False,
              help="Enables sending messages to telegram channel")
def wrapper(selenium_url: str, log_to_tg):
    with webdriver.Remote(f"{selenium_url}/wd/hub",
                          DesiredCapabilities.CHROME) as driver:
        try:
            payload(driver, log_to_tg)
        except Exception as e:
            print(e)
            with open("error_screen.png", "wb") as file:
                driver.get_screenshot_as_file(file.name)
            if log_to_tg:
                send_tg_message("Error occurred, please, check the bot logs.")
            raise e


if __name__ == '__main__':
    wrapper()
