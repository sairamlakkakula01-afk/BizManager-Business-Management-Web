from app.models.user import User, Role


def test_login_success(client, admin_user):
    res = client.post('/login', data={
        'username': 'admin',
        'password': 'AdminSecure123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome back, Admin User' in res.data


def test_login_invalid_password(client, admin_user):
    res = client.post('/login', data={
        'username': 'admin',
        'password': 'WrongPassword123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Invalid username or password' in res.data


def test_login_deactivated_account(client, db_session):
    inactive = User(
        username='inactive_user',
        email='inactive@bizmanager.test',
        full_name='Inactive User',
        role=Role.STAFF,
        is_active=False
    )
    inactive.set_password('SomePassword123!')
    db_session.add(inactive)
    db_session.commit()

    res = client.post('/login', data={
        'username': 'inactive_user',
        'password': 'SomePassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'deactivated' in res.data.lower()


def test_logout(client, admin_user):
    client.post('/login', data={'username': 'admin', 'password': 'AdminSecure123!'}, follow_redirects=True)
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b'logged out safely' in res.data.lower()


def test_role_permissions_admin_vs_staff(client, staff_user):
    # Staff logs in
    client.post('/login', data={'username': 'staff', 'password': 'StaffSecure123!'}, follow_redirects=True)

    # Staff attempts to access admin-only /users
    res_users = client.get('/users')
    assert res_users.status_code == 403

    # Staff attempts to access admin-only /settings
    res_settings = client.get('/settings/')
    assert res_settings.status_code == 403

    # Staff can access products list
    res_products = client.get('/products/')
    assert res_products.status_code == 200


def test_unauthenticated_redirect(client):
    res = client.get('/', follow_redirects=False)
    assert res.status_code == 302
    assert '/login' in res.headers['Location']
