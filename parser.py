from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta
import time

# Функция для получения событий с определенной даты
def get_events(date):
    url = f"https://kudago.com/msk/events/?date={date}&page=1"
    events = []
    page = 1

    while True:
        driver.get(url.replace('page=1', f'page={page}')) # Ждем загрузки JS

        event_cards = driver.find_elements(By.CLASS_NAME, 'post-content')  # Обновите этот селектор

        if not event_cards:
            break

        for card in event_cards:
            try:
                title = card.find_element(By.CLASS_NAME, 'post-header').text.strip()  # Обновите в зависимости от структуры HTML
            except:
                title = ''
            try:
                place = card.find_element(By.CLASS_NAME, 'post-detail--event-place').text  # Обновите в зависимости от структуры HTML
            except:
                place = ''

            try:
                urlLink = card.find_element(By.CLASS_NAME, "link-secondary").get_attribute('href')
                driver.execute_script("window.open('');")  # Открываем новую вкладку
                driver.switch_to.window(driver.window_handles[1])  # Переключаемся на новую вкладку  
                driver.get(urlLink)   
                schedule = driver.find_element(By.CLASS_NAME, 'post-big-details-schedule')
                dates = schedule.find_elements(By.TAG_NAME, 'tr')
                for event_date in dates:
                    if "–" in event_date.text:
                        start_date, end_date = event_date.text.split('–',1)
                    else:
                        start_date = event_date.text
                        end_date = ''
                    events.append((date, title, place, start_date, end_date))
                driver.close()  # Закрываем новую вкладку
                driver.switch_to.window(original_window)  # Возвращаемся на оригинальную вкладку
                
            except Exception as ex:
                dates = card.find_elements(By.CLASS_NAME, 'date-item')
                for event_date in dates:
                    if "–" in event_date.text:
                        start_date, end_date = event_date.text.split('–',1)
                    else:
                        start_date = event_date.text
                        end_date = ''
                    events.append((date, title, place, start_date, end_date))
        page += 1

    return events

# Основная функция
def main():
    global driver, original_window
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    original_window = driver.current_window_handle
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    all_events = []

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"Получение событий для {date_str}...")
        events = get_events(date_str)
        all_events.extend(events)
        current_date += timedelta(days=1)

    # Запись данных в Excel
    df = pd.DataFrame(all_events, columns=['Дата', 'Название', 'Место', 'Дата с', 'Дата по'])
    df.to_excel('events_2024.xlsx', index=False)
    print("Данные записаны в файл events_2024.xlsx")

    driver.quit()  # Закрываем браузер

if __name__ == "__main__":
    main()