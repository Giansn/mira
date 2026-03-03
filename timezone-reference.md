# Time Zone Reference

## Primary Time Zones

### 1. **Bogotá, Colombia (Primary Reference)**
- **Time Zone**: COT (Colombia Time)
- **UTC Offset**: UTC-5 (no DST)
- **Abbreviation**: COT
- **Current**: Used for all user-facing time references
- **Note**: Gianluca is currently in Colombia (traveling from Switzerland)

### 2. **UTC (System Time)**
- **Time Zone**: Coordinated Universal Time
- **UTC Offset**: UTC+0
- **System Default**: All logs, timestamps, and system operations
- **Conversion**: Bogotá = UTC - 5 hours

### 3. **Switzerland (Home Base)**
- **Time Zone**: CET/CEST (Central European Time/Summer Time)
- **UTC Offset**: UTC+1 (CET) / UTC+2 (CEST)
- **Current**: Not in use (Gianluca traveling)
- **Note**: Home base is Switzerland (FHNW, Bern)

## Time Conversion

### Quick Reference
```
Bogotá (COT) = UTC - 5 hours
UTC = Bogotá + 5 hours
Switzerland (CET) = UTC + 1 hour
Switzerland (CEST) = UTC + 2 hours
```

### Common Times
| Bogotá | UTC | Switzerland (CET) | Note |
|--------|-----|-------------------|------|
| 09:00 | 14:00 | 15:00 | Morning in Bogotá |
| 12:00 | 17:00 | 18:00 | Noon in Bogotá |
| 18:00 | 23:00 | 00:00+1 | Evening in Bogotá |
| 21:00 | 02:00+1 | 03:00+1 | Night in Bogotá |

## Usage Guidelines

### 1. **User Communication**
- Always use **Bogotá time** when referring to times for Gianluca
- Include both times when precision matters: "14:00 UTC (09:00 Bogotá)"
- For scheduling: "Tomorrow at 09:00 Bogotá (14:00 UTC)"

### 2. **System Operations**
- Logs and timestamps: **UTC** (system default)
- Cron jobs: **UTC** (system scheduling)
- File timestamps: **UTC**

### 3. **Memory and Documentation**
- Memory files: Include both times: `2026-03-02 19:40 UTC (14:40 Bogotá)`
- Important events: Primary reference is Bogotá time
- Historical context: Original timezone noted

### 4. **Scheduling Considerations**
- **Working hours**: 09:00-18:00 Bogotá (14:00-23:00 UTC)
- **Quiet hours**: 22:00-08:00 Bogotá (03:00-13:00 UTC)
- **Heartbeats**: Schedule considering Bogotá daytime
- **Moltbook**: 09:00 UTC = 04:00 Bogotá (early morning)

## Time Zone Tools

### Python Conversion
```python
from datetime import datetime, timezone, timedelta
import pytz

# Current times
utc_now = datetime.now(timezone.utc)
bogota_tz = pytz.timezone('America/Bogota')
bogota_now = utc_now.astimezone(bogota_tz)

print(f"UTC: {utc_now.strftime('%Y-%m-%d %H:%M')}")
print(f"Bogotá: {bogota_now.strftime('%Y-%m-%d %H:%M')}")
```

### Bash Conversion
```bash
# Current time in Bogotá
TZ=America/Bogota date

# Convert UTC to Bogotá
date -u +"%Y-%m-%d %H:%M UTC" && TZ=America/Bogota date +"(%Y-%m-%d %H:%M Bogotá)"
```

## Important Notes

### 1. **No Daylight Saving Time**
- Colombia does not observe DST
- Bogotá is always UTC-5
- Switzerland observes DST (CET/CEST)

### 2. **Travel Context**
- Gianluca: Switzerland-based, currently in Colombia
- Time references should match current location
- When he returns to Switzerland, switch to CET/CEST

### 3. **System Impact**
- Cron jobs remain in UTC (unaffected)
- Log analysis uses UTC
- User communication uses Bogotá time

### 4. **Future Changes**
- Update this document when timezone changes
- Track Gianluca's location in USER.md
- Adjust scheduling as needed

## Examples

### Correct Format
```
✅ "The meeting is at 15:00 Bogotá (20:00 UTC)"
✅ "Completed at 2026-03-02 19:40 UTC (14:40 Bogotá)"
✅ "Scheduled for tomorrow 10:00 Bogotá"
```

### Incorrect Format
```
❌ "The meeting is at 20:00" (missing timezone)
❌ "Completed at 14:40" (assumes Bogotá without context)
❌ "3 PM" (ambiguous)
```

## Maintenance

### Regular Updates
1. Check current timezone in USER.md
2. Update this document if timezone changes
3. Verify time conversions are accurate
4. Adjust scheduling for optimal times

### Version History
- **2026-03-02**: Created with Bogotá (UTC-5) as primary reference
- **Note**: Will update when Gianluca returns to Switzerland