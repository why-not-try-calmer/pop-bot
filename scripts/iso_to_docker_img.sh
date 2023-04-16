#!/usr/bin/bash
options=$@
skip_checksum=0

user_downloads_dir=$(xdg-user-dir DOWNLOAD)
download_path="${user_downloads_dir}/${default_iso_name}"
download_homepage="https://pop.system76.com/"
download_url="https://iso.pop-os.org/22.04/amd64/intel/25/pop-os_22.04_amd64_intel_25.iso"

unsq=$(which unsquashfs)
rootfs_dir_path="${user_downloads_dir}/rootfs"    
unsquash_dir_path="${user_downloads_dir}/unquashfs"
default_iso_name="pop_os.iso"
default_docker_img_name="pop-docker"

function check_requisites {
    needed_executables=("unsquashfs" "docker" "tar")
    for exe in "${needed_executables[@]}"; do
        type $exe &> /dev/null
        if [[ "$?" -ne 0 ]]; then echo "Unable to find executable '$exe'. Aborting."; exit 1; fi 
    done
    return 0
    if ! [[ -f "$download_path" ]]
    then
        echo "Unable to find ISO file. Please run again with '--download-iso'."
        exit 1
    fi
}


function clean_up {
    sudo umount /dev/loop0
    sudo rm -rf $rootfs_dir_path
    sudo rm -rf $unsquash_dir_path
}

function confirm_checksum {
    if [[ "$skip_checksum" -eq 1 ]]
    then 
        echo "Skipping checksum."
        return 0
    fi
    echo "Computing checksum..."
    checksum=$(sha256sum "$download_path")
    echo "Visit $download_homepage and make sure the SHA256 for the default image (Intel) matches: $checksum. Does it match? (y/n)"
    read reply
    if [[ "$reply" != "y" ]]; then echo "Aborting."; exit 1; fi
}

function resolve_options {
    case "${options[@]}" in 
        *"--download-iso" )             
            if ! [[ -f "$download_path" ]]
            then
                echo "Downloading ISO now..."; 
                wget -O "$download_path" "$download_url"
            else
                echo "ISO already exists."
            fi
            ;;
        *"--cleanup" )
            clean_up
            exit 0
            ;;
        *"--skip-checksum" )
            skip_checksum=1
            ;;
    esac
}

function create_docker_img {
    echo "About to create a Docker image with $download_path, using these variables:"
    config=($unsq $unsquash_dir_path $rootfs_dir_path)
    for v in "${config[@]}"; do
        echo "$v";
    done
    echo "Continue? (y/n)"
    read reply
    if [[ "$reply" != "y" ]]; then exit 1; fi

    echo "Creating directories...[1/4]"
    mkdir $rootfs_dir_path $unsquash_dir_path
    
    echo "Mounting image...[2/4]"
    sudo mount -o loop $download_path $rootfs_dir_path
    fs_path=$(find $download_path -type f | grep filesystem.squashfs)
    
    echo "Unsquashing....[3/4]"
    sudo unsquashfs -f -d "${unsquash_dir_path}/" $fs_path
    
    echo "Compressing and importing to Docker...[4/4]"
    sudo tar -C $unsquash_dir_path -c $user_downloads_dir | docker import - $default_docker_img_name
}

function main {
    check_requisites
    resolve_options
    confirm_checksum
    create_docker_img
    clean_up
}

main
