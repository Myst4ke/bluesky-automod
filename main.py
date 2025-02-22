from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import hashlib
import os
from dotenv import load_dotenv
from blocklist import get_following_list, get_users_from_list, login

load_dotenv()
viral_like_threshold = 100
viral_repost_threshold = 100

class BlueskyFilter:
    def __init__(self, driver: webdriver.Chrome, banwords: list[str]):
        self.driver = driver
        self.banwords = [word.lower() for word in banwords]
        self.processed_posts: set[str] = set()
        self.client = login()

    def _get_post_id(self, post_text:str) -> str:
        """Generate unique ID using post text"""
        try:
            return hashlib.md5(bytes(post_text, "utf-8")).hexdigest()[:10]
        except StaleElementReferenceException:
            return str(time.time_ns())
        
    def _get_post_author(self, post_element) -> str:
        try:
            authorProfileLink = post_element.find_elements(By.XPATH, ".//a[@aria-label='View profile']")
            return authorProfileLink[0].get_attribute("href").split('/')[-1]
        except (NoSuchElementException, StaleElementReferenceException):
            return ''
    
    def _get_post_link(self, post_element) -> str:
        try:
            return post_element.find_elements(By.XPATH, ".//a[starts-with(@href, '/profile/') and contains(@href, '/post/')]")[0].get_attribute("href")
        except (NoSuchElementException, StaleElementReferenceException):
            return ''
    
    def _get_post_text(self, post_element) -> str:
        """Returns the text of the given post"""
        try:
            return post_element.find_elements(By.XPATH, ".//div[@data-testid='postText']")[0].text
        except (NoSuchElementException, StaleElementReferenceException):
            return ''
        
    def _get_repost_and_like_count(self, post_element) -> tuple[str, str]:
        """
        Extrait le nombre de reposts et de likes d'un post.

        :param post_element: L'élément Web du post (WebElement Selenium)
        :return: Tuple (nombre de reposts, nombre de likes)
        """
        try:
            # Chercher la div contenant le nombre de reposts
            repost_div = post_element.find_element(By.XPATH, ".//div[@data-testid='repostCount']")
            repost_count = repost_div.text
        except:
            repost_count = None  # Aucun repost trouvé

        try:
            # Chercher la div contenant le nombre de likes
            like_div = post_element.find_element(By.XPATH, ".//div[@data-testid='likeCount']")
            like_count = like_div.text
        except:
            like_count = None  # Aucun like trouvé

        return repost_count, like_count

    def _is_viral(self, post_element):
        repost_count, like_count = self._get_repost_and_like_count(post_element)
        return repost_count > 500 or like_count > 500
    
    def _is_in_blocking_list(self, username):
        blocklist = get_users_from_list(self.client, "block list")
        return username in blocklist
    
    def _is_in_blocking_list(self, username):
        followingList = get_following_list(self.client, os.environ['BSKY_HANDLE'])
        return username in followingList
    
    def _contains_banword(self, text: str) -> bool:
        text = text.lower()
        # print(f"{self.banwords} not in '{text}'")
        return any(banword in text for banword in self.banwords)
    
    def is_following_blocked_account(self, threshold=5):
        followingList = get_following_list(self.client, os.environ['BSKY_HANDLE'])
        blocklist = get_users_from_list(self.client, "block list")
        intersec = len(set(followingList) & set(blocklist))
        return (intersec /len(followingList)) *100 > threshold
    
    def filter_posts(self) -> None:
        """Safe filtering with stale element handling"""
        try:
            posts = self.driver.find_elements(By.XPATH, "//div[starts-with(@data-testid, 'feedItem-by-')]")
            # posts = self.driver.find_elements(By.XPATH, "//div[@data-testid='feedItem-by-afpfr.bsky.social']")
            
            for post in posts:
                try:
                    if not post.is_displayed():
                        continue

                    post_text = self._get_post_text(post)
                    post_id = self._get_post_id(post_text)
                    
                    if post_id in self.processed_posts:
                        continue
                    
                    if post_text and self._contains_banword(post_text):
                        print(f"Trying to delete : {post_text[:25]}...  by {self._get_post_author(post)}, post link : {self._get_post_link(post)}")
                        self.driver.execute_script("arguments[0].remove();", post)  # Supprime l'élément du DOM
                        print("Post supprimé du DOM !")

                    self.processed_posts.add(post_id)
                except StaleElementReferenceException:
                    continue
        except Exception as e:
            print(f"Filter error: {str(e)[:100]}")
            raise(e)

def monitor_user_scroll(driver: webdriver.Chrome, filter_instance: BlueskyFilter) -> None:
    """Détection passive du scroll utilisateur"""
    last_scroll = driver.execute_script("return window.pageYOffset;")
    
    while True:
        current_scroll = driver.execute_script("return window.pageYOffset;")
        
        # Se déclenche seulement si l'utilisateur a scrollé
        if current_scroll != last_scroll:
            time.sleep(1)  # Laisse le temps au contenu de se charger
            filter_instance.filter_posts()
            last_scroll = current_scroll
        
        time.sleep(0.5)  # Vérification moins fréquente

def login_to_bluesky(driver, username, password):
    """
    Se connecte à Bluesky avec un identifiant et un mot de passe.
    
    :param driver: WebDriver Selenium
    :param username: Identifiant ou adresse email
    :param password: Mot de passe
    """

    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Sign in']"))
    )
    sign_in_button.click()


    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username or email address']"))
    )

    username_input = driver.find_element(By.XPATH, "//input[@placeholder='Username or email address']")
    username_input.send_keys(username)

    password_input = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
    password_input.send_keys(password)

    next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
    next_button.click()

    print("Connexion en cours...")




def main():
    BANWORDS = ["Amazon MGM", "Hamas à Gaza", "Luis Rubiales", "Olivier Faure", "trump"]
    PROFILE_URL = "https://bsky.app/profile/afpfr.bsky.social"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(options=options)
    driver.get(PROFILE_URL)
    driver.implicitly_wait(5)
    login_to_bluesky(driver, os.environ['BSKY_HANDLE'], os.environ['BSKY_APP_PASSWORD'])   
    
    filter_instance = BlueskyFilter(driver, BANWORDS)
    filter_instance.filter_posts()  # Filtrage initial
    try:
        monitor_user_scroll(driver, filter_instance)
    except KeyboardInterrupt:
        print("\nArrêt propre de l'application...")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()