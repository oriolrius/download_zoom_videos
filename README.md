# Dowload and Delete Zoom Meeting Recordings

## Description
This Python script interacts with the Zoom API to manage user recordings. It retrieves an access token, fetches the list of recordings, downloads MP4 recordings, and deletes them afterward.

## My use case

I use Zoom to record my meetings, and I want to keep the recordings for a few days in case I need to review them. After a few days, I don't need them anymore, so I want to delete them. I also want to keep a copy of the recordings on my computer, so I download them before deleting them from Zoom.

## Prerequisites

- Python 3.x
- and the content of the [requirements.txt](requirements.txt) file
- create a Server-to-Server OAuth2 app in Zoom Marketplace with the scope: `recording:read:admin` and `recording:write:admin`

## Installation

1. Clone the repository
    ```bash
    git clone https://github.com/oriolrius/download_zoom_videos.git
    ```

1. Navigate into the project directory
    ```bash
    cd download_zoom_videos
    ```

1. Create a venv for installing the application dependencies
    ```bash
    python -m venv venv
    ```

1. Activate the venv
    ```bash
    source venv/bin/activate
    ```

1. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```

1. Copy env.example to .env; and edit the .env file with your credentials. Credentials can be found in the Zoom Marketplace under the "Develop" section.

    ```dotenv
    LOG_LEVEL=DEBUG
    ACCOUNT_ID=<Your-Account-ID>
    CLIENT_ID=<Your-Client-ID>
    CLIENT_SECRET=<Your-Client-Secret>
    ```

5. Run the application
    ```bash
    python download_all_videos.py
    ```

## Script steps description

The script performs the following tasks automatically:

1. Retrieves an access token from Zoom API
2. Fetches the list of recordings
3. Downloads MP4 recordings
4. Deletes the recordings from Zoom

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request.

## Author

Oriol Rius <oriol@joor.net>

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
