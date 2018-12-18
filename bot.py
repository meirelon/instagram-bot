from selenium import webdriver as seleniumWebDriver
from selenium.webdriver.common.keys import Keys
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

        button_login = webdriver.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > button')
        button_login.click()
        sleep(3)
        return webdriver

        # notnow = webdriver.find_element_by_css_selector('body > div:nth-child(13) > div > div > div > div.mt3GC > button.aOOlW.HoLwm')
        # notnow.click() #comment these last 2 lines out, if you don't get a pop up asking about notifications

    def follow_hashtag(self, webdriver, hashtag='travelblog', pages=10, file_path=None):
        # hashtag_list = [x.strip() for x in hashtag_list.split(" ")]

        prev_user_list = [] #- if it's the first time you run it, use this line and comment the two below
        if file_path:
            prev_user_list = pd.read_csv(file_path, delimiter=',').iloc[:,1:2] # useful to build a user log
            prev_user_list = list(prev_user_list['0'])


        new_followed = []
        tag = -1
        followed = 0
        likes = 0
        comments = 0

        webdriver.get('https://www.instagram.com/explore/tags/'+ hashtag + '/')
        # webdriver.get('https://www.instagram.com/'+ hashtag + '/') #for account pages
        sleep(5)
        first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[1]/a/div')
        # first_thumbnail = webdriver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[3]/article/div[1]/div/div[1]/div[1]/a/div') #for account pages

        first_thumbnail.click()
        sleep(randint(1,2))
        for x in range(1,pages):
            try:
                username = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text

                if username not in prev_user_list:
                    # If we already follow, do not unfollow
                    if webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[2]/button').text == 'Follow':
                        webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/header/div[2]/div[1]/div[2]/button').click()

                        new_followed.append(username)
                        followed += 1

                        # Liking the picture
                        button_like = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[1]/button/span')
                        button_like.click()
                        likes += 1
                        sleep(randint(18,25))

                        # Comments and tracker
                        comment_choices = ["Really Cool!", "Nice Work :)", "Nice job!", "So cool! :)", "Wow, this is awesome!"]
                        comm_prob = randint(0,7)
                        print('{}_{}: {}'.format(hashtag, x,comm_prob), end=" ")

                        if comm_prob <= len(comment_choices):
                            comments += 1
                            webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[1]/span[2]/button/span').click()
                            comment_box = webdriver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/article/div[2]/section[3]/div/form/textarea')

                            comment_box.send_keys(comment_choices[comm_prob])
                            sleep(1)
                            # Enter to post comment
                            comment_box.send_keys(Keys.ENTER)
                            sleep(randint(22,28))

                    # Next picture
                    webdriver.find_element_by_link_text('Next').click()
                    sleep(randint(25,29))
                else:
                    webdriver.find_element_by_link_text('Next').click()
                    sleep(randint(20,26))
            except:
                continue

        for n in range(0,len(new_followed)):
            prev_user_list.append(new_followed[n])

        updated_user_df = pd.DataFrame(prev_user_list)
        updated_user_df.to_csv('{}_users_followed_list.csv'.format(strftime("%Y%m%d-%H%M%S")), index=False)
        print('Liked {} photos.'.format(likes))
        print('Commented {} photos.'.format(comments))
        print('Followed {} new people.'.format(followed))
