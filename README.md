# Trim2Circle

Trim2Circle is a web application that allows users to upload images, resize and crop them to a circle, and generate a PDF or ZIP file with the processed images.

## New in this fork: Option to add a black border for cutting guidance

## New in this fork: Ability to specify the border width


## Usecase

Custome figurines and tags for Teddy Cloud

https://github.com/toniebox-reverse-engineering/teddycloud

https://gt-blog.de/toniebox-hacking-how-to-get-started/

https://forum.revvox.de/t/teddycloud-esp32-newbie-documentation-deprecated/112

https://www.youtube.com/watch?v=JpMRyshgy9o

## Features

- Upload multiple images (PNG, JPG, JPEG)
- Resize images to a specified diameter
- Crop images to a circle
- Generate a PDF with the processed images
- Generate a ZIP file with the processed images

## Installation

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/jdp-code/Trim2Circle.git
    cd Trim2Circle
    ```

2. Build and run the application using Docker Compose:

    ```sh
    docker compose up -d
    ```

3. Open your web browser and go to `http://localhost:5000`.

## Usage

1. Select the output format (PDF or ZIP).
2. If PDF is selected, specify the diameter (in mm) and the paper size.
3. Upload the images you want to process.
4. Click the "Process" button to generate the output file.

## Example Output PDF
![Screenshot 2025-02-08 191108](https://github.com/user-attachments/assets/4e18e048-2bac-4e49-a0d6-5cf4a058efb0)
![image](https://github.com/user-attachments/assets/2f7c7840-0b33-4b70-bdcd-8fbce054c381)
![Screenshot 2025-02-08 191141](https://github.com/user-attachments/assets/0bfa68f2-2ab1-438e-af13-399ecb74d7de)



## Dependencies

- Flask
- Pillow
- reportlab

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
