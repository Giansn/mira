#!/usr/bin/env python3
"""
Fix OpenClaw E5 configuration - remove invalid keys and place them correctly
"""

import json
import os
import sys
from datetime import datetime

def main():
    """Fix OpenClaw configuration by removing invalid keys."""
    
    config_path = "/home/ubuntu/.openclaw/openclaw.json"
    backup_path = f"{config_path}.backup-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print("🔧 Fixing OpenClaw E5 configuration")
    print("=" * 60)
    print("Issue: 'chunkTokens' and 'chunkOverlap' are invalid keys")
    print("These should be configured differently or not at this level")
    print()
    
    # Load current configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False
    
    # Create backup
    try:
        import shutil
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Fix the configuration
    if "agents" in config and "defaults" in config["agents"]:
        if "memorySearch" in config["agents"]["defaults"]:
            mem_search = config["agents"]["defaults"]["memorySearch"]
            
            # Remove invalid keys
            invalid_keys = ["chunkTokens", "chunkOverlap"]
            removed = []
            
            for key in invalid_keys:
                if key in mem_search:
                    del mem_search[key]
                    removed.append(key)
            
            if removed:
                print(f"✅ Removed invalid keys: {', '.join(removed)}")
            else:
                print("✅ No invalid keys found (already removed?)")
            
            # Check if we need to add chunk configuration elsewhere
            # Based on OpenClaw docs, chunk size might be configured differently
            # or might be automatically determined by the model
            
            print("\n📋 Current memorySearch configuration:")
            print(f"   - provider: {mem_search.get('provider', 'N/A')}")
            print(f"   - model: {mem_search.get('model', 'N/A')}")
            print(f"   - local.modelPath: {mem_search.get('local', {}).get('modelPath', 'N/A')}")
            print(f"   - hybrid search: {'Enabled' if mem_search.get('query', {}).get('hybrid', {}).get('enabled', False) else 'Disabled'}")
            
        else:
            print("❌ memorySearch not found in configuration")
            return False
    else:
        print("❌ Could not find agents.defaults in configuration")
        return False
    
    # Save fixed configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration fixed: {config_path}")
        
        # Verify the fix
        with open(config_path, 'r') as f:
            updated_config = json.load(f)
        
        mem_search = updated_config.get("agents", {}).get("defaults", {}).get("memorySearch", {})
        
        # Check that invalid keys are gone
        if "chunkTokens" not in mem_search and "chunkOverlap" not in mem_search:
            print("✅ Verification passed: Invalid keys removed")
        else:
            print("❌ Verification failed: Invalid keys still present")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        
        # Try to restore from backup
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, config_path)
                print(f"✅ Restored from backup: {backup_path}")
            except Exception as restore_error:
                print(f"❌ Could not restore from backup: {restore_error}")
        
        return False

if __name__ == "__main__":
    print("🧠 Fix OpenClaw E5 Configuration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    success = main()
    
    if success:
        print("\n✅ Configuration fix completed!")
        print("\n🎯 Next Steps:")
        print("   1. Restart OpenClaw: openclaw gateway restart")
        print("   2. Check logs for indexing progress")
        print("   3. Test memory search")
        print("\n💡 Note: E5-small-v2 has 512 token context")
        print("   OpenClaw should auto-configure appropriate chunk size")
    else:
        print("\n❌ Configuration fix failed!")
    
    sys.exit(0 if success else 1)