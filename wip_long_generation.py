"""
@file wip_long_generation.py
@author qu-gg

This is a WIP version where we generate longer songs automatically using the "Continue from..." and "Whole song"
buttons on the interface to generate ~2min clips. It is more involved and the current implementation is awkward.

Unsure on the generation and merging times here as 1) lyrics generation in the program takes 6-10s and
2) two generations easily take 25-45s each while the total output ranges from 104-180s. Likely some waiting
will occur in a true online version.

The current version as-is here uses a weird 2-tab system instead of the grid-list like app.py does.
It needs to be changed over so the hopping between isn't as bad.

It currently does not take lyric or genre input, using the given random generations.
"""
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_latest_action(driver):
    """ Helper function to find the last song in the list and click its 'extras' bar """
    elements = driver.find_elements(By.XPATH, f"//*[@aria-label='More Actions']")[:-2]
    return elements[-1]


def generate_lyrics(driver):
    """ Handles interacting with the lyrics box, clearing it and making random lyrics """
    # Clear the textarea
    for textarea in driver.find_elements(By.TAG_NAME, 'textarea'):
        if 'Enter your own' in textarea.get_property('placeholder'):
            textarea.click()
            textarea.send_keys(Keys.CONTROL + "a")
            textarea.send_keys(Keys.DELETE)
            break

    # Generate new lyrics
    for button in driver.find_elements(By.TAG_NAME, 'button'):
        if button.text == "Make Random Lyrics":
            button.click()
            sleep(10)
            break


def generate_title(driver):
    """ Unused currently, wipes the title but needs to be changed to put in a random title """
    for textarea in driver.find_elements(By.TAG_NAME, 'textarea'):
        if 'Enter a title' in textarea.get_property('placeholder'):
            textarea.click()
            textarea.send_keys(Keys.CONTROL + "a")
            textarea.send_keys(Keys.DELETE)
            break


def create_song(driver, style=None):
    """ Main song creation method, generating both song sets and merging them together """
    # Clear lyrics
    print("=> Generating first lyrics...")
    generate_lyrics(driver)

    # Check for previous Continue
    for button in driver.find_elements(By.TAG_NAME, 'button'):
        if button.text == "Clear":
            button.click()
            break

    # Create or set style
    if style is not None:
        for button in driver.find_elements(By.TAG_NAME, 'button'):
            if button.text == "Use Random Style":
                button.click()
                break
        sleep(1)

    # Generate the song
    # TODO change this sleep to not have a static time but wait until some HTML element is complete
    for button in driver.find_elements(By.TAG_NAME, 'button'):
        if button.text == "Create":
            button.click()
            break
    print(f"=> Creating first part...")
    sleep(75)

    # Generate new lyrics for second half
    print(f"=> Generating second lyric set...")
    generate_lyrics(driver)

    # Click on the latest actions
    get_latest_action(driver).click()
    sleep(2)

    # Click the continue button
    for menu in driver.find_elements(By.XPATH, f"//*[@role='menuitem']"):
        if "Continue From This Song" in menu.text:
            menu.click()
            sleep(2)
            break

    # Generate part 2
    # TODO change this sleep to not have a static time but wait until some HTML element is complete
    for button in driver.find_elements(By.TAG_NAME, 'button'):
        if button.text == "Continue":
            button.click()
            break
    print(f"=> Creating second part...")
    sleep(75)

    # Click on the latest actions
    get_latest_action(driver).click()
    sleep(2)

    # Get the merge song button
    print(f"=> Merging...")
    for menu in driver.find_elements(By.XPATH, f"//*[@role='menuitem']"):
        if "Whole" in menu.text:
            menu.click()
            break


def get_song_info(driver):
    """ As-is, little loaded and useless function that could be removed if we get rid of the 2-tab system """
    # Song info dict
    song_info = dict()

    # Get the song name
    for header in driver.find_elements(By.TAG_NAME, 'h2'):
        if header.aria_role == "heading":
            song_info["name"] = header.text

    # Get the song info
    for paragraph in driver.find_elements(By.TAG_NAME, 'p'):
        # Date text will for the next 2 years include these years, safe bet
        if any(paragraph.text.__contains__(o) for o in [', 2023', ', 2024', ', 2025']):
            song_info["date"] = paragraph.text

        # If \n in text, then likely the lyrics
        elif '\n' in paragraph.text:
            song_info["lyrics"] = paragraph.text

        # Tags have a specific element size in the selenium
        # TODO change to something better
        elif paragraph.size['height'] == 24 and paragraph.size['width'] == 445:
            song_info["tags"] = paragraph.text

        # Song length reference
        elif paragraph.text == "0:00":
            song_info['length_object'] = paragraph

    # Get the play button
    for button in driver.find_elements(By.TAG_NAME, 'button'):
        if button.text == "Play":
            song_info['button'] = button

    # Return the song and its info
    return song_info


def open_latest_song(driver):
    """ Handles opening the latest song in a new tab """
    # Get all links
    elements = driver.find_elements(By.XPATH, f"//*[contains(@class, 'chakra-link')]")

    # Restrict to song hrefs
    song_links = []
    for element in elements:
        if '/song/' in element.get_property('href'):
            song_links.append(element.get_property('href'))

    # Cut out the song player at the bottom and song info on the side
    song_links = song_links[:-3]
    print(f"=> Latest song: {song_links[-1]}")

    # Open and switch to the new tab with the dedicated music
    driver.execute_script("window.open(arguments[0]);", song_links[-1])
    driver.switch_to.window(driver.window_handles[-1])
    sleep(1)
    driver.refresh()
    sleep(1)


def main(driver, live=False):
    """ Main driver function, handles tab management and playing songs """
    # Make sure we are on the main tab
    driver.switch_to.window(driver.window_handles[0])
    sleep(1)

    # Loop over, generating X number of songs on the fly
    for song_idx in range(5):
        try:
            # Refresh the page
            driver.refresh()
            sleep(2)

            # Open the latest song
            open_latest_song(driver)
            sleep(2)

            # Get the song info
            info = get_song_info(driver)
            sleep(2)
            print(info)

            # Select to repeat the song in case of over-generation
            repeat = driver.find_elements(By.XPATH, f"//*[@aria-label='Toggle Repeat One']")
            repeat[0].click()
            sleep(2)

            # Play the current song
            info['button'].click()
            sleep(2)

            # Get its length
            minutes, seconds = info['length_object'].text.split(":")
            song_length = (int(minutes) * 60) + int(seconds)

            # Log playing
            print(f"=> Playing latest song: [{info['name']} | {song_length}s]")

            # Create a new song while the current one is playing
            if live is True:
                print(f"=> Creating song...")
                driver.switch_to.window(driver.window_handles[0])
                sleep(1)

                create_song(driver)

                # Sleep for remaining song length
                print(f"=> Now sleeping for {song_length - 136}s...")
                sleep(max(1, song_length - 136))
            else:
                sleep(song_length)
        except Exception as e:
            print(f"=> Error: {e}")

        # Close song tab
        driver.switch_to.window(driver.window_handles[-1])
        sleep(1)
        driver.close()

        # Switch to base tab
        driver.switch_to.window(driver.window_handles[0])
        sleep(1)


if __name__ == '__main__':
    # Initialize the WebDriver
    global_driver = webdriver.Chrome()  # Adjust if using a different browser
    global_driver.get("https://app.suno.ai/create/")

    # We wait on input as it takes an unknown time to log into the service
    input("Enter to continue...")

    # Run the service
    main(global_driver, live=True)
