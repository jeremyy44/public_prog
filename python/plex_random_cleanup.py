#!/usr/bin/env python3

import os
import random
import argparse
import shutil

def truncate_middle(text, width):
    if len(text) <= width:
        return text
    half = (width - 3) // 2
    return text[:half] + "..." + text[-half:]

def get_dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

def bytes_to_gb(b):
    return b / (1024 ** 3)

def main():
    parser = argparse.ArgumentParser(
        description="Random Plex media cleanup tool"
    )
    parser.add_argument("library", help="Path to Plex media library")
    parser.add_argument("--size", type=float, required=True, help="Target size in GB")
    parser.add_argument("--delete", action="store_true", help="Actually delete files")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    medias = [
        os.path.join(args.library, d)
        for d in os.listdir(args.library)
        if os.path.isdir(os.path.join(args.library, d))
    ]

    random.shuffle(medias)

    selected = []
    total_size = 0
    target_bytes = args.size * (1024 ** 3)

    for media in medias:
        size = get_dir_size(media)
        if total_size + size > target_bytes:
            continue
        selected.append((media, size))
        total_size += size
        if total_size >= target_bytes:
            break

    print("\nSelected medias")
    print("=" * 72)
    print(f"{'#':<4} {'Media':<50} {'Size (GB)':>10}")
    print("-" * 72)

    for i, (media, size) in enumerate(selected, 1):
        name = truncate_middle(os.path.basename(media), 50)
        print(f"{i:<4} {name:<50} {bytes_to_gb(size):>10.2f}")

    print("-" * 72)
    print(f"{'TOTAL':<54} {bytes_to_gb(total_size):>10.2f}")
    print("=" * 72)

    if not args.delete:
        print("\nMode: DRY RUN")
        print("Nothing was deleted.")
        print("Use --delete to perform the actual removal.")
        return

    confirm = input("\nType DELETE to confirm deletion: ")
    if confirm != "DELETE":
        print("Aborted. No files were deleted.")
        return

    for media, _ in selected:
        print(f"Deleting: {media}")
        shutil.rmtree(media)

    print("\nDeletion complete.")

if __name__ == "__main__":
    main()
