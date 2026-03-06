# The Rise of Script Kiddies & Virus Culture

> "A love letter from Manila brought the world's email to its knees. The attacker was a college student. He was never convicted — because no cybercrime law existed in the Philippines."

---

## 🎬 The Scene: May 4, 2000 — Manila, Philippines

A college student named **Onel de Guzman** is frustrated. He's 24, studying at AMA Computer College, and he's just had his thesis proposal rejected. His idea: a program that steals internet passwords so people in the Philippines — where internet access is expensive — can go online for free.

His professors said no. It's illegal, they said.

So de Guzman does something else. He takes his password-stealing code, wraps it in a Visual Basic Script, attaches it to an email with the subject line:

**"ILOVEYOU"**

The body of the email says: *"Kindly check the attached LOVELETTER coming from me."*

The attachment is called: **LOVE-LETTER-FOR-YOU.txt.vbs**

Windows hides the `.vbs` extension by default. Users see: `LOVE-LETTER-FOR-YOU.txt` — looks like a harmless text file.

Within **24 hours**, the ILOVEYOU worm has infected an estimated **45 million computers** across the planet. It causes approximately **$10 billion in damage**. The Pentagon, CIA, British Parliament, and nearly every major corporation in the world is affected.

It's the most destructive computer virus in history. And it was written by a college student who just wanted free internet.

---

## The Virus Explosion: 1999–2003

The late 1990s and early 2000s were the golden age of viruses. A strange subculture emerged: teenagers and young adults writing malicious code not for money, but for **fame**, **fun**, and **bragging rights**.

They were called **script kiddies** — a derogatory term for people who used pre-made hacking tools and code without really understanding how they worked. But some of them created code that took down global infrastructure.

### The Big Three: Melissa, ILOVEYOU, Code Red

#### Melissa (March 26, 1999)

- **Creator**: David L. Smith, a 30-year-old from New Jersey
- **Type**: Macro virus embedded in a Word document
- **Spread Method**: Emailed itself to the first 50 people in the victim's Outlook address book
- **Subject Line**: "Important Message From [your friend's name]"
- **Damage**: Crashed email servers at Microsoft, Intel, and the US Marine Corps
- **Estimated Cost**: $80 million
- **Named After**: A stripper Smith had met in Florida

**How Melissa worked:**

1. User receives email from someone they know → opens the Word document
2. Word macro executes automatically (macros were enabled by default!)
3. Macro accesses Microsoft Outlook
4. Sends copies of itself to the first 50 contacts
5. Each recipient trusts the email (it came from someone they know)
6. Exponential growth — 50 × 50 × 50 = 125,000 emails in three hops

Smith was caught because he was identified through the **GUID** (Globally Unique Identifier) embedded in the Word document. Every Microsoft Office document contained a hardware fingerprint of the computer that created it. Smith didn't know this.

**Sentence**: 20 months in federal prison and a $5,000 fine.

#### ILOVEYOU (May 4, 2000)

- **Creator**: Onel de Guzman, 24-year-old student in the Philippines
- **Type**: VBS worm that spreads via email and overwrites files
- **Spread Method**: Emailed itself to everyone in the victim's address book
- **Damage**: Overwrote image files (.jpg, .jpeg), music files (.mp3), and system files
- **Estimated Cost**: $10 billion
- **Infections**: 45 million computers in one day

**Why it was so destructive:**

Unlike Melissa (which just sent emails), ILOVEYOU was actively destructive:

| File Extension | What ILOVEYOU Did |
|---|---|
| `.jpg`, `.jpeg` | Replaced with a copy of the worm |
| `.mp3` | Hidden and replaced with worm copy |
| `.vbs`, `.js` | Overwrote with worm code |
| `.css`, `.hta` | Overwrote with worm code |
| IRC channel scripts | Modified to spread the worm |
| IE start page | Changed to download a password-stealing trojan |

The worm also installed a **password-stealing trojan** that sent captured passwords to an email address in the Philippines.

**Legal outcome**: Onel de Guzman was identified and questioned by Filipino authorities. But the Philippines had **no cybercrime law** in 2000. He couldn't be charged with any crime. He was released.

The incident prompted the Philippines to pass the **E-Commerce Act of 2000** — but it couldn't be applied retroactively. De Guzman was never prosecuted.

⚠️ In 2020, a journalist tracked down de Guzman. He was working in a small phone repair booth in metro Manila. He expressed regret and said he never expected the worm to spread so widely.

