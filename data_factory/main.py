import factory

from src.core.db import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User


class ShiftFactory(factory.Factory):
    class Meta:
        model = models.Shift


class PhotoFactory(factory.Factory):
    class Meta:
        model = models.Photo


class TaskFactory(factory.Factory):
    class Meta:
        model = models.Task


class RequestFactory(factory.Factory):
    class Meta:
        model = models.Request


class UserTaskFactory(factory.Factory):
    class Meta:
        model = models.UserTask
