#!/bin/bash

backup_dir="$HOME/backups"
backup_config_file="/opt/local/backup_config.cfg"
log_file="/opt/local/backup_script.log"

# Ensure config dir & file exist
function check() {
    if [[ ! -d "/opt/local" ]]; then
        mkdir -p /opt/local
    fi

    if [[ ! -f "$backup_config_file" ]]; then
        touch "$backup_config_file" "$log_file"
    fi
}

function log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$log_file"
}

# Add folder path to config if valid and not already added
function add_folder() {
    
    read -p "Enter folder path to backup: " path

    resolved_path=$(readlink -f "$path" 2>/dev/null)

    if [[ -z "$resolved_path" || ! -d "$resolved_path" ]]; then
        echo "[-] Folder does not exist or cannot resolve path."
        return
    fi
    
        # Check if already added
        if grep -Fxq "$path" "$backup_config_file"; then
            echo "[!] Folder already in backup list."
        else
            echo "$path" >> "$backup_config_file"
            echo "[+] Folder added to backup list."
            log "[+] Added folder: $resolved_path"
        fi
    else
        echo "[-] Folder does not exist."
    

}

# Display all folders in config file
function display_folder_list() {
    echo "Folders set to backup:"
    if [[ ! -s "$backup_config_file" ]]; then
        echo " (none)"
    else
        cat "$backup_config_file"
    fi
}

# Remove folder from backup list (interactive)
function remove_folder() {
    if [[ ! -s "$backup_config_file" ]]; then
        echo "[!] Backup list is empty."
        return
    fi

    echo "Folders in backup list:"
    nl -w3 -s'. ' "$backup_config_file"

    read -p "Enter the number of the folder to remove (or 'q' to cancel): " num
    if [[ "$num" == "q" ]]; then
        echo "Cancelled."
        return
    fi

    # Validate input is a number and in range
    total_lines=$(wc -l < "$backup_config_file")
    if ! [[ "$num" =~ ^[0-9]+$ ]] || (( num < 1 || num > total_lines )); then
        echo "Invalid selection."
        return
    fi

    sed -i "${num}d" "$backup_config_file"
    echo "[+] Removed folder #$num from backup list."
    log  "[+] Removed folder entry number: $num"
}


# Backup all folders in the config file
function backup_all() {
    if [[ ! -s "$backup_config_file" ]]; then
        echo "[-] No folders to backup. Add folders first."
        return
    fi

    mkdir -p "$backup_dir"

    while IFS= read -r folder; do
        if [[ -d "$folder" ]]; then
            base_name=$(basename "$folder")
            backup_file="$backup_dir/${base_name}_backup_$(date +%F_%H-%M-%S).tar.gz"
            echo "[+] Backing up $folder -> $backup_file"
            tar -czf "$backup_file" -C "$(dirname "$folder")" "$base_name"
            if [[ $? -eq 0 ]]; then
                log "[+] Backup successful: $backup_file"
            else
                log "[-] Backup failed: $backup_file"
            fi
        else
            echo "[-] Skipping missing folder: $folder"
        fi
    done < "$backup_config_file"

    echo "[+] Backup completed."
}

# Interactive menu
function interactive_mode() {
    while true; do
        echo ""
        echo "Backup Script -function help_menu() {
    echo "Usage: $0 [option]"
    echo "Options:"
    echo "  -a    Add folder to backup list"
    echo "  -l    List backup folders"
    echo "  -b    Run backup for all folders"
    echo "  -i    Interactive mode"
    echo "  -r    Remove folder from backup list"
    echo "  -h    Show this help"
}
 Interactive Mode"
        echo "1) Add folder to backup list"
        echo "2) List backup folders"
        echo "3) Run backup now"
        echo "4) Remove folder from backup list"
        echo "5) Exit"
        read -p "Choose an option: " opt

        case $opt in
            1) add_folder ;;
            2) display_folder_list ;;
            3) backup_all ;;
            4) echo "Exiting."; break ;;
            5) remove_folder;;
            *) echo "Invalid option." ;;
        esac
    done
}

# Help menu
function help_menu() {
    cat <<EOF
Usage: $0 [option]

Options:
  -a    Add folder to backup list
  -l    List backup folders
  -b    Run backup for all folders
  -r    Remove folder from backup list
  -i    Interactive mode
  -h    Show this help

Examples:
  $0 -a            # Add a folder interactively
  $0 -l            # List all folders
  $0 -b            # Backup all folders
  $0 -r            # Remove a folder interactively
  $0 -i            # Run interactive menu

Note:
  Config file is at $backup_config_file
  Backup archives are saved under $backup_dir
  Logs are saved to $log_file
EOF
}

# Main logic
check

if [[ $EUID -ne 0 ]]; then
    echo "[-] Please run this script as root."
    exit 1
fi

case "$1" in
    -a) add_folder ;;
    -l) display_folder_list ;;
    -b) backup_all ;;
    -i) interactive_mode ;;
    -r) remove_folder;;
    -h|*) help_menu ;;
esac
