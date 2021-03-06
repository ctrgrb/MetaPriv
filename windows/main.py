# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
## for firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
## for chrome
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.chrome.service import Service as CService
from webdriver_manager.chrome import ChromeDriverManager
# partial imports
from time import sleep as Sleep
from datetime import timedelta, datetime
from tempfile import gettempdir
from shutil import copytree
from base64 import b64encode
# full imports
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
import multiprocessing as mp
import os
import random
import getpass
import threading
import sqlite3
import sys
# imports from created files 
from firstlaunchclass import First_launch_UI
from passwordclass import Enter_Password_UI
from crypto import Hash, aes_encrypt, aes_decrypt


NORMAL_LOAD_AMMOUNT = 2
ONE_HOUR = 3600
W = 'white'
INFO_TEXT = """[*] INFO [*]
In this window you should choose your desired privacy level. 
Choose 100 to have the noise amount as double the amount of 
your normal traffic. You can be change the privacy value 
on your next run. 

If this is your first run, MetaPriv will analize your daily 
interaction with Facebook from the last week and, based on 
that and your input, decide how much noise to add to your 
Facebook account. 

To start adding noise to your account, press the button Start.
To exit MetaPriv, close the window by pressing X on your window 
border. Sometimes it may take few seconds to close. 

If you want to reset MetaPriv, delete the hidden saved_data
file. Note that your local password will not work anymore.
For more information please refer to the documentation in the
github repository.
"""

#########################################################################################################################

