from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from typing import List, Set
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import hashlib

class BlueskyFilter:
    def __init__(self, driver: webdriver.Chrome, banwords: List[str]):
        self.driver = driver
        self.banwords = [word.lower() for word in banwords]
        self.processed_posts: Set[str] = set()

    def _get_post_id(self, post_text) -> str:
        """Generate unique ID using post text"""
        try:
            return hashlib.md5(bytes(post_text, "utf-8")).hexdigest()[:10]
        except StaleElementReferenceException:
            return str(time.time_ns())

    def _get_post_text(self, post_element) -> str:
        """Text extraction with multiple fallback methods"""
        try:
            return post_element.find_elements(By.XPATH, "//div[@data-testid='postText']")
        except (NoSuchElementException, StaleElementReferenceException):
            return ''

    def _contains_banword(self, text: str) -> bool:
        text = text.lower()
        print(f"{self.banwords} not in '{text}'")
        return any(banword in text for banword in self.banwords)

    def filter_posts(self) -> None:
        """Safe filtering with stale element handling"""
        try:
            posts = self.driver.find_elements(By.XPATH, "//div[@data-testid='feedItem-by-afpfr.bsky.social']")
            posts_text = [x.text for x in self.driver.find_elements(By.XPATH, "//div[@data-testid='postText']")]
            
            for i,post in enumerate(posts):
                try:
                    if not post.is_displayed():
                        continue

                    post_id = self._get_post_id(posts_text[i])
                    if post_id in self.processed_posts:
                        continue

                    post_text = posts_text[i]
                    
                    print(post_text)
                    if post_text and self._contains_banword(post_text):
                        self.driver.execute_script("arguments[0].remove();", post)  # Supprime l'élément du DOM
                        print("Post supprimé du DOM !")

                    self.processed_posts.add(post_id)
                except StaleElementReferenceException:
                    continue
        except Exception as e:
            print(f"Filter error: {str(e)[:100]}")

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

def main():
    BANWORDS = ["Amazon MGM", "Hamas à Gaza", "Luis Rubiales", "Olivier Faure"]
    PROFILE_URL = "https://bsky.app/profile/afpfr.bsky.social"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(options=options)
    driver.get(PROFILE_URL)
    driver.implicitly_wait(5)

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