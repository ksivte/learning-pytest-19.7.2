import os
from api import PetFriends
from settings import valid_email, valid_password, wrong_email, wrong_password, wrong_auth_key

pf = PetFriends()


def test_get_api_key_valid_user(email=valid_email, password=valid_password):  # получение api key для корректных данных пользователя
    status, result = pf.get_api_key(email, password) # получаем ключ auth_key
    assert status == 200  # проверка, что статус ответа равен 200
    assert 'key' in result


def test_get_api_key_wrong_user(email=wrong_email, password=wrong_password):  # попытка получения api key для некорректных данных пользователя (пользователь отсутствует в БД)
    status, result = pf.get_api_key(email, password) # попытка получить ключ auth_key
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_get_api_key_wrong_password(email=valid_email, password=wrong_password):  # попытка получения api key для корректного логина с некорректным паролем
    status, result = pf.get_api_key(email, password)  # попытка получить ключ auth_key
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_get_all_pets_with_valid_key(filter=''):  # получение всего списка питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    status, result = pf.get_list_of_pets(auth_key, filter)  # получаем список своих питомцев
    assert status == 200  # проверка, что статус ответа равен 200
    assert len(result['pets']) > 0


def test_get_all_pets_with_wrong_key(filter=''):  # попытка получить список питомцев с некорректным api key
    status, result = pf.get_list_of_pets(wrong_auth_key, filter)  # попытка получить список питомцев
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_get_all_pets_with_wrong_filter(filter='test'):  # попытка получить список питомцев с некорректным фильтром
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    status, result = pf.get_list_of_pets(auth_key, filter)  # попытка получить список своих питомцев
    assert status == 500  # проверка, что статус ответа равен 500
    assert 'Server Error' in result


def test_add_new_pet_with_valid_data(name='Пепе', animal_type='синица', age='2', pet_photo='images/parrot.jpeg'):  # создание нового питомца с корректными данными
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo) # попытка добавить питомца
    assert status == 200  # проверка, что статус ответа равен 200
    assert result['name'] == name


def test_add_new_pet_with_wrong_api_key(name='Пепе', animal_type='синица', age='2', pet_photo='images/parrot.jpeg'):  # попытка создания нового питомца с некорректным api key
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.add_new_pet(wrong_auth_key, name, animal_type, age, pet_photo)  # попытка добавить питомца
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_add_new_pet_with_large_image(name='Пепе', animal_type='кит', age='1', pet_photo='images/whale.jpeg'):  # создание нового питомца с большим объемом изображения (> 3,5 мб)
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo) # попытка добавить питомца
    assert status == 200  # проверка, что статус ответа равен 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Тест', animal_type='попугай', age=3):  # обновление информации о питомце
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")  # получаем список своих питомцев

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200  # проверка, что статус ответа равен 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")


def test_unsuccessful_update_self_pet_info_with_wrong_api_key(name='Тест', animal_type='Тест', age=3):  # попытка обновления информации о питомце с некорректным api key
    pet_id = '0'
    status, result = pf.update_pet_info(wrong_auth_key, pet_id, name, animal_type, age)
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_unsuccessful_update_self_pet_info_with_wrong_id(name='Тест', animal_type='Тест', age=3):  # попытка обновления информации о питомце с некорректным id
    pet_id = 'test'
    status, result = pf.update_pet_info(wrong_auth_key, pet_id, name, animal_type, age)
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_successful_delete_self_pet():  # проверка удаления питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")  # получаем список питомцев
    if len(my_pets['pets']) == 0:  # если список питомцев пуст, то добавляем нового и опять запрашиваем список своих питомцев
        pf.add_new_pet(auth_key, "Тест", "попугай", "2", "images/parrot.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']  # берём id первого питомца из списка и отправляем запрос на удаление
    status, _ = pf.delete_pet(auth_key, pet_id)
    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200  # проверка, что статус ответа равен 200
    assert pet_id not in my_pets.values()  # проверка, что в списке нет id удалённого питомца


def test_unsuccessful_delete_self_pet_with_wrong_api_key():  # попытка удаления питомца с некорректным api key
    status, result = pf.delete_pet(wrong_auth_key, pet_id='0')
    assert status == 403  # проверка, что статус ответа равен 403
    assert 'Forbidden' in result


def test_successful_delete_self_pet_with_wrong_id():  # попытка удаления отсутствующего в базе питомца
    _, auth_key = pf.get_api_key(valid_email, valid_password)  # получаем ключ auth_key
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")  # получаем список питомцев
    pet_id = 'test'
    status, result = pf.delete_pet(auth_key, pet_id)
    assert status == 200  # проверка, что статус ответа равен 200

