from datetime import datetime
from typing import List

from aiogoogle import Aiogoogle
from app.core.config import settings
from app.models import CharityProject

FORMAT = '%Y/%m/%d %H:%M:%S'
SHEET_TYPE = 'GRID'
LOCALE = 'ru_RU'
SHEET_ID = 0
TITLE = 'Лист1'
ROW_COUNT = 100
COLUMN_COUNT = 10

TYPE = 'user'
ROLE = 'writer'
EMAIL = settings.email

MAJOR_DIMENSION = 'ROWS'
RANGE = 'A1:E30'
VALUE_INPUT_OPTION = 'USER_ENTERED'


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    body = {
        'properties': {
            'title': f'Отчёт от {now_date_time}',
            'locale': LOCALE
        },
        'sheets': [{
            'properties': {
                'sheetType': SHEET_TYPE,
                'sheetId': SHEET_ID,
                'title': TITLE,
                'gridProperties': {
                    'rowCount': ROW_COUNT, 'columnCount': COLUMN_COUNT
                }
            }
        }]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle
) -> None:
    body = {
        'type': TYPE,
        'role': ROLE,
        'emailAddress': EMAIL
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=body,
            fields="id"
        )
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    projects: List[CharityProject],
    wrapper_services: Aiogoogle
) -> None:

    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in projects:
        new_row = [
            str(project.name),
            str(project.close_date - project.create_date),
            str(project.description)
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': MAJOR_DIMENSION,
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=RANGE,
            valueInputOption=VALUE_INPUT_OPTION,
            json=update_body
        )
    )
