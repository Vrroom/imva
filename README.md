# imva 

imva serves images from a specified directory, displaying them in a table format on a web page. I use it to inspect training logs (which I prefer in HTML).

## Installation

You can install `imva` directly from GitHub using `pip`. Run the following command:

```bash
pip install git+https://github.com/vrroom/imva.git
```

## Usage

After installation, run `imva` using the following command with the required arguments:

```bash
imva --image_directory PATH_TO_IMAGE_DIRECTORY --image_path_patterns IMAGE_PATH_PATTERNS --sort_key SORT_KEY
```

### Arguments

- `--image_directory`: Path to the directory containing the images. This argument is required.
- `--image_path_patterns`: Patterns for identifying images to show. Accepts multiple patterns.
- `--sort_key`: Key used to sort the images. If not specified, no specific sorting is applied.
- `--port`: Port number to run the app on. Defaults to 5000.
- `--host`: Host to run the app on. Defaults to 'localhost'.

### Example

To launch the server with a specified directory and patterns:

```bash
python3 -m imva --image_directory ./image_log_dir \
                --image_path_patterns samples_gs-{global_step}_e-{epoch}_b-{batch}.png \
                                      reconstruction_gs-{global_step}_e-{epoch}_b-{batch}.png \
                --sort_key global_step
```

In the above example, `image_log_dir` has a bunch of images which follow the template in `image_path_patterns`. These are sorted by the `global_step` key in decreasing order and visualized in an HTML table.

## License

MIT License
