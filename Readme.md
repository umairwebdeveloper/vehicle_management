# Automated Borgmatic Backup Setup

This document describes how to configure BorgBackup + borgmatic for passwordless, non-interactive daily backups over SSH (port 2232) to a remote backup server. It also covers how to list and browse backups, suppress Borg location warnings, and set up convenient shell aliases.

---

## 1. Generate an SSH key without passphrase

On the **primary** server (23.141.136.108), generate an SSH key dedicated to Borg:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/borg_nopass -N ""
```

## 2. Copy the public key to the backup server

```bash
ssh-copy-id -i ~/.ssh/borg_nopass.pub -p 2232 txfiber@23.141.136.107
```

## 3. Configure root’s SSH settings

Since the borgmatic systemd timer runs as `root`, install the key and configure SSH for root:

```bash
sudo mkdir -p /root/.ssh
sudo cp ~/.ssh/borg_nopass /root/.ssh/
sudo chmod 600 /root/.ssh/borg_nopass
sudo tee /root/.ssh/config <<EOF
Host backup
  HostName 23.141.136.107
  Port 2232
  User txfiber
  IdentityFile /root/.ssh/borg_nopass
  StrictHostKeyChecking no
EOF
sudo chmod 600 /root/.ssh/config
```

Test passwordless SSH as root:

```bash
sudo ssh backup echo OK
```

You should see `OK` with no password prompt.

## 4. Supply the Borg repository passphrase in systemd

Create a systemd drop-in to export the Borg environment variables:

```bash
sudo mkdir -p /etc/systemd/system/borgmatic.service.d
sudo tee /etc/systemd/system/borgmatic.service.d/env.conf <<EOF
[Service]
Environment=BORG_RSH="ssh -oBatchMode=yes backup"
Environment=BORG_PASSPHRASE="YourBorgRepoPassphrase"
EOF
sudo systemctl daemon-reload
```

* Replace `YourBorgRepoPassphrase` with the passphrase you used during `borg init`.
* `BORG_RSH` ensures Borg uses our `backup` SSH alias.

## 5. Enable and start the borgmatic timer

```bash
sudo systemctl enable --now borgmatic.timer
```

This sets up a daily run (via the built-in systemd timer) of borgmatic without any interactive prompts.

## 6. Verify the setup

* **Logs**:

  ```bash
  sudo journalctl -u borgmatic.service -f
  ```
* **Next run**:

  ```bash
  systemctl list-timers borgmatic.timer
  ```
* **Repository contents**:

  ```bash
  borg list ssh://txfiber@23.141.136.107:2232/var/backups/borg/primary
  ```

If you see regular snapshots and no password prompts, your automated backup is working successfully!

---

## 7. Listing and inspecting backups

### 7.1 List all archives

* **Via alias** (requires SSH alias below):

  ```bash
  borg list backup:/var/backups/borg/primary
  ```
* **Full URL**:

  ```bash
  borg list ssh://txfiber@23.141.136.107:2232/var/backups/borg/primary
  ```

### 7.2 View archive metadata and file listing

* **Show metadata** (size, hostname, timestamp):

  ```bash
  borg info backup:/var/backups/borg/primary::primary-YYYY-MM-DD
  ```
* **List files and directories** inside an archive:

  ```bash
  borg list backup:/var/backups/borg/primary::primary-YYYY-MM-DD
  ```

  This prints the full file tree stored in that snapshot.

### 7.3 Mount an archive (readonly)

```bash
sudo mkdir -p /mnt/borg
sudo borg mount \
  backup:/var/backups/borg/primary::primary-YYYY-MM-DD \
  /mnt/borg
# browse /mnt/borg/...
sudo borg umount /mnt/borg
```

### 7.4 Extract files

* **Entire archive** into current directory:

  ```bash
  borg extract backup:/var/backups/borg/primary::primary-YYYY-MM-DD
  ```
* **Single file or folder**:

  ```bash
  borg extract backup:/var/backups/borg/primary::primary-YYYY-MM-DD path/to/file
  ```

---

## 8. Suppress repository location warning

If you see:

```
Warning: The repository at location ssh://backup/var/backups/borg/primary was previously located at ssh://txfiber@23.141.136.107:2232/var/backups/borg/primary
```

You can update the recorded location:

```bash
borg config \
  --set repository.location=ssh://backup/var/backups/borg/primary \
  backup:/var/backups/borg/primary
```

This aligns the internal `repository.location` with your SSH alias URL.

---

## 9. Configure your personal SSH alias

On your **personal account** (not root), add a `backup` host entry in `~/.ssh/config`:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
tee ~/.ssh/config <<EOF
Host backup
  HostName 23.141.136.107
  Port 2232
  User txfiber
  IdentityFile ~/.ssh/borg_nopass
  StrictHostKeyChecking no
EOF
chmod 600 ~/.ssh/config
```

Test it:

```bash
ssh backup echo OK
```

You should see `OK` with no prompt.

---

## 10. Convenience shell aliases

Add the following to your personal `~/.bashrc` (or `~/.zshrc`):

```bash
# Borgmatic backup shortcuts
alias blist='export BORG_PASSPHRASE="ACTUALPASSPHRASE" BORG_RSH="ssh -oBatchMode=yes -i ~/.ssh/borg_nopass" && borg list backup:/var/backups/borg/primary'
alias bls='blist'  # shorthand
```

* After reloading your shell, run `blist` or `bls` to list backups instantly without prompts.

---

**Done!** You now have:

* Automated daily backups via borgmatic.
* Passwordless SSH for both root and your user account.
* Non-interactive repository unlocking.
* Commands to list, inspect, mount, and extract archives.
* A short shell alias (`blist`) for quick backup listings.

Happy restoring! 🚀
