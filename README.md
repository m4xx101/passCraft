# passCraft

passCraft is a powerful and efficient password generation tool that creates strong, diverse passwords based on user inputs. The tool combines various password patterns, leet transformations, special characters, and leaked password files to generate secure passwords.

## Features

- **Words:** Accepts multiple words as input.
- **Birthdate:** Incorporates birthdate into password patterns.
- **Contact Numbers:** Uses contact numbers to generate combinations.
- **Leet Transformations:** Applies common leet transformations.
- **Common Passwords:** Includes a list of common passwords.
- **Special Characters:** Appends special characters to passwords.
- **Interactive Mode:** Runs in interactive mode if no arguments are provided.
- **Output File:** Saves generated passwords to a specified file.
- **Password Count:** Generates a specified number of passwords.
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/m4xx101/passCraft.git
    cd passCraft
    ```

2. (Optional) Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Commandline arguments:

    ```bash
    python3 passCraft.py -w Jhon,Doe,Naruto,Anime -b 01011990 -c 1234567890 0987654321 -l -o test.pass 

    -w, --words: Input words (space-separated or comma-separated).
    -b, --birthdate: Birthdate in DDMMYYYY format.
    -c, --contact_numbers: Contact numbers (space-separated or comma-separated).
    -l, --leet: Enable leet transformations.
    -o, --output: Output file to save generated passwords.
    ```

2. Interactive mode

    ```bash
    python3 passCraft.py

    The script will prompt for the necessary inputs and generate passwords accordingly.
    ```
## License

This project is licensed under the MIT License - see the LICENSE file for details.


