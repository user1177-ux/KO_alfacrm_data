import requests
import csv
import os
from datetime import datetime

def fetch_leads_status():
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

        # Запрос логов для получения лидов
        logs_url = f'https://{hostname}/v2api/log/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

        lead_ids = set()
        page = 0
        per_page = 100

        while True:
            logs_params = {
                'filters': {
                    'entity': 'customer'
                },
                'page': page,
                'per-page': per_page
            }

            response = requests.post(logs_url, headers=headers, json=logs_params)

            if response.status_code == 200:
                logs = response.json().get('items', [])
                if not logs:
                    break

                for log in logs:
                    if 'fields_new' in log:
                        for field in log['fields_new']:
                            if 'lead_status_id' in field:
                                lead_ids.add((log['entity_id'], field['lead_status_id']))

                page += 1
            else:
                print('Ошибка получения логов:', response.text)
                break

        # Сохранение данных в CSV файл
        with open('leads_status.csv', 'w', newline='') as csvfile:
            fieldnames = ['Lead ID', 'Status ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for lead_id, status_id in lead_ids:
                writer.writerow({'Lead ID': lead_id, 'Status ID': status_id})
        
        print('Список ID лидов сохранен в leads_status.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads_status()