class BOT:

	def update_keyword(self, key, new_word = None):
		# Increment keyword usage in file
		filepath = os.getcwd()+'\\'+'.saved_data'
		with open(filepath, "r") as f1:
		   text = f1.read()
		text = text.split('\n')
		if new_word == None:
			keyword_line = aes_decrypt(text[2],key)
			word, usage_number = keyword_line.split('|')
			usage_number = int(usage_number) + 1
		else:
			word = new_word
			usage_number = 0
		text[2] = aes_encrypt(word + '|' + str(usage_number),key)
		timestamp = get_date()
		new_hmac = b64encode(Hash(b64encode(key).decode('utf-8') + timestamp + text[2])).decode('utf-8')
		text[6] = new_hmac
		text[7] = timestamp
		text = '\n'.join(text)
		with open(filepath, "w") as f2:
			f2.write(text)

	def check_keyword(self,key):
		with open(os.getcwd()+'\\'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			keyword_line = text[2]
			dec_keyword = aes_decrypt(keyword_line,key).split('|')
			keyword = dec_keyword[0]
			usage_number = int(dec_keyword[1])
			timestamp = text[7]
			HMAC = text[6]
		# Verify keyword integrity
		hmac = b64encode(Hash(b64encode(key).decode('utf-8') + timestamp + keyword_line)).decode('utf-8')
		if hmac != HMAC:
			write_log("[!] Protocol broken!!!",key)
			self.quit_bot()
			sys.exit()
		return keyword, usage_number

	def gen_keyword(self, keyword, browser, key):
		# Generate new keywords from https://relatedwords.org
		write_log(get_date()+": "+"Generating new keyword...",key)
		# Open temporary driver
		if browser == "Firefox":
			fx_options = Options()
			fx_options.add_argument("--headless")
			temp_driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
		elif browser == "Chrome":
			ch_options = COptions()
			ch_options.add_argument("--headless")
			prefs = {"profile.default_content_setting_values.notifications" : 2}
			ch_options.add_experimental_option("prefs",prefs)
			ch_options.add_argument("--disable-infobars")
			temp_driver = webdriver.Chrome(service=CService(ChromeDriverManager().install()),options = ch_options)
		url = 'https://relatedwords.org/relatedto/' + keyword.lower()
		temp_driver.get(url)
		word_elements = temp_driver.find_elements(By.XPATH, "//a[@class='item']")[:5]
		# Get words
		words = []
		for word_element in word_elements:
			words.append(word_element.text)
		# Close driver
		temp_driver.quit()
		# Choose a random word from top 5 
		pseudo_random_word = words[random.randint(0,4)]
		write_log(get_date()+": "+"Done! New keyword: "+pseudo_random_word,key)
		sleep(2)
		self.update_keyword(key, pseudo_random_word)
		return pseudo_random_word

	def start_bot(self, eff_privacy, key):
		# Browser input
		with open(os.getcwd()+'\\'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			browser = aes_decrypt(text[3],key)

		# Create log file
		if not os.path.isfile(os.getcwd()+'\\bot_logs.log'):
			text = get_date()+": "+"First launch\n"
			print(text)
			with open(os.getcwd()+'\\'+"bot_logs.log", "w") as f:
				f.write(aes_encrypt(text,key))

		tempdirs = []
		# Start webdriver
		if browser == 'Firefox':
			# Check if browser profile folder exists
			profile_exists = os.path.isdir(os.getcwd()+'\\fx_profile')
			if not profile_exists:
				tempdirs = os.listdir(gettempdir())
			# webdriver options
			fx_options = Options()
			profile_path = os.getcwd()+'\\fx_profile'
			if profile_exists:
				fx_options.add_argument("--profile")
				fx_options.add_argument(profile_path)
			fx_options.add_argument("--headless")
			# Start
			self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
			self.driver.set_window_size(1400,814)

		elif browser == 'Chrome':
			profile_exists = False
			'''
			# Check if browser profile folder exists
			profile_exists = os.path.isdir(os.getcwd()+'/ch_profile')
			if not profile_exists:
				tempdirs = os.listdir(gettempdir())
			'''
			# webdriver options
			ch_options = COptions()
			prefs = {"profile.default_content_setting_values.notifications" : 2}
			ch_options.add_experimental_option("prefs",prefs)
			ch_options.add_argument("--disable-infobars")
			ch_options.add_argument("--headless")
			'''
			profile_path = os.getcwd()+'/ch_profile'
			if profile_exists:
				argumnt = "--user-data-dir="+profile_path
				ch_options.add_argument(argumnt)
			'''
			# Start
			self.driver = webdriver.Chrome(service=CService(ChromeDriverManager().install()),options = ch_options)
			self.driver.set_window_size(1400,700)

		eff_privacy = eff_privacy / 100
		sleep(3)
		if chck_quitdriver(): self.quit_bot(t1)

		# Start taking screenshots of the headless browser every second on different thread
		t1 = threading.Thread(target=self.take_screenshot, args=[])
		t1.start()

		# Create userdata folder if it does not exist
		try: 
			os.mkdir(os.getcwd()+"\\userdata")
		except FileExistsError:
			pass

		# Open random Facebook site
		rand_ste = rand_fb_site()
		self.driver.get(rand_ste)

		sleep(5)
		if chck_quitdriver(): self.quit_bot(t1)
		
		# Create browser profile folder
		#print(os.listdir(gettempdir()))
		if not profile_exists:
			self.login(key)
			tempdirs_2 = os.listdir(gettempdir())
			if browser == 'Firefox':
				for i in tempdirs_2:
					if i not in tempdirs:
						if 'mozprofile' in i:
							write_log(get_date()+": "+"Copying profile folder...",key)
							src = gettempdir() + '\\' + i
							os.mkdir('fx_profile')
							cmd = 'Xcopy /C/H/R/S {} {}'.format(src,profile_path)
							os.popen(cmd)


		# Get avg amount of likes per day 
		if os.path.isfile(os.getcwd()+'\\'+'userdata/supplemtary'):
			with open(os.getcwd()+'\\'+'userdata/supplemtary','r') as f:
				avg_amount_of_likes_per_day = int(aes_decrypt(f.read(),key))
		else:
			avg_amount_of_likes_per_day = self.analize_weekly_liked_posts(key)
			if chck_quitdriver(): self.quit_bot(t1)
			if not chck_quitdriver():
				with open(os.getcwd()+'\\'+'userdata\\supplemtary','w') as f:
					f.write(aes_encrypt(str(avg_amount_of_likes_per_day),key))
		
		self.generate_noise(browser, avg_amount_of_likes_per_day, eff_privacy, key)
		self.quit_bot(t1)
		#except:
		#	self.quit_bot()

	def generate_noise(self, browser, avg_amount_of_likes_per_day, eff_privacy, key):
		if chck_quitdriver(): return
		enc_keyword = self.pages_based_on_keyword(browser, key)
		if chck_quitdriver(): return

		# get urls from database based on current keyword
		conn = sqlite3.connect('userdata\\pages.db')
		c = conn.cursor()
		c.execute('SELECT ID FROM categories WHERE category IS "'+enc_keyword+'"')
		ID = c.fetchall()
		c.execute('SELECT URL FROM pages WHERE categID IS '+str(ID[0][0]))
		urls = c.fetchall()
		conn.close()
		random.shuffle(urls)

		# get urls from liked pages from database
		conn = sqlite3.connect('userdata\\likes.db')
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		liked_pages_urls = c.fetchall()
		conn.close()

		for (url,) in urls:
			dec_url = aes_decrypt(url, key)
			write_log(get_date()+": "+"GET: "+ dec_url,key)
			self.driver.get(dec_url)
			sleep(10)
			if chck_quitdriver(): break
			# Start liking
			if (url,) in liked_pages_urls:
				self.like_rand(dec_url, False, avg_amount_of_likes_per_day, eff_privacy, key)
			else:
				new_page(url)
				self.like_rand(dec_url, True, avg_amount_of_likes_per_day, eff_privacy, key)
			# Increment keyword usage
			self.update_keyword(key)
			# Go to random FB site
			rand_site = rand_fb_site()
			self.driver.get(rand_site)
			# wait between 10 s and 10 h
			randtime = rand_dist()
			if not chck_quitdriver():
				time_formatted = str(timedelta(seconds = randtime))
				write_log(get_date()+": "+"Wait for "+ time_formatted + " (hh:mm:ss)",key)
			sleep(5)
			if chck_quitdriver(): break
			sleep(randtime, True)
			if chck_quitdriver(): break

		self.generate_noise(browser, avg_amount_of_likes_per_day, eff_privacy, key)

	def pages_based_on_keyword(self, browser, key):
		# Get current keyword and how many times it was used
		keyword, usage_number = self.check_keyword(key)
		enc_keyword = aes_encrypt(keyword, key)

		# See if db exists. Otherwise, create it 
		conn = sqlite3.connect('userdata\\pages.db')
		c = conn.cursor()
		try:
			c.execute("SELECT category FROM categories")
		except sqlite3.OperationalError:
			create_categ_table()
		# then, get the keywords from the db
		keywords_in_db = c.fetchall()

		# Select URLs of respective keyword
		if (enc_keyword,) in keywords_in_db:
			c.execute('SELECT ID FROM categories WHERE category IS "'+enc_keyword+'"')
			ID = c.fetchall()
			c.execute('SELECT URL FROM pages WHERE categID IS '+str(ID[0][0]))
			urls = c.fetchall()
			conn.close()
			# Generate new keyword if done with urls from db
			nr_of_urls = len(urls)
			if usage_number >= nr_of_urls:
				keyword = self.gen_keyword(keyword, browser, key)
				enc_keyword = aes_encrypt(keyword, key)
		#if chck_quitdriver(): return

		# Add new keyword to db
		if (enc_keyword,) not in keywords_in_db:
			categID = new_keyword(enc_keyword)
			search_url = 'https://www.facebook.com/search/pages?q=' + keyword
			write_log(get_date()+": "+"GET: "+ search_url,key)
			self.driver.get(search_url)
			sleep(3)
			#if chck_quitdriver(): return
			# GET FB URLs based on keyword
			page_urls = self.select_pages(categID, key)
			#if chck_quitdriver(): return
			info = "Pages selected for keyword '{}':".format(keyword)
			write_log(get_date()+": "+info,key)
			for page_url in page_urls:
				write_log(get_date()+": "+"   "+ aes_decrypt(page_url[0],key),key)
			# Save URLs to db
			conn = sqlite3.connect('userdata\\pages.db')
			c = conn.cursor()
			c.executemany('INSERT INTO pages (URL, categID) \
				  		   VALUES (?, ?)', page_urls);
			conn.commit()
			conn.close()

		return enc_keyword

	def load_more(self, n, sec):
		# Scroll down n times to load more elements
		for i in range(n):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			sleep(sec)
			if chck_quitdriver(): break

	def login(self, key):
		# Log in to Facebook
		write_log(get_date()+": "+"Logging in...",key)
		self.driver.get("https://www.facebook.com")
		self.driver.find_element(By.XPATH,"//button[@data-cookiebanner='accept_button']").click()
		sleep(1)
		if chck_quitdriver(): return
		# Decrypt password
		with open(os.getcwd()+'\\'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			email = aes_decrypt(text[0],key)
			encp = text[1]
		password = aes_decrypt(encp, key)
		# Input email and password, then click Log In button.
		self.driver.find_element(By.NAME,"email").send_keys(email)
		self.driver.find_element(By.NAME,"pass").send_keys(password)
		self.driver.find_element(By.XPATH,"//*[text() = 'Log In']").click()
		sleep(3)

	def analize_weekly_liked_posts(self, key):
		# Analize daily Facebook interaction in the last 7 days, based on Facebook logs
		write_log(get_date()+": "+"Analyzing daily Facebook interaction...",key)
		self.driver.get("https://www.facebook.com/100065228954924/allactivity?category_key=ALL")
		while True:
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			days = self.driver.find_elements(By.XPATH, "//div[@class='kvgmc6g5 sj5x9vvc sjgh65i0 l82x9zwi uo3d90p7 pw54ja7n ue3kfks5 hybvsw6c']")
			if len(days) > 8:
				break
			sleep(5)
			if chck_quitdriver(): return

		days = days[:7]
		weekly_amount_of_likes = []
		# How many posts per day
		for day in days:
			likes_per_day = day.find_elements(By.XPATH, ".//div[@class='l9j0dhe7 btwxx1t3 j83agx80']")
			likes = 0
			for like in likes_per_day:
				txt = like.find_element(By.XPATH, ".//div[@class='qzhwtbm6 knvmm38d']").text
				if 'likes' or 'reacted' in txt:
					likes += 1
			weekly_amount_of_likes.append(likes)
			likes = 0

		# Take average
		avg_amount_of_likes_per_day = int(sum(weekly_amount_of_likes)/len(weekly_amount_of_likes))
		return avg_amount_of_likes_per_day

	def select_pages(self, categID, key):
		self.load_more(NORMAL_LOAD_AMMOUNT, 3)
		urls = self.driver.find_elements(By.TAG_NAME,'a')
		urls = [a.get_attribute('href') for a in urls]
		return_urls = []
		for url in urls:
			if url.endswith('?__tn__=%3C'):
				enc_url = aes_encrypt(url.split('?__tn__=%3C')[0], key)
				return_urls.append((enc_url,categID))

		rand_number = random.randint(8,15)
		return return_urls[:rand_number]

	def delete_element(self, element):
		self.driver.execute_script("""var element = arguments[0];
								element.parentNode.removeChild(element);
								""", element)

	def like_rand(self, pagename, first_visit, avg_amount_of_likes_per_day, eff_privacy, key):
		sleep(2)
		amount_of_likes = 0
		#pagename_short = pagename.split("https://www.facebook.com/")[1]
		try: pagename_short = pagename_short.split("/")[0]
		except:pass
		# Check Chatbox element and delete it
		try:
			chatbox = self.driver.find_element(By.XPATH, '//div[@data-testid="mwchat-tabs"]')
			self.delete_element(chatbox)
		except NoSuchElementException: 
			pass

		if first_visit:
			# Like page
			write_log(get_date()+": "+"First visit on: "+pagename,key)
			#os.mkdir(os.getcwd()+'/'+"userdata/"+pagename_short)
			try:
				main_element = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]//div[@aria-label="Like"]')
				main_element.click()
			except: pass
			try:
				main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]//div[@aria-label="Like"]')
				main_element.click()
			except: pass
			try:
				main_element = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]//div[@aria-label="Follow"]')
				main_element.click()
			except: pass
			try:
				main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]//div[@aria-label="Follow"]')
				main_element.click()
			except: pass

		# Delete banner elements
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top: 56px;"]')
			self.delete_element(banner)
		except: pass
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]')
			self.delete_element(banner)
		except: pass
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]')
			self.delete_element(banner)
		except: pass
		banner_2 = self.driver.find_element(By.XPATH, '//div[@role="banner"]')
		self.delete_element(banner_2)

		# for adding a random value between -40% and +40% to the avg_amount_of_likes_per_day variable 
		random_addition = int(avg_amount_of_likes_per_day*0.4)
		random_break = random.randint(-random_addition,random_addition)

		# Connect to database
		conn = sqlite3.connect('userdata\\likes.db')
		c = conn.cursor()

		# Randomly like posts in an infinite while loop until broken
		last_element = ''
		while True:
			if chck_quitdriver(): break
			# Find article elements
			article_elements = self.driver.find_elements(By.XPATH, "//div[@class='lzcic4wl']")
			if last_element != '':
				indx = article_elements.index(last_element)
				article_elements = article_elements[indx+1:]

			# Go through every element
			for article_element in article_elements:
				if chck_quitdriver(): break
				last_element = article_element
				article_element.location_once_scrolled_into_view
				try:
					check_if_liked = article_element.find_element(By.XPATH, './/div[@aria-label="Remove Like"]')
					sleep(random.randint(3,7))
					if chck_quitdriver(): break
					continue
				except NoSuchElementException:
					pass
				sleep(random.randint(3,20))
				if chck_quitdriver(): break
				try:
					decide_like = bool(random.randint(0,1))
					if decide_like:
						# Find and focus a post element that uncovers the post url.
						link_element = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')
						action = ActionChains(self.driver)
						action.move_to_element(link_element).perform()
						if chck_quitdriver(): break
						sleep(3)
						dots_elemn = article_element.find_element(By.XPATH, './/div[@class="nqmvxvec j83agx80 jnigpg78 cxgpxx05 dflh9lhu sj5x9vvc scb9dxdr odw8uiq3"]')
						action.move_to_element(dots_elemn).perform()
						sleep(2)
						if chck_quitdriver(): break
						post_url = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
						post_url = post_url.split('__cft__')[0]
					
						# Save screenshot
						#data = article_element.screenshot_as_png
						#with open(os.getcwd()+'/'+"userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
						#	f.write(data)

						# Like post
						like_element = article_element.find_element(By.XPATH, './/div[@aria-label="Like"]')
						like_element.location_once_scrolled_into_view
						like_element.click()
						amount_of_likes += 1

						# Save post to database
						c.execute('INSERT INTO "' + aes_encrypt(pagename,key) + '" (post, time) \
								VALUES ("' + aes_encrypt(post_url,key) + '","' + get_date() + '")');
						conn.commit()
						write_log(get_date()+": "+"Liked {} post on page {}".format(post_url, pagename),key)
						sleep(random.randint(1,5))
						if chck_quitdriver(): break
						del action
				except Exception as e:
					print(get_date()+":","DEBUG:", e)

			# avg pages per day == 7. Break loop based on input privacy level.
			if amount_of_likes > ((avg_amount_of_likes_per_day + random_break) * (eff_privacy/0.5)) / 7:
				write_log(get_date()+": "+"Random loop break",key)
				break
			sleep(random.randint(3,10))
			if chck_quitdriver(): break

		conn.close()

	def take_screenshot(self, ):
		# Take a browser screenshot every second
		while not chck_quitdriver():
			if not chck_waitinglong():
				self.driver.save_screenshot(os.getcwd()+'\\'+".screenshot.png")
			sleep(1)
		
	def quit_bot(self, thread = None):
		# Exit webdriver
		self.driver.quit()
		if thread != None:
			thread.join()

