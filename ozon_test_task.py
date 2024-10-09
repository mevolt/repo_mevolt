# Импортируем модуль random для работы со случайными значениями
import random

# Импортируем библиотеку для тестирования
import pytest

# Импортируем библиотеку для работы с HTTP-запросами
import requests

# Определяем класс для работы с загрузкой файлов на Яндекс.Диск
class YaUploader:
    # Конструктор класса, здесь он пустой
    def init(self):
        pass

    # Метод для создания папки на Яндекс.Диске
    def create_folder(self, path, token):
        # URL для создания ресурса (папки)
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
        # Заголовки запроса, включая авторизацию
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        # Выполняем PUT-запрос для создания папки
        response = requests.put(f'{url_create}?path={path}', headers=headers)

    # Метод для загрузки фото на Яндекс.Диск
    def upload_photos_to_yd(self, token, path, url_file, name):
        # URL для загрузки файла
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        # Заголовки запроса, включая авторизацию
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        # Параметры запроса, включая путь и URL файла для загрузки
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        # Выполняем POST-запрос для загрузки файла
        resp = requests.post(url, headers=headers, params=params)

# Функция для получения списка подвидов собак указанной породы
def get_sub_breeds(breed):
    # Выполняем GET-запрос к API, чтобы получить список подвидов
    res = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
    # Возвращаем список подвидов, если он есть
    return res.json().get('message', [])

# Функция для получения URL изображений для указанной породы и её подвидов
def get_urls(breed, sub_breeds):
    # Список для хранения URL изображений
    url_images = []
    # Если имеются подвиды
    if sub_breeds:
        # Для каждого подвида
        for sub_breed in sub_breeds:
            # Выполняем GET-запрос для получения случайного изображения подвида
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            # Получаем URL изображения и добавляем его в список
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        # Если подвидов нет, получаем одно случайное изображение для породы
        url_images.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json().get('message'))
    # Возвращаем список URL изображений
    return url_images

# Функция для загрузки изображений собак на Яндекс.Диск
def u(breed):
    # Получаем подвиды для указанной породы
    sub_breeds = get_sub_breeds(breed)
    # Получаем URL изображений для породы и её подвидов
    urls = get_urls(breed, sub_breeds)
    # Создаем экземпляр класса для работы с Яндекс.Диском
    yandex_client = YaUploader()
    # Создаем папку на Яндекс.Диске
    yandex_client.create_folder('test_folder', "AgAAAAAJtest_tokenxkUEdew")
    # Для каждого URL изображения
    for url in urls:
        # Разбиваем URL на части и создаем имя файла
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        # Загружаем изображение на Яндекс.Диск
        yandex_client.upload_photos_to_yd("AgAAAAAJtest_tokenxkUEdew", "test_folder", url, name)

# Тестовая функция, проверяющая загрузку изображений собак
@pytest.mark.parametrize('breed', ['doberman', random.choice(['bulldog', 'collie'])])
def test_proverka_upload_dog(breed):
    # Вызываем функцию загрузки изображений
    u(breed)
    # URL для проверки ресурса (папки)
    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    # Заголовки запроса,


включая авторизацию
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth AgAAAAAJtest_tokenxkUEdew'}
    # Выполняем GET-запрос, чтобы получить информацию о папке
    response = requests.get(f'{url_create}?path=/test_folder', headers=headers)
    # Проверяем, что папка создана и она имеет правильное имя
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == "test_folder"
    # Проверка всегда проходит
    assert True
    # Если у породы нет подвидов
    if get_sub_breeds(breed) == []:
        # Проверяем, что в папке только один файл
        assert len(response.json()['_embedded']['items']) == 1
        # Для каждого элемента в папке проверяем, что это файл с корректным именем
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)
    else:
        # Если у породы есть подвиды, проверяем количество файлов и имена аналогично
        assert len(response.json()['_embedded']['items']) == len(get_sub_breeds(breed))
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)
