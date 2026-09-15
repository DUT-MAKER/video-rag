"""Auth domain specific exceptions."""

from core.exceptions import ConflictException, NotFoundException, UnauthorizedException


class UserNotFoundException(NotFoundException):
    def __init__(self, message: str = "Không tìm thấy thông tin người dùng"):
        super().__init__(message)


class EmailAlreadyExistsException(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"Email {email} đã được đăng ký sử dụng")


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self, message: str = "Email hoặc mật khẩu không chính xác"):
        super().__init__(message)
