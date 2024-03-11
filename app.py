"""
@file app.py
@author qu-gg

Essentially builds a Selenium service interactor with Suno that handles actively generating
and playing songs while current ones play. The loop is that the next song to play will not
be pre-selected.

Generations of 30-60s clips only take about 25s on average so there is no real downtime
in this online approach. It currently does not consider genre or description inputs.
"""
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By


def play_latest_song(driver):
    """
    On the /create page, get the gridlip associated with the songs - denoted by the aria-label 'X CLips'
    Get the button of the latest Play button in that list and click it
    """
    # Song list
    gridlist = driver.find_element(By.XPATH, f"//*[contains(@aria-label, 'Clips')]")

    # Get the list of buttons
    button_list = []
    for button in gridlist.find_elements(By.TAG_NAME, "button"):
        if button.get_attribute("aria-label") == "Play" or button.get_attribute("aria-label") == "Pause":
            button_list.append(button)

    # Play the current song
    button_list[-1].click()
    sleep(0.5)


def main(driver):
    """
    Main loop of the program where songs are generated and played online.
    It requires at least one song in the /create queue to get started.
    """
    # Make sure we're at the base window
    driver.switch_to.window(driver.window_handles[0])

    # Play the latest song
    play_latest_song(driver)

    # Generate infinite songs
    while True:
        # Create a new song while the current one is playing
        print(f"=> Creating song...")
        for button in driver.find_elements(By.TAG_NAME, 'button'):
            if button.text == "Create":
                button.click()
                break

        # Sleep
        sleep(30)

        # Wait until playtime is over
        playbar = driver.find_element(By.XPATH, f"//*[contains(@type, 'hidden')]")
        while playbar.get_attribute('value') != "100":
            sleep(0.25)
            continue

        # Refresh here to get new prompt before next song
        driver.refresh()
        sleep(1)

        # Turn off autoplay just to stop queue weirdness during the transition
        driver.find_element(By.XPATH, f"//*[@aria-label='Toggle Autoplay']").click()
        sleep(0.25)

        # Play the latest song
        play_latest_song(driver)


if __name__ == '__main__':
    # Initialize the WebDriver
    global_driver = webdriver.Chrome()  # Adjust if using a different browser
    global_driver.get("https://app.suno.ai/create/")

    # We wait on input as it takes an unknown time to log into the service
    input("Enter to continue...")

    # Run the service
    main(global_driver)
