# Markdown to Imgur Upload

This Python script uploades local images to Imgur and replaces their path with the remote URL in the Markdown.

## Usage

1. Clone the repository.
2. Run `pip install -r requirements-dev.txt`.
3. Copy `.env.example` to `.env` and add your `CLIENT_ID` from the Imgur API.
4. Create an `original.md` file and add your markdown to it.
5. Add your local images to `screenshots` directory and also update the path of your local images in `original.md` file so that the Python script can find them in the `screenshots` directory.
6. Run `python src/main.py` and a new `updated.md` will be created for you.
