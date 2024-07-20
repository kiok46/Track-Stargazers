import json

# Загрузка данных из файлов
with open('stargazers.json', 'r') as stargazers_file:
    stargazers = json.load(stargazers_file)

with open('jsons/data_0.json', 'r') as data_file:
    users_info = json.load(data_file)


# Функция для поиска пользователей с информацией "Location not found"
def find_users_with_location_not_found(stargazers, users_info):
    user_dict = {user["user"]: user for user in users_info["users"]}
    users_with_location_not_found = []

    for stargazer in stargazers:
        if stargazer in user_dict and user_dict[stargazer].get("country") == "Location not found":
            users_with_location_not_found.append(stargazer)

    return users_with_location_not_found


# Поиск пользователей
users_with_location_not_found = find_users_with_location_not_found(stargazers, users_info)


# Сохранение результатов в JSON-файл
output_file_path = 'users_with_location_not_found.json'
with open(output_file_path, 'w') as output_file:
    json.dump(users_with_location_not_found, output_file, indent=4)

print(f"Users with 'Location not found' have been saved to {output_file_path}")
