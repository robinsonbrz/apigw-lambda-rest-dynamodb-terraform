def get_first_movie_id(sget):
    response = sget("/movies")
    movies_list = response.json()
    first_movie = movies_list[0]['id']['S']
    return first_movie

first_movie = get_first_movie_id()


def test_get_movies_should_return_200(sget):
    # GET all movies
    response = sget("/movies")
    assert response.status_code == 200

def test_get_movie_by_id_should_return_200(sget):
    response = sget(f"/movies/{first_movie}")
    assert response.status_code == 200

def test_get_movie_by_wrong_id_should_return_404(sget):
    response = sget("/movies/erroneous-id")
    assert response.status_code == 404

