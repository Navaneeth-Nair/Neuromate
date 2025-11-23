import sys


def main():
    # Check if text mode is requested
    if len(sys.argv) > 1 and sys.argv[1] in ['--text', '-t', 'text']:
        from backend.interfaces import text_input
        text_input.text_mode()
    else:
        # Default: voice mode
        from backend.interfaces import speechrecog as spr
        spr.main()


if __name__ == "__main__":
    main()
