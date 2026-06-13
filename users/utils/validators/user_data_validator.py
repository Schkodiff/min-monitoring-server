class UserDataValidator:
    @classmethod
    def __validate_email(cls, email):
        pass

    @classmethod
    def validate_email_on_create(cls, email):
        if email is None or email == "":
            raise ValueError('Электронная почта не может быть пустой!')
        cls.__validate_email(email)

    @classmethod
    def validate_email_on_update(cls, email):
        if email is None or email == "":
            return
        cls.__validate_email(email)

    @classmethod
    def validate_email_exists(cls, email):
        # if email :
        #     return
        # cls.__validate_email(email)
        pass

    @classmethod
    def __validate_phone(cls, phone):
        pass

    @classmethod
    def validate_phone_on_create(cls, phone):
        if phone is None or phone == "":
            raise ValueError('Номер телефона не может быть пустым!')
        cls.__validate_phone(phone)

    @classmethod
    def validate_phone_on_update(cls, phone):
        if phone is None or phone == "":
            return
        cls.__validate_phone(phone)

    @classmethod
    def validate_phone_exists(cls, phone):
        pass