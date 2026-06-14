from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="sarvamai/sarvam-1",
    local_dir="sarvam_local",
    local_dir_use_symlinks=False
)

print("Download Complete")