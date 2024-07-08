import argparse
import random
import re
import itertools
import sys
import time
import threading
from password_strength import PasswordPolicy

# Define common leet replacements
leet_dict = {
    'a': ['4', '@'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['5', '$'],
    't': ['7'],
    'b': ['8']
}

# Special characters and digits
special_characters = list('!@#$%^&*()_+-=[]{}|;:,.<>?/')
digits = list('0123456789')

# Common passwords and patterns
common_passwords = [
    "123456", "password", "123456789", "12345678", "12345", "1234567", "qwerty",
    "111111", "123123", "abc123", "password1", "letmein", "welcome", "monkey",
    "654321", "superman", "1qaz2wsx", "qazwsx", "qwe123", "football", "dragon"
]

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
    nonletters=1  # need min. 1 non-letter characters (digits, specials, anything)
)

def leet_transform(word):
    leet_words = {word}
    for char in word:
        if char in leet_dict:
            leet_words.update(
                {w[:i] + leet_char + w[i + 1:] for w in leet_words for i, leet_char in enumerate(leet_dict[char]) if w[i] == char}
            )
    return list(leet_words)

def apply_patterns(words, birthdate, contact_numbers, leet):
    combinations = set()
    if birthdate:
        dd = birthdate[:2]
        mm = birthdate[2:4]
        yy = birthdate[4:8]

    if leet:
        leet_words = set()
        for word in words:
            leet_words.update(leet_transform(word))
        words = list(leet_words)
    
    if contact_numbers:
        contact_combinations = [num[:4] + num[-4:] for num in contact_numbers]

    for word in words:
        for sc in special_characters:
            combinations.add(f"{word}{sc}")
            combinations.add(f"{sc}{word}")
        if birthdate:
            combinations.add(f"{word}{dd}{mm}{yy}")
            combinations.add(f"{word}{yy}{mm}{dd}")
            combinations.add(f"{dd}{mm}{yy}{word}")
            combinations.add(f"{yy}{mm}{dd}{word}")
        if contact_numbers:
            for num in contact_numbers:
                combinations.add(f"{word}{num[:4]}")
                combinations.add(f"{word}{num[-4:]}")
                combinations.add(f"{word}{num}")
                combinations.add(f"{num[:4]}{word}")
                combinations.add(f"{num[-4:]}{word}")
                combinations.add(f"{num}{word}")
                for sc in special_characters:
                    combinations.add(f"{word}{sc}{num[:4]}")
                    combinations.add(f"{word}{sc}{num[-4:]}")
                    combinations.add(f"{word}{sc}{num}")
                    combinations.add(f"{num[:4]}{sc}{word}")
                    combinations.add(f"{num[-4:]}{sc}{word}")
                    combinations.add(f"{num}{sc}{word}")
        for word2 in words:
            if word != word2:
                combinations.add(f"{word}{word2}")
                combinations.add(f"{word}{random.choice(special_characters)}{word2}")
                combinations.add(f"{word2}{random.choice(special_characters)}{word}")

    return combinations

def generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords, fullname):
    combinations = set()

    combinations.update(common_passwords)
    combinations.update(leaked_passwords)

    if fullname:
        first_name, last_name = fullname
        words.append(first_name)
        words.append(last_name)

    word_combinations = apply_patterns(words, birthdate, contact_numbers, leet)
    
    combinations.update(word_combinations)

    valid_passwords = set()
    for pwd in combinations:
        if len(valid_passwords) >= num_passwords:
            break
        if policy.test(pwd):
            continue
        valid_passwords.add(pwd)

    return list(valid_passwords)[:num_passwords]

def print_banner():
    banner = """
░█▀▀█ █▀▀█ █▀▀ █▀▀ ░█▀▀█ █▀▀█ █▀▀█ █▀▀ ▀▀█▀▀ 
░█▄▄█ █▄▄█ ▀▀█ ▀▀█ ░█─── █▄▄▀ █▄▄█ █▀▀ ──█── 
░█─── ▀──▀ ▀▀▀ ▀▀▀ ░█▄▄█ ▀─▀▀ ▀──▀ ▀── ──▀──
    """
    print(banner)