#########################################################################################################################

class Userinterface(tk.Frame):

	def __init__(self, parent, key, *args, **kwargs):
		self.BOT_started = False
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent

		# Window options
		self.mainwindow.title("MetaPriv")
		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		self.mainwindow.grid_rowconfigure(0, weight=1)
		self.mainwindow.grid_rowconfigure(1, weight=1)
		self.mainwindow.grid_rowconfigure(2, weight=1)
		self.mainwindow.grid_rowconfigure(3, weight=1)
		self.mainwindow.grid_columnconfigure(0, weight=1)
		self.mainwindow.grid_columnconfigure(1, weight=1)
		self.mainwindow.grid_columnconfigure(2, weight=1)
		
		########### Canvas ###########
		self.canvas = tk.Canvas(self.mainwindow, width=1400, height=700, background=W)
		self.canvas.grid(row=1, column=0,columnspan=3)

		########### Slider ###########
		self.eff_privacy = tk.DoubleVar()
		tk.Label(self.mainwindow, text=INFO_TEXT, background=W,
			font=('TkFixedFont', 20, '')).grid(row=1, column=1,sticky='n')
		self.slider = tk.Scale(self.mainwindow,from_=10,to=100,orient='horizontal', background=W,
			variable=self.eff_privacy,tickinterval=10,sliderlength=20,resolution=5,length=1000,width=18,
			label='Privacy level:',font=15,troughcolor='grey',highlightbackground=W)#
		self.slider.set(55)
		self.slider.grid(column=0,row=1,sticky='sew', columnspan=3)

		########### Start button ###########
		self.start_button = tk.Button(self.mainwindow, text="Start", command= lambda: self.strt(key),
			font=10, background=W)
		self.start_button.grid(row=1,column=2,sticky='ne')
		
		########### Logs ###########
		self.grid(column=0, row=2, sticky='ew', columnspan=3)
		self.textbox = ScrolledText.ScrolledText(self,state='disabled', height=8, width=197, 
			background='black')
		self.textbox.configure(font=('TkFixedFont', 10, 'bold'),foreground='green')
		self.textbox.grid(column=0, row=2, sticky='w', columnspan=3)
		
	def get_last_log(self, key):
		# Get last line in bot_logs.log
		with open(os.getcwd()+'/'+'bot_logs.log','rb') as f:
			try:
				f.seek(-2, os.SEEK_END)
				while f.read(1) != b'\n':
					f.seek(-2, os.SEEK_CUR)
			except OSError:
				f.seek(0)
			last_line = f.readline().decode()
			last_line = aes_decrypt(last_line, key)
		return last_line

	def update_ui(self, key):
		if not chck_waitinglong():
			# Update logs
			last_log = self.get_last_log(key)
			if last_log != self.previous_last_log:
				self.textbox.configure(state='normal')
				self.textbox.insert(tk.END, last_log+"\n")
				self.textbox.configure(state='disabled')
			self.previous_last_log = last_log
			self.textbox.yview(tk.END)
			# Update screenshot
			try:
				photo = tk.PhotoImage(file=os.getcwd()+'\\'+".screenshot.png")
				self.screeshot_label.image = photo
				self.screeshot_label.config(image=photo)
				self.mainwindow.update_idletasks()
			except:
				#print("Image error")
				pass
		# Recursion
		self.mainwindow.after(2000,self.update_ui, key)

	def strt(self,key):
		# Get inputs
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Starting bot...\n")
		self.textbox.configure(state='disabled')
		priv = int(self.eff_privacy.get())
		# Start BOT on different core
		self.BOT = BOT()
		self.bot_process = mp.Process(target=self.BOT.start_bot,args=[priv, key])
		self.bot_process.start()
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Bot process started...\n")
		self.textbox.configure(state='disabled')
		self.BOT_started = True
		# Get the last log
		try: self.previous_last_log = self.get_last_log(key)
		except FileNotFoundError: sleep(3); self.previous_last_log = self.get_last_log(key)
		# Disable inputs
		self.start_button["state"] = "disabled"
		self.slider["state"] = "disabled"
		sleep(5)
		########### Screenshot ###########
		self.screeshot_label = tk.Label(self.mainwindow)
		self.screeshot_label.grid(row=1, column=0,columnspan=3)
		# Start recursive update
		self.mainwindow.after(0,self.update_ui, key)
		
	def close(self):
		self.mainwindow.destroy()
		open('breaksleep', 'w').close()
		if self.BOT_started:
			open('quitdriver', 'w').close() #chck_quitdriver() = True
			self.bot_process.join()
			try:
				os.remove(".screenshot.png")
			except FileNotFoundError:
				pass
		
