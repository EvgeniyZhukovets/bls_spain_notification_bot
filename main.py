import argparse
import http
import os
import random
from http import client
import urllib
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def __send_message(text: str, token: str, channel_id: str):
    connection = http.client.HTTPSConnection("api.telegram.org")
    notification_text = urllib.parse.urlencode({"text": text})
    url = f"/bot{token}/sendMessage?chat_id={channel_id}&{notification_text}"
    connection.request("POST", url)
    response = connection.getresponse()
    if response.status != 200:
        raise Exception(f"Failed to send message. Status code: {response.status}")


def send_tg_message(text: str):
    bot_token = os.environ.get("API_TOKEN_NOTIFICATION")
    channel_id = os.environ.get("NOTIFICATIONS_CHANNEL_ID")
    __send_message(text, bot_token, channel_id)


def send_tg_alert(text: str):
    bot_token = os.environ.get("API_TOKEN_ALERT")
    channel_id = os.environ.get("ALERTS_CHANNEL_ID")
    __send_message(text, bot_token, channel_id)


def payload(driver: WebDriver, log_to_tg: bool):
    driver.get(
        "https://armenia.blsspainvisa.com/book_appointment.php"
    )

    driver.implicitly_wait(2.0)
    driver \
        .find_element(By.CSS_SELECTOR, "#centre > option:nth-child(2)") \
        .click()

    driver \
        .find_element(By.XPATH, '//*[@id="category"]') \
        .click()
    driver \
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
        send_tg_message("There is a new appoitment slot open! https://armenia.blsspainvisa.com/appointment.php")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wrapper for Selenium')
    parser.add_argument('--selenium_url', default='http://localhost:4444',
                        help='in the format http://host:port.')
    parser.add_argument('--log-to-tg', action='store_true', default=False,
                        help='Enables sending messages to telegram channel')
    args = parser.parse_args()

    with webdriver.Remote(f"{args.selenium_url}/wd/hub",
                          DesiredCapabilities.CHROME) as driver:
        try:
            send_tg_alert("Started.")
            send_tg_message("Started.")
            payload(driver, args.log_to_tg)
        except Exception as e:
            send_tg_alert("Error occurred, please, check the bot logs.")
            raise e
