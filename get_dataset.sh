#!/bin/bash


algorithms_download_url="https://github.com/TheAlgorithms/Python/archive/refs/heads/master.zip"
CWD=$(pwd)
data_dir="$CWD/data"
db_target_path="$data_dir/pre-sorted"

target_db_dirs=(
    "data_structures"
    "digital_image_processing"
    "divide_and_conquer"
    "dynamic_programming"
    "fractals"
    "graphs"
    "greedy_methods"
    "hashes"
    "maths"
    "scheduling"
    "searches"
    "sorts"
    "web_programming"
    )

mkdir -p "$db_target_path"
if [[ -d "$db_target_path" ]]; then
    echo "Created $db_target_path directory"
    wget -q -P "$data_dir" "$algorithms_download_url" && echo "Downloaded Python Algorithms Dataset"
    zipped_path="$data_dir/master.zip"
    unzip -q "$zipped_path" -d "$data_dir"
    echo -e "\nMoving following directories into $db_target_path:\n"
    find "$data_dir/Python-master" -type d -print0 | while IFS= read -r -d $'\0' dir; do
        iterdirname=$(basename "$dir")
        for target_dir in "${target_db_dirs[@]}"; do
            if [[ "$target_dir" == "$iterdirname" ]]; then
                mv "$dir" "$db_target_path"
                echo -e "\t- $target_dir"
            fi
        done
    done
else
    echo "Failed to create database target directory: $db_target_path"
fi

