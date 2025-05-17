# Facebook Post Number Scraper

A web application that extracts numeric post IDs from Facebook post URLs.

## Features

- Extracts post numbers from Facebook URLs
- Simple web interface
- Deployable on Render.com

## Deployment

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com/)
3. Connect your GitHub account and select this repository
4. Render will automatically detect the `render.yaml` file
5. Deploy!

## Environment Variables

The following environment variables are required:

- `GOOGLE_CHROME_BIN`: Path to Chrome binary
- `CHROMEDRIVER_PATH`: Path to ChromeDriver

These are automatically set in the `render.yaml` file.

## Limitations

- May not work with private posts
- Facebook may block frequent requests
- Requires Chrome and ChromeDriver to be installed
