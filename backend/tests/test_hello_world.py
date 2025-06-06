def test_hello_world(client):
    """
        Test Hello World
    """
    response = client.get('/')
    assert response.status_code == 200
