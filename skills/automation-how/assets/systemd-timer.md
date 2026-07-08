# systemd timer — the sturdier cron (Linux, user-level, no root)

User timers need no sudo, survive reboots, log to the journal, and won't overlap runs. Put both files in `~/.config/systemd/user/`.

`myjob.service`:

```ini
[Unit]
Description=My job

[Service]
Type=oneshot
# absolute paths — the unit env is minimal
WorkingDirectory=%h/path/to/job
ExecStart=/usr/bin/python3 %h/path/to/job/job.py
# secrets from an env file (chmod 600), never inline:
EnvironmentFile=%h/path/to/job/.env
```

`myjob.timer`:

```ini
[Unit]
Description=Run My job daily

[Timer]
OnCalendar=*-*-* 09:00:00     # daily 09:00 local time
Persistent=true               # catch up if the machine was off
RandomizedDelaySec=120        # optional jitter

[Install]
WantedBy=timers.target
```

Enable and inspect:

```bash
systemctl --user daemon-reload
systemctl --user enable --now myjob.timer
systemctl --user list-timers            # see next run
journalctl --user -u myjob.service -f   # watch logs
systemctl --user disable --now myjob.timer   # stop it
```

`OnCalendar` examples: `hourly` · `*-*-* *:00/15:00` (every 15 min) · `Mon..Fri 09:00` · `weekly`. Validate with `systemd-analyze calendar "Mon..Fri 09:00"`.

For a plain-cron equivalent instead:

```
0 9 * * *  cd /home/you/path/to/job && /usr/bin/python3 job.py >> job.log 2>&1
```
