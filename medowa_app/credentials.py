ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@corestore.local'
ADMIN_PASSWORD = 'Admin@12345'

TEST_USERNAME = 'testuser'
TEST_EMAIL = 'testuser@corestore.local'
TEST_PASSWORD = 'TestPass123!'


def ensure_accounts():
    from django.contrib.auth import get_user_model

    user_model = get_user_model()

    admin_user, _ = user_model.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={'email': ADMIN_EMAIL},
    )
    admin_user.email = ADMIN_EMAIL
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.set_password(ADMIN_PASSWORD)
    admin_user.save()

    test_user, _ = user_model.objects.get_or_create(
        username=TEST_USERNAME,
        defaults={'email': TEST_EMAIL},
    )
    test_user.email = TEST_EMAIL
    test_user.is_active = True
    test_user.is_staff = False
    test_user.is_superuser = False
    test_user.set_password(TEST_PASSWORD)
    test_user.save()

    return admin_user, test_user
