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
            try:
                total += os.path.getsize(fp)
            except (OSError, FileNotFoundError):
                continue  # File deleted or inaccessible
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
        if os.path.isdir(os.path.join(args.library, d)) and not d.startswith('.')
    ]

    random.shuffle(medias)

    # Calculate sizes for all media directories
    media_with_sizes = []
    for media in medias:
        size = get_dir_size(media)
        media_with_sizes.append((media, size))

    # Better bin-packing: keep trying to add items that fit
    selected = []
    total_size = 0
    target_bytes = args.size * (1024 ** 3)
    used_indices = set()

    for i, (media, size) in enumerate(media_with_sizes):
        if i in used_indices:
            continue
        if total_size + size <= target_bytes:
            selected.append((media, size))
            total_size += size
            used_indices.add(i)

    print("\nSelected medias")
    print("=" * 72)
    print(f"{'#':<4} {'Media':<50} {'Size (GB)':>1}")
    print("-" * 72)

    for i, (media, size) in enumerate(selected, 1):
        name = truncate_middle(os.path.basename(media), 50)
        print(f"{i:<4} {name:<50} {bytes_to_gb(size):>10.2f}")

    print("-" * 72)
    print(f"{'TOTAL':<55} {bytes_to_gb(total_size):>10.2f}")
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

    failed = []
    for media, _ in selected:
        print(f"Deleting: {media}")
        try:
            shutil.rmtree(media)
        except OSError as e:
            print(f"  ERROR: {e}")
            failed.append(media)

    print("\nDeletion complete.")
    if failed:
        print(f"\nFailed to delete {len(failed)} item(s):")
        for media in failed:
            print(f"  - {media}")

if __name__ == "__main__":
    main()