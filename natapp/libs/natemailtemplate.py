class EmailTemplate:

    EMAIL_TEMPLATES = {
        'verify_email': {
            'en': {
                'subject': 'E-Diploma account verification',
                'file_name': 'USERS_Registration_complete_en.html'
            },
            'hu': {
                'subject': 'E-Diploma regisztáció megerősítés',
                'file_name': 'USERS_Registration_complete_hu.html'
            },
            'parameters': ['recipient', 'customer_id', 'verifyaccount_url', 'token']
        },
        'verify_email_with_password': {
            'en': {
                'subject': 'E-Diploma account created - email verification',
                'file_name': 'USERS_Registration_complete_with_password_en.html'
            },
            'hu': {
                'subject': 'E-Diploma felhasználó létrehozva - email cím megerősítés',
                'file_name': 'USERS_Registration_complete_with_password_hu.html'
            },
            'parameters': ['recipient', 'customer_id', 'verifyaccount_url', 'token', 'password']
        },
        'pwdreset_email': {
            'en': {
                'subject': 'E-Diploma Password Reset Request',
                'file_name': 'USERS_Password_reset_en.html'
            },
            'hu': {
                'subject': 'E-Diploma Jelszó változtatás',
                'file_name': 'USERS_Password_reset_hu.html'
            },
            'parameters': ['recipient', 'customer_id', 'pwreset_url_base', 'token']
        },
    }