#########################################################################################################################

def chck_quitdriver(): 
	try: open('quitdriver', 'r').close(); return True
	except: return False
def chck_breaksleep(): 
	try: open('breaksleep', 'r').close(); return True
	except: return False
def chck_waitinglong(): 
	try: open('waitinglong', 'r').close(); return True
	except: return False

def sleep(seconds, long_wait = False):
	if long_wait:
		open('waitinglong', 'w').close()
	time = 0
	while True:
		# Computation time. On average the waiting time == seconds parameter
		Sleep(1-0.003)
		time += 1
		if chck_breaksleep():
			break
		if time == seconds:
			break
	if long_wait:
		os.remove('waitinglong')

def new_page(pagename):
	# Add a new page to database
	conn = sqlite3.connect('userdata\\likes.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post] text PRIMARY KEY,
	              [time] date)'''.format(pagename))
	conn.commit()
	conn.close()

def new_keyword(keyword):
	# Add a new keyword to database
	conn = sqlite3.connect('userdata\\pages.db')
	c = conn.cursor()
	c.execute('INSERT INTO categories (category) \
			  		   VALUES (?)', [keyword])
	conn.commit()
	ID = c.lastrowid
	conn.close()
	return ID

def create_categ_table():
	# Create pages database to store page urls based on a keyword
	conn = sqlite3.connect('userdata\\pages.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE categories
	             ([ID] INTEGER PRIMARY KEY,
	              [category] text)''')
	c.execute('''CREATE TABLE pages
	             ([PID] INTEGER PRIMARY KEY,
	              [URL] text,
	              [categID] int)''')
	conn.commit()
	conn.close()

