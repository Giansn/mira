#!/bin/bash
# Secure API Key Manager for OpenClaw
# Stores API keys in encrypted format with GPG

KEYS_DIR="$HOME/.secure-keys"
CONFIG_DIR="$HOME/.config/moltbook"
BACKUP_DIR="$HOME/.secure-backups"

# Create directories
mkdir -p "$KEYS_DIR" "$BACKUP_DIR"
chmod 700 "$KEYS_DIR" "$BACKUP_DIR"

# Function to encrypt a key
encrypt_key() {
    local service="$1"
    local key="$2"
    local label="$3"
    
    # Generate random passphrase
    local passphrase=$(openssl rand -hex 32)
    
    # Encrypt the key
    echo "$key" | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$passphrase" -out "$KEYS_DIR/${service}.enc"
    
    # Store passphrase in separate file (encrypted with master key)
    echo "$passphrase" | gpg --encrypt --recipient "$USER" --output "$KEYS_DIR/${service}.pass.gpg" 2>/dev/null || {
        echo "Warning: GPG not configured, storing passphrase in plain text (NOT SECURE)"
        echo "$passphrase" > "$KEYS_DIR/${service}.pass"
        chmod 600 "$KEYS_DIR/${service}.pass"
    }
    
    # Create metadata
    cat > "$KEYS_DIR/${service}.meta" <<EOF
service: $service
label: $label
encrypted: true
algorithm: aes-256-cbc
created: $(date -Iseconds)
last_accessed: $(date -Iseconds)
EOF
    
    chmod 600 "$KEYS_DIR/${service}.enc" "$KEYS_DIR/${service}.meta"
    echo "Encrypted key for $service stored securely"
}

# Function to decrypt a key
decrypt_key() {
    local service="$1"
    
    if [ ! -f "$KEYS_DIR/${service}.enc" ]; then
        echo "Error: No encrypted key found for $service"
        return 1
    fi
    
    # Get passphrase
    if [ -f "$KEYS_DIR/${service}.pass.gpg" ]; then
        local passphrase=$(gpg --decrypt "$KEYS_DIR/${service}.pass.gpg" 2>/dev/null)
    elif [ -f "$KEYS_DIR/${service}.pass" ]; then
        local passphrase=$(cat "$KEYS_DIR/${service}.pass")
    else
        echo "Error: No passphrase found for $service"
        return 1
    fi
    
    # Decrypt the key
    openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:"$passphrase" -in "$KEYS_DIR/${service}.enc" 2>/dev/null
    
    # Update last accessed time
    sed -i "s/last_accessed:.*/last_accessed: $(date -Iseconds)/" "$KEYS_DIR/${service}.meta"
}

# Function to rotate a key
rotate_key() {
    local service="$1"
    local new_key="$2"
    
    # Backup old key
    local timestamp=$(date +%Y%m%d_%H%M%S)
    cp "$KEYS_DIR/${service}.enc" "$BACKUP_DIR/${service}_${timestamp}.enc"
    [ -f "$KEYS_DIR/${service}.pass.gpg" ] && cp "$KEYS_DIR/${service}.pass.gpg" "$BACKUP_DIR/${service}_${timestamp}.pass.gpg"
    [ -f "$KEYS_DIR/${service}.pass" ] && cp "$KEYS_DIR/${service}.pass" "$BACKUP_DIR/${service}_${timestamp}.pass"
    cp "$KEYS_DIR/${service}.meta" "$BACKUP_DIR/${service}_${timestamp}.meta"
    
    # Encrypt new key
    encrypt_key "$service" "$new_key" "$(grep '^label:' "$KEYS_DIR/${service}.meta" | cut -d: -f2-)"
    
    echo "Key rotated for $service. Old key backed up to $BACKUP_DIR/"
}

