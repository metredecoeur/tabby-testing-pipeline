
set shell := ["bash", "-c"]
cwd := `pwd`
python_version_file := ".python-version"
pyproject_file := "pyproject.toml"
requirements_file := "requirements.txt"
uv_lock_file := "uv.lock"
get_dataset_script := "get_dataset.sh"
python_scripts := ["src/sort_data-1.py", "query_server-2.py", "similarity_tester-3.py" "static_tester-3.py" "make_plot-4.py"]


install-uv:
    pipx install uv

recreate-env:
    just install-uv
    uv venv -project {{cwd}}

get-dataset:
    bash {{get_dataset_script}}


run-pipeline:
    for script in {{python_scripts}}; do
        python "$$script"
    done

all: recreate-env get-dataset run-pipeline

