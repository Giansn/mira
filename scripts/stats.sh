#!/bin/bash
# Mira /stats — compact system + session overview

echo "=== SYSTEM ==="
echo "Uptime:    $(uptime -p)"
echo "CPU load:  $(cut -d' ' -f1-3 /proc/loadavg)"
echo "RAM:       $(free -h | awk '/^Mem/{print $3 " used / " $2 " total"}')"
echo "Swap:      $(free -h | awk '/^Swap/{print $3 " used / " $2 " total"}')"
echo "Disk /:    $(df -h / | awk 'NR==2{print $3 " used / " $2 " total (" $5 ")"}')"
echo ""

echo "=== OPENCLAW ==="
echo "Gateway:   $(openclaw gateway status 2>/dev/null | head -1 || echo 'unknown')"
PENDING=$(cat ~/.openclaw/exec-approvals-pending.json 2>/dev/null | grep -c '"id"' || echo 0)
echo "Pending approvals: $PENDING"
echo ""

echo "=== THESIS ==="
LATEST=$(ls -t /home/ubuntu/.openclaw/workspace/BA_Thesis* /home/ubuntu/.openclaw/workspace/thesis* 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  echo "Last file:  $(basename $LATEST)"
  echo "Modified:   $(date -r "$LATEST" '+%Y-%m-%d %H:%M UTC')"
  if [[ "$LATEST" == *.md ]]; then
    WORDS=$(wc -w < "$LATEST")
    echo "Words:      $WORDS"
  fi
else
  echo "No thesis files found"
fi
echo ""

echo "=== SUB-AGENTS ==="
ls /tmp/openclaw-subagent-* 2>/dev/null | wc -l | xargs -I{} echo "Active: {}"
echo ""

echo "=== WORKSPACE ==="
echo "Size:      $(du -sh /home/ubuntu/.openclaw/workspace 2>/dev/null | cut -f1)"
echo "Files:     $(find /home/ubuntu/.openclaw/workspace -maxdepth 1 -type f | wc -l)"
