from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def test_moodtune_basic_functionality():
    driver = webdriver.Chrome()
    driver.get('http://localhost:8000')
    
    try:
        # Test mood slider
        mood_slider = driver.find_element(By.ID, 'moodSlider')
        mood_slider.send_keys(Keys.RIGHT)
        
        # Test song input
        song_input = driver.find_element(By.ID, 'songInput')
        song_input.send_keys('Shape of You - Ed Sheeran')
        
        # Test save button
        save_button = driver.find_element(By.TAG_NAME, 'button')
        save_button.click()
        
        # Verify entry was created
        time.sleep(1)
        history = driver.find_element(By.ID, 'history')
        entries = history.find_elements(By.CLASS_NAME, 'entry')
        assert len(entries) == 1
        assert 'Shape of You - Ed Sheeran' in entries[0].text
        
        print('All tests passed!')
        
    finally:
        driver.quit()

if __name__ == '__main__':
    test_moodtune_basic_functionality()