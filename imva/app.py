from flask import Flask, render_template, jsonify, send_from_directory, url_for, request
import time
from functools import partial
import os
import random
import argparse
import re
import threading

def extract_braced_parts(s):
    # Regular expression to find parts enclosed in braces
    pattern = r'\{(.*?)\}'
    return set(re.findall(pattern, s))

def assert_all_keys_identical (pattern_list) :
    sets = [extract_braced_parts(_) for _ in pattern_list]
    if len(sets) > 0 :
        assert all([sets[0] == s for s in sets[1:]]), f'Pattern List is inconsistent - {pattern_list}'

def prepare_images (args): 
    image_paths = os.listdir(args.image_directory) 
    col_headers = args.image_path_patterns
    row_groups = []
    for path_pattern in args.image_path_patterns : 
        path_params = []
        for path in image_paths :
            try :
                path_params.append((path, reverse_f_string(path, path_pattern, int)))
            except Exception as e: 
                pass
        if args.sort_key is not None :
            path_params = list(reversed(sorted(path_params, key=lambda x: x[1][args.sort_key])))
        row_groups.append(path_params)
    return [''] + col_headers, row_groups

def reverse_f_string(s, fstring_pattern, var_types, scope=None):
    """
    Extracts variables from a string based on an f-string-like pattern. Optionally updates a provided scope with these variables.

    Parameters
    ----------
    s : str
        The string to be processed, which is expected to match the format defined by `fstring_pattern`.

    fstring_pattern : str
        The f-string-like pattern used to parse `s`. Variables in the pattern should be enclosed in curly braces, e.g., '{variable}'.

    var_types : type or list of types
        The type or a list of types to which the extracted string values should be converted. If a list is provided, it should be in the
        same order as the variables in `fstring_pattern`.

    scope : dict, optional
        The scope in which extracted variables should be updated. If provided, this function will update the scope with the extracted variables.
        If None (default), no scope is updated, and a dictionary of extracted variables is returned.

    Returns
    -------
    dict
        A dictionary containing the extracted variables and their values, converted to the specified types.

    Raises
    ------
    ValueError
        If the string `s` does not match the `fstring_pattern`, if the number of types provided does not match the number of variables,
        or if a type conversion fails.

    Example
    -------
    >>> values = reverse_f_string('epoch=0_step=4.ckpt', 'epoch={epoch}_step={step}.ckpt', [int, int], locals())
    >>> epoch, step = values['epoch'], values['step']
    >>> print(epoch, step)

    Notes
    -----
    - The function assumes that `fstring_pattern` contains simple variable placeholders and does not support complex expressions or format specifications.
    - When `scope` is provided, it must be a mutable dictionary-like object (e.g., the result of calling `locals()` or `globals()` in the calling scope).
    - The `var_types` parameter should either be a single type (if there's only one variable) or a list of types corresponding to each variable in order.
    """
    # Extract variable names from f-string-like pattern
    var_names = re.findall(r'\{(.*?)\}', fstring_pattern)

    # Validate and construct the regex pattern
    regex_pattern = fstring_pattern
    for var in var_names:
        regex_pattern = regex_pattern.replace(f"{{{var}}}", r"(.+?)")

    # Match against the string
    match = re.match(regex_pattern, s)
    if not match:
        raise ValueError("No match found")

    # Ensure each variable name has exactly one match
    if len(match.groups()) != len(var_names):
        raise ValueError("Number of matches and variables do not correspond")

    # Convert parsed strings to specified types and return as a dict
    values = {}
    for i, var in enumerate(var_names):
        try:
            # Apply the type conversion
            var_type = var_types[i] if isinstance(var_types, list) else var_types
            value = var_type(match.group(i + 1))
            values[var] = value
        except ValueError as e:
            raise ValueError(f"Conversion error for variable '{var}': {e}")

    if scope is not None:
        scope.update(values)
    return values

app = Flask(__name__)

parser = argparse.ArgumentParser(description='Flask app serving images from a directory')
parser.add_argument('--image_directory', type=str, help='Path to the image directory', required=True)
parser.add_argument('--image_path_patterns', nargs='+', help='Patterns for identifying images to show', type=str)
parser.add_argument('--sort_key', default=None, help='How to sort images', type=str)
parser.add_argument('--port', default=5000, help='Port to run app on', type=int)
parser.add_argument('--host', default='localhost', help='Host to run app on', type=str)
args = parser.parse_args()

assert_all_keys_identical(args.image_path_patterns)
col_headers, row_groups = prepare_images(args)

image_data_lock = threading.Lock()

def update_image_data_every_n_min (n_min) : 
    global col_headers, row_groups, image_data_lock
    while True: 
        time.sleep(n_min * 60)
        with image_data_lock :
            print('checking to see new data ...')
            col_headers, row_groups = prepare_images(args)
            print('done checking ...')

update_thread = threading.Thread(target=partial(update_image_data_every_n_min, n_min=10))
update_thread.daemon = True
update_thread.start()

@app.route('/')
def index():
    return render_template('index.html', col_headers=col_headers)

@app.route('/load_more_images')
def load_more_images():
    with image_data_lock: 
        idx = request.args.get('row_id', type=int)
        try : 
            params = ['\n'.join(f'{k}:{v}' for k, v in row_groups[0][idx][1].items())]
            images = [group[idx][0] for group in row_groups]
            image_urls = [url_for('serve_image', filename=image) for image in images]
            return jsonify(params + image_urls)
        except IndexError :
            return jsonify([])

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(args.image_directory, filename)

def main() : 
    app.run(debug=True, port=args.port, host=host)

if __name__ == '__main__':
    main()

