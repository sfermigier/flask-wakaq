from flask import Flask

from app.flask.extensions import wakaq


@wakaq.task
def lazy1():
    print("hello world")


@wakaq.task()
def lazy2():
    print("hello world")


def test_wakaq_eager(app: Flask):
    @wakaq.task
    def mytask1():
        print("hello world")

    mytask1.delay()


def test_wakaq_eager_call(app: Flask):
    @wakaq.task()
    def mytask2():
        print("hello world")

    mytask2.delay()


def test_wakaq_lazy(app: Flask):
    lazy1.delay()


def test_wakaq_lazy_call(app: Flask):
    lazy2.delay()
