#!/bin/bash
# Mira /stats — enhanced system + session + hardware + API overview

echo "=== HARDWARE ==="
echo "Host:      $(hostname)"
echo "Kernel:    $(uname -r)"
echo "CPU:       $(lscpu | awk '/Model name/{sub(/@.*/, ""); print $4, $5, $6, $7, $8, $9}')"
echo "Cores:     $(nproc) cores"
echo "RAM:       $(free -h | awk '/^Mem/{print $3 " used / " $2 " total"}')"
echo "Swap:      $(free -h | awk '/^Swap/{print $3 " used / " $2 " total"}')"
echo "Disk /:    $(df -h / | awk 'NR==2{print $3 " used / " $2 " total (" $5 ")"}')"
echo ""

echo "=== SYSTEM ==="
echo "Uptime:    $(uptime -p)"
echo "Load:      $(cut -d' ' -f1-3 /proc/loadavg)"
echo ""

echo "=== GATEWAY ==="
GW_STATUS=$(openclaw gateway status 2>/dev/null | head -5)
echo "$GW_STATUS"
echo ""

echo "=== MODEL & API ==="
CONFIG_JSON=$(cat ~/.openclaw/openclaw.json)
PRIMARY_MODEL=$(echo "$CONFIG_JSON" | jq -r '.agents.defaults.model.primary // "unknown"')
REASONING=$(echo "$CONFIG_JSON" | jq -r '.models.providers.minimax.models[] | select(.id | contains("Lightning")) | .reasoning')
CTX_WINDOW=$(echo "$CONFIG_JSON" | jq -r '.models.providers.minimax.models[0].contextWindow // 200000')
CTX_K=$((CTX_WINDOW / 1000))
echo "Model:     $PRIMARY_MODEL"
echo "Context:   ${CTX_K}k tokens"
echo "Reasoning: $REASONING"

# Context usage from active session
CTX_USAGE=$(openclaw sessions 2>/dev/null | grep "main" | head -1 | awk -F'(' '{print $2}' | cut -d'%' -f1)
if [ -n "$CTX_USAGE" ]; then
  echo "Ctx used:  $CTX_USAGE%"
fi

# TPS test
START=$(date +%s%N)
OUTPUT=$(openclaw agent --local --message "Count from 1 to 50, one number per line." --session-id stats-tps-$(date +%s) 2>&1 | grep -E "^[0-9]+$" | tail -1)
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
TOKEN_COUNT=50
if [ -n "$OUTPUT" ] && [ "$DURATION" -gt 0 ]; then
  TPS=$(echo "scale=1; $TOKEN_COUNT * 1000 / $DURATION" | bc)
  echo "TPS:       ~$TPS tokens/sec"
fi
echo ""

echo "=== RUNTIME ==="
echo "Node:      $(node --version 2>/dev/null)"
echo "OS:        $(uname -s) $(uname -m)"
RUNTIME_INFO=$(openclaw status 2>/dev/null | grep "Runtime" | head -1)
if [ -n "$RUNTIME_INFO" ]; then
  echo "$RUNTIME_INFO" | awk '{print "Runtime:   " $2}'
fi
echo "Version:   $(openclaw --version 2>/dev/null | head -1 | awk '{print $2}')"
echo ""

echo "=== CACHE ==="
MAIN_CACHE=$(openclaw sessions 2>/dev/null | grep "telegram:direct" | head -1 | grep -oP '\d+% cached' | head -1)
if [ -n "$MAIN_CACHE" ]; then
  echo "Main:      $MAIN_CACHE"
fi
MEM_CACHE=$(openclaw status 2>/dev/null | grep "Cache:" | head -1)
if [ -n "$MEM_CACHE" ]; then
  echo "$MEM_CACHE" | awk '{$1=""; print "Memory:" $0}'
fi
echo ""

echo "=== AGENTS & SESSIONS ==="
AGENT_COUNT=$(openclaw sessions 2>/dev/null | grep -c "direct" || echo 0)
echo "Sessions:  $AGENT_COUNT"
echo "Active:   main (telegram)"
echo ""

echo "=== THESIS ==="
LATEST=$(ls -t /home/ubuntu/.openclaw/workspace/BA_Thesis* /home/ubuntu/.openclaw/workspace/thesis* 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  echo "File:      $(basename $LATEST)"
  echo "Modified:  $(date -r "$LATEST" '+%Y-%m-%d %H:%M UTC')"
  if [[ "$LATEST" == *.md ]]; then
    WORDS=$(wc -w < "$LATEST")
    echo "Words:     $WORDS"
  fi
else
  echo "No thesis files"
fi
echo ""

echo "=== WORKSPACE ==="
echo "Size:      $(du -sh /home/ubuntu/.openclaw/workspace 2>/dev/null | cut -f1)"
echo "Files:     $(find /home/ubuntu/.openclaw/workspace -maxdepth 1 -type f | wc -l)"
echo "Skills:    $(ls -d ~/.openclaw/workspace/skills/*/ 2>/dev/null | wc -l)"