#### Code Red (July 19, 2001)

- **Creator**: Unknown
- **Type**: Worm targeting Microsoft IIS web servers
- **Spread Method**: Exploited a buffer overflow vulnerability (not via email)
- **Notable Feature**: Defaced websites with "Hacked By Chinese!"
- **Infections**: 359,000 servers in 14 hours
- **Estimated Cost**: $2.6 billion

Code Red was different from Melissa and ILOVEYOU because it didn't require human interaction. It was fully automated — the worm scanned the internet for vulnerable IIS servers, exploited the buffer overflow, installed itself, and began scanning for more targets. No email, no attachments, no clicking required.

Code Red II (August 2001) was even worse — it installed a **backdoor** that gave attackers complete remote control of the infected server.

---

## The Complete Malware Family Tree

By the early 2000s, malware had diversified into a complete ecosystem. Here's every type, explained simply:

### Malware That Needs Human Help

| Type | How It Spreads | What It Does | Example |
|---|---|---|---|
| **Virus** | Attaches to legitimate files; user must run the file | Copies itself into other files, may destroy data | CIH/Chernobyl |
| **Trojan** | Disguised as useful software; user installs it | Provides backdoor access, steals data | Back Orifice, SubSeven |
| **Macro Virus** | Embedded in documents (Word, Excel); auto-runs when opened | Spreads via email, modifies documents | Melissa |
| **Dropper** | User downloads/runs it | Installs other malware silently | Various |

### Malware That Spreads Itself

| Type | How It Spreads | What It Does | Example |
|---|---|---|---|
| **Worm** | Exploits network vulnerabilities; no human needed | Self-replicates across networks | Morris Worm, Code Red |
| **Email Worm** | Emails itself using victim's address book | Spreads exponentially via social trust | ILOVEYOU, Melissa |
| **Boot Sector Virus** | Infects the boot sector of disks/USB drives | Runs before the OS, very hard to remove | Stoned, Brain |

### Malware That Hides

| Type | How It Works | Why It's Dangerous | Example |
|---|---|---|---|
| **Rootkit** | Modifies the OS to hide its presence | Invisible to antivirus, survives reboots | Sony BMG rootkit |
| **Bootkit** | Infects the master boot record | Loads before the OS and antivirus | Nemesis |
| **Fileless Malware** | Lives only in memory (RAM) | Nothing on disk for antivirus to scan | PowerShell-based attacks |
| **Polymorphic Virus** | Changes its code each time it copies itself | Defeats signature-based antivirus | Storm Worm |
| **Metamorphic Virus** | Completely rewrites its code with each generation | Even behavioral analysis struggles | Zmist |

### Malware That Steals

| Type | What It Steals | How | Example |
|---|---|---|---|
| **Keylogger** | Every keystroke you type | Records keyboard input | Ardamax |
| **Spyware** | Browsing habits, personal data | Monitors all activity silently | CoolWebSearch |
| **Adware** | Your attention (shows ads) | Injects ads into browsers | Gator, Bonzi Buddy |
| **Password Stealer** | Login credentials | Intercepts password entry or reads stored passwords | Various |
| **Banking Trojan** | Bank login credentials | Overlays fake login pages | Zeus, SpyEye |
| **Screen Scraper** | Whatever's on your screen | Takes periodic screenshots | Various |
| **Clipboard Stealer** | Copied data (crypto addresses, passwords) | Monitors clipboard and replaces content | CryptoShuffler |

### Malware That Holds Hostage (Preview — Full Chapter Later)

| Type | What It Does | First Major Incident |
|---|---|---|
| **Ransomware** | Encrypts files, demands payment | AIDS Trojan (1989), CryptoLocker (2013) |
| **Screenlocker** | Locks the screen, demands payment | WinLock (2010) |
| **Doxware** | Threatens to publish stolen data | Chimera (2015) |

---

## Famous Viruses of the Era: A Hall of Infamy

