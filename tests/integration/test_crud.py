def test_post_request_should_return_201(api_request):
    endpoint = "/movies"
    body = {"title": "Inception", "year": 2010}
    response = api_request("post", endpoint, body=body)
    assert response.status_code == 201
    assert response.request.body == b'{"title": "Inception", "year": 2010}'
    print(response.request.body)

def test_get_movies_should_return_200(sget):
    # GET all movies
    response = sget("/movies")
    assert response.status_code == 200
    assert '[{"year": {"N": ' in response.text
    print(response.request.body)

def test_get_movie_by_id_should_return_200(sget, first_movie_id):
    response = sget(f"/movies/{first_movie_id}")
    assert response.status_code == 200
    assert '{"year": ' in response.text
    print(response.request.body)

def test_get_movie_by_wrong_id_should_return_404(sget):
    response = sget("/movies/erroneous-id")
    assert response.status_code == 404
    print(response.request.body)

def test_patch_request(api_request, first_movie_id):
    endpoint = "/movies"
    body = {"title": "Inception Updated"}
    response = api_request("patch", endpoint, movie_id=first_movie_id, body=body)
    assert response.status_code == 200
    print(response.request.body)

def test_put_request(api_request, first_movie_id):
    endpoint = "/movies"
    body = {"title": "Inception", "year": 2010}
    response = api_request("put", endpoint, movie_id=first_movie_id, body=body)
    assert response.status_code == 200
    print(response.request.body)

def test_put_request_approving_movie(api_request, first_movie_id):
    endpoint = "/movies"
    body = {"title": "Inception", "year": 2010, "approval_status": "approved"}
    response = api_request("put", endpoint, movie_id=first_movie_id, body=body)
    assert response.status_code == 200
    print(response.request.body)

    


def test_delete_request(api_request, first_movie_id):
    endpoint = "/movies"
    body = {"title": "Inception", "year": 2010}
    response = api_request("post", endpoint, body=body)
    print(response.request.body)

    response = api_request("delete", endpoint, movie_id=first_movie_id)
    assert response.status_code == 204
    print(response.request.body)

def test_head_request_correct_movie_should_return_200(api_request, first_movie_id):
    endpoint = "/movies"
    response = api_request("head", endpoint, movie_id=first_movie_id)
    assert response.status_code == 200
    print(response.request.body)


def test_head_request_incorrect_movie_should_return_404(api_request):
    endpoint = "/movies"
    first_movie_id = "non-existent-id"
    response = api_request("head", endpoint, movie_id=first_movie_id)
    assert response.status_code == 404
    assert response.request.body is None
    print(response.request.body)