def rand_dist():
	# Return random ammount of seconds between 10s and 10h. High probability of 10s to 5h. Low probability of 5h to 10h.
	rand_number = random.randint(1,23)
	if rand_number in [1,2,3]:
		return random.randint(10,ONE_HOUR)
	elif rand_number in [4,5,6]:
		return random.randint(ONE_HOUR,2*ONE_HOUR)
	elif rand_number in [7,8,9,10]:
		return random.randint(2*ONE_HOUR,3*ONE_HOUR)
	elif rand_number in [11,12,13]:
		return random.randint(3*ONE_HOUR,4*ONE_HOUR)
	elif rand_number in [14,15,16]:
		return random.randint(4*ONE_HOUR,5*ONE_HOUR)
	elif rand_number in [17,18]:
		return random.randint(5*ONE_HOUR,6*ONE_HOUR)
	elif rand_number in [19,20]:
		return random.randint(6*ONE_HOUR,7*ONE_HOUR)
	elif rand_number in [21]:
		return random.randint(7*ONE_HOUR,8*ONE_HOUR)
	elif rand_number in [22]:
		return random.randint(8*ONE_HOUR,9*ONE_HOUR)
	elif rand_number in [23]:
		return random.randint(9*ONE_HOUR,10*ONE_HOUR)
		