| Year | Virus/Worm | Damage | Interesting Fact |
|---|---|---|---|
| 1986 | **Brain** | First PC virus | Created by two brothers in Pakistan as anti-piracy measure |
| 1992 | **Michelangelo** | Overhyped, minimal damage | Media predicted 5 million infections; actual: a few thousand |
| 1998 | **CIH/Chernobyl** | Overwrote hard drive data AND BIOS | Named after Chernobyl because it activated on April 26 |
| 1999 | **Melissa** | $80M in damage | Named after a stripper |
| 1999 | **Happy99** | First worm to spread via email | Showed fireworks animation while installing itself |
| 2000 | **ILOVEYOU** | $10B in damage | Creator was never charged |
| 2001 | **Anna Kournikova** | Promised photos of tennis star | Created by a Dutch teenager using a virus-creation kit |
| 2001 | **Code Red** | $2.6B, 359K servers | Spelled out "Hacked By Chinese!" on defaced websites |
| 2001 | **Nimda** | Spread via 5 different methods | Name is "admin" spelled backwards |
| 2003 | **SQL Slammer** | Infected 75,000 servers in 10 minutes | Only 376 bytes — one of the smallest worms ever |
| 2003 | **Blaster** | Tried to DDoS Microsoft's update site | Contained message: "Billy Gates, stop making money" |
| 2004 | **Sasser** | Crashed machines running unpatched Windows | Created by an 18-year-old German student on his birthday |
| 2004 | **MyDoom** | Fastest-spreading email worm ever | Generated 25% of all emails sent worldwide at its peak |

---

## SQL Slammer: When 376 Bytes Took Down the Internet

**SQL Slammer** deserves special attention because it demonstrates how a tiny piece of code can cause massive damage.

On January 25, 2003, at 5:30 AM UTC, a worm **just 376 bytes long** was released. It exploited a buffer overflow in Microsoft SQL Server 2000's Resolution Service.

### How It Spread

1. Send a 376-byte UDP packet to a random IP address on port 1434
2. If the target was running an unpatched SQL Server, the buffer overflow triggered
3. The worm's code executed in memory (fileless — nothing written to disk)
4. The infected server immediately began spraying 376-byte packets at random IP addresses
5. Each infected server could send thousands of packets per second

### The Speed

- **0 minutes**: 1 infected server
- **1 minute**: ~1,000 infected servers
- **3 minutes**: Scanning the entire internet every 5.5 seconds
- **10 minutes**: 75,000 servers infected
- **30 minutes**: Internet backbone routers failing under flood of traffic

The internet effectively **went dark** for several hours. ATMs stopped working. Airline reservation systems crashed. Emergency 911 systems failed. A 376-byte packet — smaller than this paragraph — took down critical global infrastructure.

The patch for the vulnerability had been available for **6 months** before Slammer struck. 75,000 servers were still unpatched. This is perhaps the most important lesson:

> **Security patches only work if you apply them. Knowing about a vulnerability and fixing it are two entirely different things.**

---

## The Script Kiddie Phenomenon

The term "script kiddie" emerged in the late 1990s to describe a new breed of hacker: people who used pre-made tools without understanding how they worked.

### The Tools of the Trade

| Tool | What It Did | Skill Required |
|---|---|---|
| **Back Orifice** (1998) | Remote administration trojan for Windows | Click and install |
| **SubSeven** (1999) | More advanced remote trojan with GUI | Very low |
| **Netbus** (1998) | Remote control of Windows machines | Point and click |
| **L0phtCrack** (1997) | Windows password cracker | Download and run |
| **nmap** (1997) | Network scanner (legitimate tool used for recon) | Some knowledge needed |
| **Low Orbit Ion Cannon (LOIC)** | DDoS attack tool | Click one button |

These tools democratized hacking. You no longer needed to understand buffer overflows, assembly language, or networking protocols. You could download a tool, point it at a target, and cause real damage.

The script kiddie era proved an important principle:

> **The skill barrier for attacking is always lower than the skill barrier for defending.**

An attacker can use a point-and-click tool. A defender needs to understand networking, operating systems, application security, incident response, and forensics. This asymmetry is one of the fundamental challenges of cybersecurity.

---

## 🔑 Key Takeaways

1. **Email + human trust = perfect attack vector** — Melissa and ILOVEYOU exploited trust in senders, not technical vulnerabilities
2. **No cybercrime law = no consequences** — ILOVEYOU showed that global attacks require global legal frameworks
3. **Malware has diversified into a complete ecosystem** — viruses, worms, trojans, rootkits, spyware all serve different purposes
4. **Patches only work if applied** — SQL Slammer exploited a 6-month-old vulnerability on 75,000 unpatched servers
5. **Attack tools are democratized** — script kiddie tools mean anyone can attack; defense requires expertise

---

> **Next Chapter**: *How Firewalls & Antivirus Were Born* → The defense industry responds. The first firewalls, antivirus products, and intrusion detection systems emerge. But every defense creates a new attack — and the arms race accelerates.
