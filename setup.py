from distutils.core import setup
 
setup(
    name = "sorl",
    version = "3.1",
    packages = [
        "sorl",
        "sorl.thumbnail",
        "sorl.thumbnail.templatetags",
        "sorl.thumbnail.tests",
    ],
)
