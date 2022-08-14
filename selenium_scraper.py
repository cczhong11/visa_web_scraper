# from pyvirtualdisplay import Display
from cgitb import reset
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import sys
from telegram import send_message, send_photo
from cred import username, password, url_id, country_code
from selenium.webdriver.common.by import By


def run_visa_scraper(url, no_appointment_text):
    def has_website_changed():
        '''Checks for changes in the site. Returns True if a change was found.'''
        # Getting the website to check
        driver.get(url)

        # Checking if website is still logged
        if driver.current_url == f'https://ais.usvisa-info.com/en-{country_code}/niv/users/sign_in':
            print('Logging in.')

            # Clicking the first prompt, if there is one
            try:
                driver.find_element(By.XPATH,
                                    '/html/body/div[6]/div[3]/div/button').click()
            except e:
                print(e)
                pass
            # Filling the user and password
            user_box = driver.find_element(By.NAME, 'user[email]')
            user_box.send_keys(username)
            password_box = driver.find_element(
                By.NAME, 'user[password]')
            password_box.send_keys(password)
            # Clicking the checkbox
            driver.find_element(By.XPATH,
                                "//label[contains(@for,'policy_confirmed')]").click()
            time.sleep(1)
            # Clicking 'Sign in'
            driver.find_element(By.NAME,
                                'commit').click()

            # Waiting for the page to load.
            # 5 seconds may be ok for a computer, but it doesn't seem enougn for the Raspberry Pi 4.
            time.sleep(10)

            # Logging to screen
            print('Logged in.')
        # else:
        #     print('Already logged.')

        # Getting the website to check again
        # in case it was redirected to another website and
        # avoid using a timer for waiting for the login redirect. DIDN'T WORK

        print('Checking for changes.')

        # # For debugging false positives.
        # with open('debugging/page_source.html', 'w', encoding='utf-8') as f:
        #     f.write(driver.page_source)

        # Getting main text
        # print(driver.page_source)
        # with open('debugging/main_page', 'w') as f:
        #    f.write(driver.page_source)
        main_page = driver.find_element(By.CLASS_NAME, 'for-layout')
        result = []
        for line in main_page.text.split('\n'):
            if no_appointment_text not in line:
                result.append(line)

        # If the "no appointment" text is not found return True. A change was found.
        # return no_appointment_text not in main_page.text
        return result
    # To run Chrome in a virtual display with xvfb (just in Linux)
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    seconds_between_checks = 10 * 60

    # Setting Chrome options to run the scraper headless.
    chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless")  # Comment for visualy debugging

    # Initialize the chromediver (must be installed and in PATH)
    # Needed to implement the headless option
    driver = webdriver.Chrome(options=chrome_options)

    while True:
        current_time = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())
        print(f'Starting a new check at {current_time}.')
        result = has_website_changed()
        if result:
            print('A change was found. Notifying it.')
            send_photo(driver.get_screenshot_as_png())
            send_message('\n'.join(result))

            # Closing the driver before quicking the script.
            driver.close()
            exit()
        else:
            # print(f'No change was found. Checking again in {seconds_between_checks} seconds.')
            # time.sleep(seconds_between_checks)
            for seconds_remaining in range(int(seconds_between_checks), 0, -1):
                sys.stdout.write('\r')
                sys.stdout.write(
                    f'No change was found. Checking again in {seconds_remaining} seconds.')
                sys.stdout.flush()
                time.sleep(1)
            print('\n')


def main():
    base_url = f'https://ais.usvisa-info.com/en-{country_code}/niv/schedule/{url_id}'

    # Checking for an appointment
    url = base_url + '/payment'
    text = 'No Appointments Available'

# Checking for a rescheduled
# url = base_url + '/appointment'
# text = 'FORCING SCREENSHOT'
# text = 'There are no available appointments at the selected location.'

    run_visa_scraper(url, text)


if __name__ == "__main__":
    main()
