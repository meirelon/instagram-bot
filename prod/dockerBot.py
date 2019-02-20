from selenium import webdriver as seleniumWebDriver
from selenium.webdriver.common.keys import Keys

import logging
from datetime import datetime
from time import sleep, strftime
from random import randint
import pandas as pd

class InstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def driver(self):
        chrome_options = seleniumWebDriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        return seleniumWebDriver.Chrome(chrome_options=chrome_options)


    def login(self):
        webdriver = self.driver()
        sleep(2)
        webdriver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)

        username = webdriver.find_element_by_name('username')
        username.send_keys(self.username)
        password = webdriver.find_element_by_name('password')
        password.send_keys(self.password)

        button_login = webdriver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > button')
        button_login.click()
        sleep(3)
        return webdriver

        # notnow = webdriver.find_element_by_css_selector('body > div:nth-child(13) > div > div > div > div.mt3GC > button.aOOlW.HoLwm')
        # notnow.click() #comment these last 2 lines out, if you don't get a pop up asking about notifications

    def unfollow_users(self, webdriver, total_users=11):
        webdriver.get("https://www.instagram.com/{username}/following/".format(username=self.username))
        following_button = webdriver.find_element_by_css_selector('#react-root > section > main > div > header > section > ul > li:nth-child(3) > a')
        following_button.click()

        q = """select distinct followed_username
                from `scarlet-labs.instagram.followed_master_table`
                where date(timestamp(followed_datetime)) < date_sub(current_date(), interval 3 day) and master_account = '{username}'
                """.format(username=self.username)
        unfollow_user_list = pd.read_gbq(query=q,
                                         project_id="scarlet-labs",
                                         dialect="standard",
                                         verbose=False,
                                         private_key="scarlet-labs.json")
        unfollow_user_df = pd.DataFrame()

        user = 0
        while user < total_users:
            user+=1
            try:
                username = webdriver.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div.isgrP > ul > div > li:nth-child({user}) > div > div.Igw0E.IwRSH.YBx95.vwCYk'.format(user=user)).text.split("\n")[0]
                print(username, end=' ')

                if username in list(unfollow_user_list["followed_username"]):
                    following = webdriver.find_element_by_xpath('/html/body/div[2]/div/div[2]/ul/div/li[{user}]/div/div[3]/button'.format(user=user))
                    following.click()
                    unfollow_button = webdriver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/button[1]')
                    sleep(randint(1,3))
                    unfollow_button.click()

                    unfollow_user_df = pd.concat([unfollow_user_df, pd.DataFrame.from_dict({"username":username,
                                "unfollowed_datetime":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "master_account":"colleenthehorse"}, orient="index").transpose()], axis=0)

            except Exception as e:
                print(e)
        return unfollow_user_df

    def follow_hashtag(self, webdriver, hashtag='travelblog', pages=10):
        # hashtag_list = [x.strip() for x in hashtag_list.split(" ")]
        first_thumbnail_xpath = '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div'
        username_xpath = '/html/body/div[2]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a'
        follow_button_xpath = '/html/body/div[2]/div/div[2]/div/article/header/div[2]/div[1]/div[2]/button'
        button_like_xpath = '/html/body/div[2]/div/div[2]/div/article/div[2]/section[1]/span[1]/button/span'
        comment_button_xpath = '/html/body/div[2]/div[2]/div/article/div[2]/section[1]/span[2]/button/span'
        comment_box_xpath = '/html/body/div[2]/div[2]/div/article/div[2]/section[3]/div/form/textarea'




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
        first_thumbnail = webdriver.find_element_by_xpath(first_thumbnail_xpath)
        # first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[2]/article/div[1]/div/div[1]/div[1]/a/div') #for account pages

        first_thumbnail.click()
        sleep(randint(1,2))
        for x in range(1,int(pages)):
            try:
                # username = webdriver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text
                username = webdriver.find_element_by_xpath(username_xpath).text

                if username not in prev_user_list:
                    # If we already follow, do not unfollow
                    try:
                        follow_button = webdriver.find_element_by_xpath(follow_button_xpath)
                    except:
                        follow_button = webdriver.find_element_by_xpath('/html/body/div[2]/div[2]/div/article/header/div[2]/div[1]/div[2]/button')

                    if follow_button.text == 'Follow':
                        # follow_button.click()

                        new_followed.append(username)
                        new_followed_datetime.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        followed += 1

                        # Liking the picture
                        try:
                            button_like = webdriver.find_element_by_xpath(button_like_xpath)
                        except:
                            button_like = webdriver.find_element_by_xpath('/html/body/div[2]/div[2]/div/article/div[2]/section[1]/span[1]/button/span')


                        button_like.click()
                        likes += 1
                        sleep(randint(5,10))

                        # Comments and tracker
                        comment_choices = ["Really Cool!", "Nice Work :)", "Nice job!", "So cool! :)", "Wow, this is awesome!"]
                        comm_prob = randint(0,7)
                        print('{}_{}: {}'.format(hashtag, x, comm_prob), end=" ")

                        if comm_prob < len(comment_choices):
                            comments += 1

                            try:
                                webdriver.find_element_by_xpath(comment_button_xpath).click()
                            except:
                                webdriver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/article/div[2]/section[1]/span[2]/button/span').click()

                            try:
                                comment_box = webdriver.find_element_by_xpath(comment_box_xpath)
                            except:
                                comment_box = webdriver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/article/div[2]/section[3]/div/form/textarea')

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
        d = {"followed_username":new_followed,
                                        "followed_datetime":new_followed_datetime,
                                        "comment":comment_list,
                                        "hashtag":hashtag_column,
                                        "master_account":account_column}
        updated_user_df = pd.DataFrame.from_dict(d, orient='index')

        return updated_user_df.transpose()