# Function to list all stored keys
list_keys() {
    echo "Stored API Keys:"
    echo "----------------"
    for meta in "$KEYS_DIR"/*.meta; do
        [ -f "$meta" ] || continue
        local service=$(basename "$meta" .meta)
        echo "Service: $service"
        cat "$meta"
        echo "----------------"
    done
}

# Function to clean up plain text credentials
cleanup_plaintext() {
    echo "Searching for plain text credentials..."
    
    # Check common locations
    find "$HOME" -name "*.json" -type f -exec grep -l "api_key\|API_KEY\|token\|TOKEN" {} \; 2>/dev/null | while read file; do
        echo "Found potential credentials in: $file"
        # Backup before cleaning
        cp "$file" "$BACKUP_DIR/$(basename "$file")_$(date +%Y%m%d_%H%M%S).bak"
    done
    
    # Specific cleanup for moltbook credentials
    if [ -f "$CONFIG_DIR/credentials.json" ]; then
        echo "Backing up and cleaning moltbook credentials..."
        cp "$CONFIG_DIR/credentials.json" "$BACKUP_DIR/moltbook_credentials_$(date +%Y%m%d_%H%M%S).json"
        # Replace with placeholder
        cat > "$CONFIG_DIR/credentials.json" <<EOF
{
  "moltbook": {
    "api_key": "ENCRYPTED_IN_SECURE_STORAGE",
    "agent_name": "mirakl"
  },
  "moltshell": {
    "api_key": "ENCRYPTED_IN_SECURE_STORAGE"
  }
}
EOF
        echo "Moltbook credentials secured"
    fi
}

# Function to create API key usage script
create_usage_script() {
    cat > "$HOME/bin/get-moltbook-key.sh" <<'EOF'
#!/bin/bash
# Secure Moltbook API Key Retrieval
# This script retrieves the Moltbook API key from secure storage

KEYS_DIR="$HOME/.secure-keys"

if [ ! -f "$KEYS_DIR/moltbook.enc" ]; then
    echo "Error: Moltbook API key not found in secure storage" >&2
    exit 1
fi

# Decrypt and output the key
"$HOME/secure-api-manager.sh" decrypt moltbook
EOF
    
    chmod 700 "$HOME/bin/get-moltbook-key.sh"
    echo "Usage script created: $HOME/bin/get-moltbook-key.sh"
}

# Main execution
case "$1" in
    encrypt)
        encrypt_key "$2" "$3" "$4"
        ;;
    decrypt)
        decrypt_key "$2"
        ;;
    rotate)
        rotate_key "$2" "$3"
        ;;
    list)
        list_keys
        ;;
    cleanup)
        cleanup_plaintext
        ;;
    setup)
        # Initial setup: encrypt existing keys
        if [ -f "$CONFIG_DIR/credentials.json" ]; then
            moltbook_key=$(jq -r '.moltbook.api_key' "$CONFIG_DIR/credentials.json")
            moltshell_key=$(jq -r '.moltshell.api_key' "$CONFIG_DIR/credentials.json")
            
            encrypt_key "moltbook" "$moltbook_key" "Moltbook API Key for mirakl agent"
            encrypt_key "moltshell" "$moltshell_key" "Moltshell API Key"
            
            cleanup_plaintext
            create_usage_script
            
            echo "Setup complete. API keys secured."
            echo "Use: $HOME/bin/get-moltbook-key.sh to retrieve keys"
        else
            echo "Error: No credentials.json found at $CONFIG_DIR/credentials.json"
        fi
        ;;
    *)
        echo "Usage: $0 {encrypt|decrypt|rotate|list|cleanup|setup}"
        echo "  encrypt <service> <key> <label>  - Encrypt and store a key"
        echo "  decrypt <service>                - Decrypt and output a key"
        echo "  rotate <service> <new_key>       - Rotate an existing key"
        echo "  list                             - List all stored keys"
        echo "  cleanup                          - Clean up plain text credentials"
        echo "  setup                            - Initial setup with existing credentials"
        exit 1
        ;;
esac