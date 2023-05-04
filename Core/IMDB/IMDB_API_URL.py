import requests

API_Key = 'k_cyxla4fq'

GetTop250_URL = 'https://imdb-api.com/en/API/Top250Movies/{0}'.format(API_Key)


def SearchByTitle(title):
    GetWithTitle_URL = 'https://imdb-api.com/en/API/SearchTitle/{0}/{1}'.format(API_Key, title)
    response = requests.get(GetWithTitle_URL)
    data = response.json()
    Movies = []

    if data['results'] == [] or data['errorMessage'] != "":
        return "فیلمی با این عنوان {0} یافت نشد".format(title)
    else:
        for item in data['results']:
            Movies.append(item)
        return Movies


def SearchByGenres(genre):
    SearchWithGenres_URL = 'https://imdb-api.com/API/AdvancedSearch/{0}?genres={1}'.format(API_Key, genre)
    response = requests.get(SearchWithGenres_URL)
    data = response.json()
    Movies = []

    if data['results'] == [] or data['errorMessage'] is not None:
        return 'فیلمی یافت نشد!'
    else:
        for item in data['results']:
            Movies.append(item)
        return Movies


def GetMovieDetails(id):
    MovieDetailes_URL = 'https://imdb-api.com/en/API/Title/{0}/{1}/Trailer'.format(API_Key, id)
    response = requests.get(MovieDetailes_URL)
    data = response.json()
    return data
