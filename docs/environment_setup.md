# Environment Setup (Technical)

> Target Python: **3.11.8**  
> Virtual env name: **vitd_env**

## 0) Prerequisites

- **Python 3.11.8** installed on your system  
  > The virtual environment will use the version currently installed — make sure it's 3.11.8.  
- **Git** for cloning the repository  
- **Visual Studio Code** (recommended) with:
  - *Python* extension
  - *Jupyter* extension (for notebooks)
- Build tools for compiling packages from source (only if needed):
  - **Windows**: Visual Studio Build Tools  
  - **Ubuntu/Debian**: `sudo apt-get install -y build-essential python3-dev`  
  - **macOS**: `xcode-select --install`

---

## 1) Clone repository
```bash
git clone https://github.com/paulairazoqui/vitD-transcriptomic-profiling.git
cd vitD-transcriptomic-profiling
```

## 2) Create the virtual environment
```bash
python -m venv vitd_env
```

## 3) Activate the environment
***Windows (PowerShell):***
```bash
.\vitd_env\Scripts\activate
```

***Linux / Mac:***
```bash
source vitd_env/bin/activate
```

## 4) Install required packages
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) (Optional) Register Jupyter kernel
```bash
python -m ipykernel install --user --name vitd_env --display-name "vitd_env (Python 3.11.8)"
```

### 6) Deactivate when done
```bash
deactivate
```

## Troubleshooting
- **PowerShell won't activate the venv**  
  Run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Kernel not showing in Jupyter**  
  Re-run the kernel registration step:
  ```bash
  python -m ipykernel install --user --name vitd_env --display-name "vitd_env (Python 3.11.8)"
  ```

- **Permission issues on Linux/Mac**

  Run: `chmod +x vitd_env/bin/activate`