from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField('Электронная почта', max_length=254, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='follower', verbose_name='Пользователь'
    )
    subscription = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following', verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscription'],
                                    name='user_subscription'
                                    )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.subscription}'
