#!/bin/bash
# Scratch: Create tmpfs scratch space for temporary files

SIZE_MB="${1:-512}"
LOCATION="${2:-/tmp}"

# Create unique scratch directory
SCRATCH_DIR="${LOCATION}/hot-workspace-$$"

mkdir -p "$SCRATCH_DIR"

if mount | grep -q "$SCRATCH_DIR"; then
    # Already mounted as tmpfs
    :
else
    # Mount as tmpfs (requires sudo or appropriate permissions)
    if [ "$LOCATION" = "/dev/shm" ]; then
        # /dev/shm is already tmpfs
        :
    else
        # Try to mount as tmpfs, fallback to regular dir
        mount -t tmpfs -o size=${SIZE_MB}M tmpfs "$SCRATCH_DIR" 2>/dev/null || {
            echo "Warning: Could not mount tmpfs, using regular directory"
        }
    fi
fi

# Output export commands
echo "export HOT_SCRATCH=\"$SCRATCH_DIR\""
echo "export HOT_SCRATCH_SIZE_MB=$SIZE_MB"
echo "echo \"Scratch space: \$HOT_SCRATCH\""
echo "echo \"Scratch size: ${SIZE_MB}MB\""
