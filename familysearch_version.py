#!/usr/bin/env python3

VERSION = "v0.1"

import os
import shutil
import sys
import time
import random
from datetime import datetime

# === Setup: version backup ===
def copy_self_if_missing():
    target_dir = os.path.expanduser("~/neuralnexus")
    target_path = os.path.join(target_dir, "familysearch_version.py")
    current_path = os.path.abspath(sys.argv[0])

    os.makedirs(target_dir, exist_ok=True)
    if not os.path.exists(target_path):
        shutil.copy(current_path, target_path)
        print(f"📁 Backed up version {VERSION} to {target_path}")

# === One-time seed from Seed_scri.txt ===
def seed_family_tree_structure():
    seed_path = os.path.expanduser("~/Seed_scri.txt")
    if not os.path.exists(seed_path):
        print("⚠️ Seed script not found, skipping seeding step.")
        return

    with open(seed_path, "r") as f:
        for line in f:
            if line.startswith("mkdir"):
                path = line.split("mkdir", 1)[1].strip()
                normalized_path = os.path.expanduser(path).lower()
                try:
                    os.makedirs(normalized_path, exist_ok=True)
                    print(f"📁 Created: {normalized_path}")
                except Exception as e:
                    print(f"❌ Error creating {normalized_path}: {e}")

# === Globals ===
START_TIME = time.time()
RESEARCH_LOG = os.path.expanduser("~/FamilyTree/research.txt")

# === Utility functions ===
def strip_to_alpha(text):
    return ''.join(c for c in text if c.isalpha())

def normalize_name(name):
    return name.lower().replace(" ", "_").replace("'", "")

def delay_and_check_time():
    global START_TIME
    if time.time() - START_TIME > 2 * 3600:
        print("🕒 I am done researching my tree. Time limit reached.")
        exit(0)
    time.sleep(random.randint(3, 14))

def is_valid_name(name):
    return len(name.split()) == 2

def get_quendor_response(prompt):
    print(f"🤖 Quendor: {prompt}")
    return input("Your input: ").strip()

def say_to_quendor(message):
    print(f"🧙 Quendor, say: {message}")

def write_info_and_log(info_path, name, content):
    os.makedirs(os.path.dirname(info_path), exist_ok=True)
    with open(info_path, "w") as f:
        f.write(content)
    with open(RESEARCH_LOG, "a") as log:
        log.write(f"\n{name}:\n{content}\n")

def extract_name_from_path(path):
    name = os.path.basename(path)
    return name.replace("_male", "").replace("_female", "").replace("_", " ")

def ensure_family_folder(parent, name, gender):
    norm = normalize_name(name)
    subfolder = os.path.join(parent, f"{norm}_{gender}")
    os.makedirs(subfolder, exist_ok=True)
    return subfolder

def explore_person(person_path):
    # Random chance to return to root
    if random.randint(1, 4) == 1:
        root = os.path.expanduser("~/FamilyTree")
        subdirs = [d for d in os.listdir(root) if d.endswith(("_male", "_female"))]
        if subdirs:
            explore_person(os.path.join(root, random.choice(subdirs)))
            return

    delay_and_check_time()
    person_name = extract_name_from_path(person_path)
    say_to_quendor(f"learn_about {person_name}")
    delay_and_check_time()

    info_path = os.path.join(person_path, "info.txt")
    if not os.path.exists(info_path):
        response = get_quendor_response(f"What do you know about {person_name}?")
        write_info_and_log(info_path, person_name, response)
        delay_and_check_time()

    # Ask for father
    father = ""
    while not is_valid_name(father):
        father = get_quendor_response("Quendor, please give me the exact name of the father")
        if not is_valid_name(father):
            print("Quendor, I only need a first and last name.")
    father_path = ensure_family_folder(person_path, father, "male")

    # Ask for mother
    mother = ""
    while not is_valid_name(mother):
        mother = get_quendor_response("Quendor, please give me the exact name of the mother")
        if not is_valid_name(mother):
            print("Quendor, I only need a first and last name.")
    mother_path = ensure_family_folder(person_path, mother, "female")

    delay_and_check_time()
    next_dir = random.choice([father_path, mother_path])
    explore_person(next_dir)

# === Main Entry ===
def main():
    os.makedirs(os.path.expanduser("~/FamilyTree"), exist_ok=True)
    if not os.path.exists(RESEARCH_LOG):
        open(RESEARCH_LOG, "w").close()
    explore_person(os.path.expanduser("~/FamilyTree/jeremiah_oneal_male"))

if __name__ == "__main__":
    copy_self_if_missing()
    seed_family_tree_structure()
    main()
