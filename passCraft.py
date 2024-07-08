import argparse
import random
import re
import itertools
import sys
import time
import threading

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
    "654321", "superman", "1qaz2wsx", "qazwsx", "qwe123", "football", "dragon",
    "master", "hello", "whatever", "trustno1", "baseball", "sunshine", "starwars",
    "princess", "azerty", "555555", "michael", "jordan", "hunter", "qaz123",
    "zaq12wsx", "123qwe", "passw0rd", "batman", "thomas", "hockey", "121212",
    "charlie", "liverpool", "letmein123", "a1b2c3", "secret", "freedom", "mustang",
    "shadow", "whatever1", "monkey123", "987654", "password123", "zxcvbnm", "qazxsw",
    "123654", "jessica", "awesome", "7777777", "1q2w3e", "william", "123abc",
    "mickey", "pokemon", "charles", "michael1", "princess123", "987654321", "1111",
    "888888", "sunshine1", "ashley", "bailey", "654321987", "football1", "666666",
    "jennifer", "amanda", "james", "tigger", "happy", "iloveyou1", "michael123",
    "summer", "admin123", "1212", "george", "trustnoone", "superman123", "hello123",
    "qwerty123"
]

def leet_transform(word):
    leet_words = {word}
    for char in word:
        if char in leet_dict:
            leet_words.update(
                {w[:i] + leet_char + w[i + 1:] for w in leet_words for i, leet_char in enumerate(leet_dict[char]) if w[i] == char}
            )
    return list(leet_words)

def generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords):
    combinations = set()
    
    combinations.update(common_passwords)
    combinations.update(leaked_passwords)
    
    if birthdate:
        dd = birthdate[:2]
        mm = birthdate[2:4]
        yy = birthdate[4:8]

    if contact_numbers:
        contact_combinations = [num[:4] + num[-4:] for num in contact_numbers]

    for word in words:
        if leet:
            leet_words = leet_transform(word)
        else:
            leet_words = [word]
        
        for lw in leet_words:
            combinations.update([lw + sc for sc in special_characters])
            if birthdate:
                combinations.update([lw + dd, lw + mm, lw + yy, lw + dd + mm + yy, lw + yy + mm + dd])
            if contact_numbers:
                combinations.update([lw + cc for cc in contact_combinations])
            combinations.update([lw, lw + yy, lw + mm, lw + dd, lw + dd + yy, lw + dd + mm + yy, lw + yy + mm + dd])
            for sc in special_characters:
                combinations.update([lw + sc, lw + sc + dd, lw + sc + mm, lw + sc + yy, lw + dd + sc, lw + mm + sc, lw + yy + sc])
            for cc in contact_combinations:
                combinations.update([lw + cc, cc + lw])
            combinations.update([lw + sc + yy + mm + dd for sc in special_characters])
            combinations.update([lw + yy + mm + dd + sc for sc in special_characters])

    for i in range(2, len(words) + 1):
        for perm in itertools.permutations(words, i):
            perm_str = ''.join(perm)
            combinations.add(perm_str)
            combinations.update([perm_str + sc for sc in special_characters])
            if birthdate:
                combinations.update([perm_str + dd, perm_str + mm, perm_str + yy, perm_str + dd + mm + yy, perm_str + yy + mm + dd])
            if contact_numbers:
                combinations.update([perm_str + cc for cc in contact_combinations])

    return list(combinations)[:num_passwords]

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
    parser.add_argument('-n', '--number', type=int, help="Number of passwords to generate.")
    
    args = parser.parse_args()

    words = re.split(r'[ ,]+', ' '.join(args.words))
    birthdate = args.birthdate
    contact_numbers = args.contact_numbers if args.contact_numbers else []
    leet = args.leet
    output_file = args.output
    num_passwords = args.number
    leaked_passwords = set()

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
    passwords = generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords)
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
        passwords = generate_combinations(words, birthdate, contact_numbers, leet, leaked_passwords, num_passwords)
        end_time = time.time()
        time_taken = end_time - start_time

        stop_event.set()
        animation_thread.join()

        for pwd in passwords:
            print(pwd)

        print_summary(len(passwords), time_taken, None)
    else:
        main()
