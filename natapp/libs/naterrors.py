class Errors:
    EGEN_internal_E001, EGEN_http_E001, EGEN_400_E001, EGEN_404_E001, \
    EGEN_badreq_E001, EGEN_badreq_E002, EGEN_transact_E001, EGEN_lockedout_E001, \
    EGEN_unauth_E001, EGEN_unauth_E002, EGEN_invchars_E001, EGEN_invtype_E001, EGEN_tokenref_E001, EGEN_tokenref_E002, \
    EGEN_dbresp_E001, EGEN_dummy_E001, EGEN_dbresp_E001, EGEN_dbresult_E001, EVRF_missing_E001, \
    EVRF_missing_E002, EGEN_unauth_E001, SENDMAIL_missing_001, SENDMAIL_missing_002, SENDMAIL_missing_003, SENDMAIL_missing_004, SENDMAIL_missing_005, SENDMAIL_invalid_001,  SENDMAIL_invalid_002, SENDMAIL_invalid_003, SENDMAIL_error_001, SENDMAIL_error_002, ERSTPWD_missing_E001, ERSTPWD_invalid_E002, ERSTPWD_old_token_E003, EREG_badpwd_E001, EREG_badusr_E001, EREG_badusr_E002, EREG_badusr_E003, EREG_badusr_E004, EREG_badusr_E005, EREG_badusr_E006, EREG_invemail_E001, SETLANG_missing_001, SETLANG_error_001, ERFS_old_token_E001, ENAT_invstate_E001, ENAT_notactivated_E001, ENAT_selfremove_E001, ENAT_badnonce_E001, ENAT_badnonce_E002, EREG_badphone_E001, ENAT_noprice_E001, EGEN_invref_E001, EGEN_invref_E002, ENAT_badaddr_E001, ETSK_assigned_E001, ENAT_badtxid_E001, ENAT_badtxid_E002, EDOC_invalias_E001, ENAT_pldeleted_E001, ENAT_plnotdeleted_E001 = range(61)

    ERR_TEXT = {
        EGEN_400_E001: ('EGEN_400_E001', "HTTP 400 error, Bad Request", 400),
        EGEN_404_E001: ('EGEN_404_E001', "HTTP 404 error, Not Found", 404),
        EGEN_internal_E001: ('EGEN_internal_E001', "Internal Server Error", 500),
        EGEN_http_E001: ('EGEN_http_E001', "HTTP error"),
        EGEN_badreq_E001: ('EGEN_badreq_E001', "Missing field, please check the API documentation"),
        EGEN_badreq_E002:
        ('EGEN_badreq_E002', "Bad request, one or more field length is shorter or larger than expected"),
        EGEN_invref_E001: ('EGEN_invref_E001', 'Invalid DB reference'),
        EGEN_invref_E002: ('EGEN_invref_E002', 'Expired/deleted or missing reference'),
        EDOC_invalias_E001: ('EDOC_invalias_E001', 'Organization alias invalid for given date'),
        EGEN_transact_E001: ('EGEN_transact_E001', "Failed to complete transaction. Processed changes is rollbacked"),
        EGEN_lockedout_E001: ('EGEN_lockedout_E001', "Account suspended or permanently locked out"),
        EVRF_missing_E001: ('EVRF_missing_E001', "Missing token reference"),
        EVRF_missing_E002: ('EVRF_missing_E002', "Invalid token reference"),
        EGEN_unauth_E001: ('EGEN_unauth_E001', "Unauthorized access", 401),
        EGEN_unauth_E002: ('EGEN_unauth_E002', "Unauthorized access to resource", 401),
        EGEN_invchars_E001: ('EGEN_invchars_E001', "Invalid format or prohibited characters in request fields"),
        EGEN_invtype_E001: ('EGEN_invtype_E001', "Invalid type/cast for request fields"),
        EGEN_tokenref_E001: ('EGEN_tokenref_E001', "Missing token reference"),
        EGEN_tokenref_E002: ('EGEN_tokenref_E002', "Invalid token reference"),
        EGEN_dbresp_E001: ('EGEN_dbresp_E001', "Backend's response is invalid, please contact support"),
        EGEN_dummy_E001: ('EGEN_dummy_E001', "Dummy for dummies"),
        EGEN_dbresult_E001: ('EGEN_dbresult_E001', 'General background database error. unexpected result'),
        SENDMAIL_missing_001: ('SENDMAIL_missing_001', 'Missing template id.'),
        SENDMAIL_missing_002: ('SENDMAIL_missing_002', 'Missing instance.'),
        SENDMAIL_missing_003: ('SENDMAIL_missing_003', 'Missing parameters for template.'),
        SENDMAIL_missing_004: ('SENDMAIL_missing_004', 'Missing recipient address.'),
        SENDMAIL_missing_005: ('SENDMAIL_missing_005', 'Missing parameter.'),
        SENDMAIL_invalid_001: ('SENDMAIL_invalid_001', 'Invalid template id.'),
        SENDMAIL_invalid_002: ('SENDMAIL_invalid_002', 'Invalid number of parameters.'),
        SENDMAIL_invalid_003: ('SENDMAIL_invalid_003', 'Invalid recipient address.'),
        SENDMAIL_error_001: ('SENDMAIL_error_001', 'Error in opening template file.'),
        SENDMAIL_error_002: ('SENDMAIL_error_002', 'Error in sending mail.'),
        ERSTPWD_missing_E001: ('ERSTPWD_missing_E001', 'Missing password reset token'),
        ERSTPWD_invalid_E002: ('ERSTPWD_invalid_E002', 'Invalid password reset token'),
        ERSTPWD_old_token_E003: ('ERSTPWD_old_token_E003', 'Password reset token already expired'),
        EREG_badpwd_E001: ('EREG_badpwd_E001',
                           "Password is not acceptable (min 8 chars, and required to contains digits and upper chars)"),
        EREG_badusr_E001: ('EREG_badusr_E001', "Username is too short, minimum username length should be 5 characters"),
        EREG_badusr_E002: ('EREG_badusr_E002',
                           "Username contains nonaccepted characters, only alphanumerical chars and !@#. are allowed"),
        EREG_badusr_E003: ('EREG_badusr_E003', "This email address is already associated to an existing user"),
        EREG_badusr_E004: ('EREG_badusr_E004', "This username already exists, please select an other"),
        EREG_badusr_E005:
        ('EREG_badusr_E005', "This email address is already associated to an existing user which is pending deletion"),
        EREG_badusr_E006:
        ('EREG_badusr_E006', "This user name is already associated to an existing account which is pending deletion"),
        EREG_invemail_E001: ('EREG_invemail_E001', "The specified email address is invalid"),
        EREG_badphone_E001: ('EREG_badphone_E001', "Bad phone number, must be like '+36361234567'"),
        SETLANG_missing_001: ("SETLANG_missing_001", "Missing parameter: language."),
        SETLANG_error_001: ("SETLANG_error_001", "The language is not in predefined languages."),
        ERFS_old_token_E001: ('ERFS_old_token_E001', 'Invalidate refresh token after one week of inactivity'),
        ENAT_invstate_E001: ('ENAT_invstate_E001', "Instance status does not permit this operation"),
        ENAT_notactivated_E001: ('ENAT_notactivate_E001', "Player not activated yet..."),
        ENAT_selfremove_E001: ('ENAT_selfremove_E001', "Can't remove your own admin role"),
        ENAT_badnonce_E001: ('ENAT_badnonce_E001', "Bad nonce format"),
        ENAT_badnonce_E002: ('ENAT_badnonce_E002', "Invalid/expired nonce"),
        ENAT_badaddr_E001: ('ENAT_badaddr_E001', "Invalid address"),
        ENAT_badtxid_E001: ('ENAT_badtxid_E001', "Invalid transaction id - wrong length"),
        ENAT_badtxid_E002: ('ENAT_badtxid_E002', "Invalid transaction id - contains invalid characters"),
        ENAT_noprice_E001: ('ENAT_noprice_E001', "No NatCoin price found for given date"),
        ETSK_assigned_E001: ('ETSK_assigned_E001', 'Task already assigned to different admin user'),
        ENAT_plnotdeleted_E001: ('ENAT_plnotdeleted_E001', "playlist is not in deleted state, can't restore"),
        ENAT_pldeleted_E001: ('ENAT_pldeleted_E001', "playlist is already deleted, can't remove")
    }

    @classmethod
    def get_text(cls, err_code):
        error = Errors.ERR_TEXT.get(err_code)
        if error is None:
            raise Exception(f'Unknown error code: {err_code}')
        else:
            return error
