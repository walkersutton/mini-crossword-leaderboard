import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
"""
USERNAME = "secret"
PASSWORD = "secret"
GOOGLE_SHEETS_API_KEY = "secret"
GOOGLE_SHEETS_API_CONFIG = {}
"""

def formatStats(driver):
    playerStats = {}
    for player_id in range(9):
        name = driver.find_element_by_xpath('//*[@id="lbd-root"]/div/div[2]/div[' + str(player_id + 1) + ']/p[2]').get_attribute('innerHTML')
        try:
            score = driver.find_element_by_xpath('//*[@id="lbd-root"]/div/div[2]/div[' + str(player_id + 1) + ']/p[3]').get_attribute('innerHTML')
        except Exception as e:
            score = '--'
        playerStats[name] = score
    return playerStats


def getStats():
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(options = opts)

    driver.get("https://myaccount.nytimes.com/auth/login?response_type=cookie&client_id=lgcl&redirect_uri=https%3A%2F%2Fwww.nytimes.com/puzzles/leaderboards")

    driver.find_element_by_xpath('//*[@id="username"]').send_keys(USERNAME)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(PASSWORD)
    driver.find_element_by_xpath('//*[@id="myAccountAuth"]/div[1]/div/form/div/div[4]/button').click()

    time.sleep(2)

    if (driver.title == 'Leaderboards - The New York Times - The New York Times'):
        stats_dict = formatStats(driver)
        driver.quit()
        return stats_dict

    driver.find_element_by_xpath('//*[@id="recaptcha-anchor"]').click()

    driver.find_element_by_xpath('//*[@id="username"]').send_keys(USERNAME)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(PASSWORD)
    driver.find_element_by_xpath('//*[@id="myAccountAuth"]/div[1]/div/form/div/div[4]/button').click()

    time.sleep(2)
    stats_dict = formatStats(driver)
    driver.quit()
    return stats_dict

def pipeSheets(nyt_data):
    player_scores = {}

    for player in nyt_data:
        score_data = str(nyt_data[player])
        if (score_data == '--'):
            seconds = ''
        else:
            score_ar = score_data.split(":")
            if (len(score_ar) >  1):
                seconds = int(score_ar[0]) * 60 + int(score_ar[1])
            else:
                print('getting here too')
                seconds = int(score_ar[0])
        player_scores[player.strip()] = seconds

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_API_CONFIG, scope)

    client = gspread.authorize(creds)

    data_sheet = client.open_by_key(GOOGLE_SHEETS_API_KEY).worksheet('data')  # Open the spreadhseet

    current_date = date.today().strftime('%m/%d/%Y')

    day_of_week_value = date.today().weekday()
    if (day_of_week_value == 6):
        day_of_week_value = 1
    else:
        day_of_week_value += 2

    new_row = [day_of_week_value, current_date, player_scores['Big Guy'], player_scores['Els05'], player_scores['walker <span class="lbd-score__you">(you)</span>'], player_scores['willowww'], player_scores['mom'], player_scores['Jinga822'], player_scores['charliebear'], player_scores['hannah'], player_scores['Jarett']]

    data_sheet.append_row(new_row, value_input_option='USER_ENTERED', insert_data_option="INSERT_ROWS")
    exit()

stats_dict = getStats()
pipeSheets(stats_dict)
print("successfully added today's data'")