def print_summary(password_count, time_taken, output_file):
    print("\nSummary:")
    print(f"Number of passwords generated: {password_count}")
    print(f"Time taken: {time_taken:.2f} seconds")
    if output_file:
        print(f"Passwords saved to: {output_file}")

def loading_animation(stop_event):
    text = "creating passwords...."
    while not stop_event.is_set():
        for i in range(len(text)):
            if stop_event.is_set():
                break
            sys.stdout.write(f"\033[1m\033[92m{text[:i+1]}\033[0m")
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\r')
            sys.stdout.flush()
        sys.stdout.write(' ' * len(text) + '\r')
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Generate strong passwords based on input words, birthdate, contact numbers, and leet transformations.")
    parser.add_argument('-w', '--words', nargs='+', required=True, help="Input words (space-separated or comma-separated).")
    parser.add_argument('-b', '--birthdate', type=str, help="Birthdate in DDMMYYYY format.")
    parser.add_argument('-c', '--contact_numbers', nargs='+', help="Contact numbers (space-separated or comma-separated).")
    parser.add_argument('-l', '--leet', action='store_true', help="Enable leet transformations.")
    parser.add_argument('-o', '--output', type=str, help="Output file to save generated passwords.")
    parser.add_argument('-f', '--file', type=str, help="File containing leaked passwords to enhance generation.")
    parser.add_argument('-n', '--number', type=int, default=1000, help="Number of passwords to generate.")
    parser.add_argument('--fullname', type=str, help="Full name: Firstname Lastname.")
    args = parser.parse_args()

    words = re.split(r'[ ,]+', ' '.join(args.words))
    birthdate = args.birthdate
    contact_numbers = args.contact_numbers if args.contact_numbers else []
    leet = args.leet
    output_file = args.output
    num_passwords = args.number
    leaked_passwords = set()
    fullname = tuple(args.fullname.split()) if args.fullname else None

    if args.file:
        try:
            with open(args.file, 'r') as f:
                leaked_passwords = {line.strip() for line in f}
        except FileNotFoundError:
            print(f"Leaked passwords file '{args.file}' not found.")
            sys.exit(1)

    stop_event = threading.Event()
    animation_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    animation_thread.start()

    start_time = time.time()
    passwords = generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords, fullname)
    end_time = time.time()
    time_taken = end_time - start_time

    stop_event.set()
    animation_thread.join()

    if output_file:
        with open(output_file, 'w') as f:
            for pwd in passwords:
                f.write(f"{pwd}\n")
        print(f"Passwords saved to {output_file}")
    else:
        for pwd in passwords:
            print(pwd)

    print_summary(len(passwords), time_taken, output_file)

if __name__ == "__main__":
    print_banner()
    if len(sys.argv) == 1:
        words = input("Enter Words separated by space or comma: ").split(',')
        birthdate = input("Enter Birth date (DDMMYYYY): ")
        contact_numbers = input("Enter Contact numbers separated by space or comma: ").split(',')
        leet = input("Enable leet transformations? (Y/N): ").lower() in ['y', 'yes']
        fullname = input("Enter Full name: Firstname Lastname: ").strip().split()
        leaked_passwords = set()
        leaked_file = input("Enter file path for leaked passwords (optional): ").strip()
        if leaked_file:
            try:
                with open(leaked_file, 'r') as f:
                    leaked_passwords = {line.strip() for line in f}
            except FileNotFoundError:
                print(f"Leaked passwords file '{leaked_file}' not found.")
                sys.exit(1)

        stop_event = threading.Event()
        animation_thread = threading.Thread(target=loading_animation, args=(stop_event,))
        animation_thread.start()

        start_time = time.time()
        passwords = generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords, tuple(fullname))
        end_time = time.time()
        time_taken = end_time - start_time

        stop_event.set()
        animation_thread.join()

        for pwd in passwords:
            print(pwd)

        print_summary(len(passwords), time_taken, None)
    else:
        main()
