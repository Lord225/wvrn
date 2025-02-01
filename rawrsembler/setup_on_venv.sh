#!/bin/bash

# check if $profile exists, if not create it
if [ ! -e "$HOME/.bashrc" ]; then
  touch "$HOME/.bashrc"
fi

# current folder
root=$(dirname "$(readlink -f "$0")")

# check if # rawrsembler-begin comment exists in $profile, if so remove everything between # rawrsembler-begin and # rawrsembler-end
if grep -q "# rawrsembler-begin" "$HOME/.bashrc"; then
  echo "Usuwanie poprzedniej instalacji 'lords-asm-for-mc' z $HOME/.bashrc"
  sed -i '/# rawrsembler-begin/,/# rawrsembler-end/d' "$HOME/.bashrc"
fi

# create a virtual environment
venv_dir="$root/venv"
if [ ! -d "$venv_dir" ]; then
  echo "Tworzenie wirtualnego środowiska w $venv_dir"
  python3 -m venv "$venv_dir"
fi

# activate the virtual environment and install requirements
source "$venv_dir/bin/activate"
echo "Instalowanie zależności 'lords-asm-for-mc' w $root przy użyciu pip"
pip install -r "$root/requirements.txt"
deactivate

# add # rawrsembler-begin comment to $profile
echo "# rawrsembler-begin" >> "$HOME/.bashrc"
echo "# Nie edytuj, nie usuwaj ani nie zmieniaj tych komentarzy; są używane przez 'rawrsembler' do instalacji i dezinstalacji" >> "$HOME/.bashrc"

# add alias to compile.py
compile="$root/compile.py"
echo "function rawr { source \"$venv_dir/bin/activate\" && \$@ | python3 \"$compile\" \"\$@\"; deactivate; }" >> "$HOME/.bashrc"

# Add alias to get-wvrn-bin.py
get_wvrn="$root/tools/get-wvrn-bin.py"
echo "function to-wve { source \"$venv_dir/bin/activate\" && \$@ | python3 \"$get_wvrn\" \"\$@\"; deactivate; }" >> "$HOME/.bashrc"

echo "Alias 'rawr' i 'get_wvrn' utworzony w $HOME/.bashrc"

# add $root to the PATH, if not already there
if [[ ":$PATH:" != *":$root:"* ]]; then
  echo "export PATH=\"\$PATH:$root\"" >> "$HOME/.bashrc"
fi

echo "Dodano '$root' do PATH"

echo "Gotowe"
