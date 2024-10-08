import requests
import json
import csv
import os
from datetime import datetime

def fetch_leads_with_status_and_source():
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
        
        customers_url = f'https://{hostname}/v2api/1/customer/index'
        headers = {'X-ALFACRM-TOKEN': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        
        data = {
            "page": 0,  # Начальная страница
            "is_study": 0,
            "removed": 1  # Включить архивных клиентов
        }
        
        all_customers = []

        while True:
            response = requests.post(customers_url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                customers = response.json().get('items', [])
                if not customers:
                    break
                all_customers.extend(customers)
                data['page'] += 1
            else:
                print(f'Ошибка получения данных клиентов: {response.text}')
                break
            
        # Сохранение данных в CSV файл
        with open('leads_statuses_sources.csv', 'w', newline='') as csvfile:
            fieldnames = ['lead_id', 'status_id', 'lead_source_id', 'e_date', 'lead_reject_id', 'custom_datarezidentstva']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for customer in all_customers:
                writer.writerow({
                    'lead_id': customer.get('id'),
                    'status_id': customer.get('lead_status_id'),
                    'lead_source_id': customer.get('lead_source_id'),
                    'e_date': customer.get('e_date'),
                    'lead_reject_id': customer.get('lead_reject_id'),
                    'custom_datarezidentstva': customer.get('custom_datarezidentstva')  # Новое поле datano
                })
            writer.writerow({'lead_id': 'Last updated', 'status_id': '', 'lead_source_id': '', 'e_date': '', 'lead_reject_id': '', 'custom_datarezidentstva': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

        print('Список клиентов с их текущими статусами и источниками сохранен в leads_statuses_sources.csv')
    else:
        print('Ошибка авторизации:', response.text)

if __name__ == "__main__":
    fetch_leads_with_status_and_source()
