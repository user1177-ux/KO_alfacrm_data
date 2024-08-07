import requests
import csv
import os

def fetch_lesson_types():
    email = os.getenv('ALPHA_CRM_EMAIL')
    api_key = os.getenv('ALPHA_CRM_API_KEY')
    hostname = os.getenv('ALPHA_CRM_HOSTNAME')

    # Авторизация
    auth_url = f'https://{hostname}/v2api/auth/login'
    auth_data = {'email': email, 'api_key': api_key}
    response = requests.post(auth_url, json=auth_data)

    if response.status_code == 200:
        token = response.json().get('token')
        print('Токен:', token)
        
        # Запрос типов уроков
        lesson_types_url = f'https://{hostname}/v2api/1/lesson-type/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        response = requests.post(lesson_types_url, headers=headers)

        if response.status_code == 200:
            lesson_types = response.json().get('items', [])
            
            # Сохранение данных в CSV файл
            with open('lesson_types.csv', 'w', newline='') as csvfile:
                fieldnames = ['ID', 'Name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for lesson_type in lesson_types:
                    writer.writerow({'ID': lesson_type['id'], 'Name': lesson_type['name']})
            print('Список типов уроков сохранен в lesson_types.csv')
        else:
            print('Ошибка получения типов уроков:', response.text)
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_lesson_types()
