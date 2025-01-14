import requests

def login_admin():
    url = 'http://localhost:8000/api/v1/admin/auth/login'
    data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f'Login failed: {response.text}')
            return None
    except Exception as e:
        print(f'Error during login: {str(e)}')
        return None

def test_countries_endpoint():
    url = 'http://localhost:8000/api/v1/code-analyzer/countries'
    try:
        response = requests.get(url)
        print(f'Countries Endpoint Status: {response.status_code}')
        print(f'Response: {response.text}\n')
    except Exception as e:
        print(f'Error testing countries endpoint: {str(e)}\n')

def test_marketplace_stats_endpoint(token):
    url = 'http://localhost:8000/api/v1/code-analyzer/marketplace/stats'
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    try:
        response = requests.get(url, headers=headers)
        print(f'Marketplace Stats Endpoint Status: {response.status_code}')
        print(f'Response: {response.text}\n')
    except Exception as e:
        print(f'Error testing marketplace stats endpoint: {str(e)}\n')

if __name__ == '__main__':
    print('Testing endpoints...\n')
    
    # Test countries endpoint (no auth required)
    test_countries_endpoint()
    
    # Login and test marketplace stats endpoint
    token = login_admin()
    if token:
        print('Admin login successful, testing marketplace stats...\n')
        test_marketplace_stats_endpoint(token)
    else:
        print('Admin login failed, skipping marketplace stats test\n') 