from selenium import webdriver as seleniumWebDriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep, strftime
from random import randint
import pandas as pd

class InstagramBot:
    def __init__(self, chromedriver_path, username, password):
        self.chromedriver_path = chromedriver_path
        self.username = username
        self.password = password

    def driver(self):
        return seleniumWebDriver.Chrome(executable_path=self.chromedriver_path)


    def login(self):
        webdriver = self.driver()
        sleep(2)
        webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)

        username = webdriver.find_element_by_name('username')
        username.send_keys(self.username)
        password = webdriver.find_element_by_name('password')
        password.send_keys(self.password)

        # button_login = webdriver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > button')
        # button_login =webdriver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(4) > button > div')
        button_login = webdriver.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button > div')
        button_login.click()
        sleep(3)
        return webdriver

        # notnow = webdriver.find_element_by_css_selector('body > div:nth-child(13) > div > div > div > div.mt3GC > button.aOOlW.HoLwm')
        # notnow.click() #comment these last 2 lines out, if you don't get a pop up asking about notifications

    def follow_hashtag(self, webdriver, hashtag='travelblog', pages=10):
        # hashtag_list = [x.strip() for x in hashtag_list.split(" ")]

        prev_user_list = prev_user_list = list(pd.read_gbq(query="""select distinct followed_username
                                                                    from `scarlet-labs.instagram.followed_master_table`
                                                                    where master_account = '{username}'
                                                                    """.format(username=self.username),
                                                            project_id="scarlet-labs",
                                                            private_key="scarlet-labs.json",
                                                            dialect="standard")["followed_username"])
        new_followed = []
        new_followed_datetime = []
        comment_list = []
        tag = -1
        followed = 0
        likes = 0
        comments = 0

        webdriver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
        # webdriver.get('https://www.instagram.com/'+ hashtag + '/') #for account pages
        sleep(5)
        first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
        # first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div') #for account pages

        first_thumbnail.click()
        sleep(randint(1,2))
        for x in range(1,int(pages)):
            try:
                # username = webdriver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text
                username = webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/span/a').text


                if username not in prev_user_list:
                    # If we already follow, do not unfollow
                    if webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').text == 'Follow':
                        webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[2]/button').click()

                        new_followed.append(username)
                        new_followed_datetime.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        followed += 1

                        # Liking the picture
                        button_like = webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button/div/span')
                        button_like.click()
                        likes += 1
                        sleep(randint(5,10))

                        # Comments and tracker
                        comment_choices = ["Really Cool!", "Nice Work :)", "Nice job!", "So cool! :)", "Wow, this is awesome!"]
                        comm_prob = randint(0,7)
                        print('{}_{}: {}'.format(hashtag, x, comm_prob), end=" ")

                        if comm_prob <= len(comment_choices):
                            comments += 1
                            webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[3]/section[3]/div').click()
                            comment_box = webdriver.find_element_by_xpath('/html/body/div[4]/div[2]/div/article/div[3]/section[3]/div/form/textarea')

                            comment_box.send_keys(comment_choices[comm_prob])
                            comment_list.append(comment_choices[comm_prob])
                            sleep(1)
                            # Enter to post comment
                            comment_box.send_keys(Keys.ENTER)
                            sleep(randint(5,20))
                        else:
                            comment_list.append("no comment")

                    # Next picture
                    webdriver.find_element_by_link_text('Next').click()
                    sleep(randint(5,10))
                else:
                    webdriver.find_element_by_link_text('Next').click()
                    sleep(randint(5,10))
            except Exception as e:
                print(e)
                logging.debug(e)
                continue

        account_column = [self.username] * len(new_followed)
        hashtag_column = [hashtag] * len(new_followed)
        print({"followed_username":len(new_followed),
                                        "followed_datetime":len(new_followed_datetime),
                                        "comment":len(comment_list),
                                        "hashtag":len(hashtag_column),
                                        "master_account":len(account_column)})
        updated_user_df = pd.DataFrame({"followed_username":new_followed,
                                        "followed_datetime":new_followed_datetime,
                                        "comment":comment_list,
                                        "hashtag":hashtag_column,
                                        "master_account":account_column})

        return updated_user_df
