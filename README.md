# Lock Screen Simulator

A **educational simulation** of a Windows lock screen with full‑screen UI, password protection, decoy passwords, biometric mock‑ups, cooldown timer, fake BSOD, persistence mechanisms, logging, and optional audio feedback.

## Project Structure
```
LockScreenProject/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── persistence_manager.py
│   ├── lock_screen.py
│   ├── bsod_manager.py
│   ├── audio_manager.py
│   ├── vm_detector.py
│   └── logger.py
│
├── educational_simulation.txt
├── requirements.txt
└── README.md
```

## Setup & Run
1. **Create the folder** and copy the files below.
2. Ensure you are running inside an isolated VM.
3. Install dependencies (optional):
   ```bash
   pip install -r requirements.txt
   ```
4. Run the simulator:
   ```bash
   python src/main.py
   ```

## Safety
- This is **strictly for study** and **must not be deployed** on real systems.
- A file named `educational_simulation.txt` must exist in the project root to bypass the safety prompt.
- Press **ESC** at any time to exit safely.

