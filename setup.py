from distutils.core import setup
 
setup(
    name = "sorl-thumbnail",
    version = "3.2",
    packages = [
        "sorl",
        "sorl.thumbnail",
        "sorl.thumbnail.templatetags",
        "sorl.thumbnail.tests",
        "sorl.thumbnail.management",
        "sorl.thumbnail.management.commands",
    ],
)