def rand_fb_site():
	# Return a random FB site so GET while waiting
	marketplace = 'https://www.facebook.com/marketplace/?ref=bookmark'
	notifications = "https://www.facebook.com/notifications"
	friends = 'https://www.facebook.com/friends'
	settings = 'https://www.facebook.com/settings/?tab=account'
	welcome_pg = 'https://www.facebook.com/?sk=welcome'
	sites = [marketplace,notifications,friends,settings,welcome_pg]
	return sites[random.randint(0,4)]

def write_log(text,key):
	# Write and print logs
	print(text)
	with open(os.getcwd()+'\\'+"bot_logs.log",'a') as f:
		f.write('\n'+aes_encrypt(text,key))

def get_date():
	# Get formatted date for logs
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
	return formatted_date

def main():
	if os.path.isfile('running'): return
	open('running', 'w').close()
	# Check if program was launched before
	if not os.path.isfile(os.getcwd()+'\\'+'.saved_data'):
		first_launch = First_launch_UI()
		first_launch.start()
		key = first_launch.h_password
		del first_launch
	else: # If yes, prompt password
		check_pass = Enter_Password_UI(None)
		check_pass.title("Enter password")
		check_pass.resizable(False, False)
		check_pass.mainloop()
		key = check_pass.h_password
		check_pass.stop()
		del check_pass

	# Start main UI
	root = tk.Tk()
	root.resizable(False, False)
	Userinterface(root,key)
	root.mainloop()

	# Remove temp files
	for file in ['breaksleep','waitinglong','quitdriver','running']:
		try: os.remove(file)
		except FileNotFoundError: pass
	
main()