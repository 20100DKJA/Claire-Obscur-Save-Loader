import sys

from clair_obscur_save_loader import controllers


def main() -> None:
    sys.exit(controllers.MainController().run())


if __name__ == '__main__':
    main()
