import json, re, subprocess
lines = open('narr.txt', encoding='utf-8').read().strip().split('\n')
LEAD, TAIL = 0.35, 0.75
scenes, t = [], 0.0
for i, line in enumerate(lines):
    d = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'raw_{i}.wav']))
    dur = LEAD + d + TAIL
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', line) if s.strip()]
    tot = sum(len(s) for s in sents); acc = 0; caps = []
    for s in sents:
        caps.append({'t': round(LEAD + d * acc / tot, 3), 'txt': s}); acc += len(s)
    scenes.append({'start': round(t, 3), 'dur': round(dur, 3), 'audio': d, 'caps': caps})
    t += dur
json.dump({'scenes': scenes, 'total': round(t, 3)}, open('timing.json', 'w'), ensure_ascii=False, indent=1)
print('total', round(t, 2), [round(s['dur'], 1) for s in scenes])
