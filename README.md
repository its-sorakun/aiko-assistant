# Aiko: Native OS-Aware Assistant

Aiko is an experimental, event-driven assistant built to bypass high-level GUI automation frameworks and interface directly with underlying Windows OS mechanisms. 

The purpose of this project is to investigate how LLM function calling can be mapped onto raw OS APIs. Rather than relying on fragile UI scraping, simulated inputs, or bloated orchestration libraries, the implementation drops down to Win32, WMI, and WinRT interfaces to manipulate the environment natively.

## Implementation Details

- **Autonomous Tool Execution**: Connects Gemini function calling directly to local Python API bindings.
- **DWM Z-Order Interception**: Ignores the invoking terminal by traversing the Desktop Window Manager stack downward, identifying the true foreground application.
- **Direct Memory & Thermal Probing**: Reads hardware vitals via `psutil` and attempts user-space ACPI hooks through Windows Management Instrumentation (WMI).
- **Native Registry Resolution**: Discovers executable paths natively via Windows Registry hives rather than relying on environment variables or shell searches.
- **WinRT Media Hooking**: Hooks into the asynchronous WinRT System Media Transport Controls (SMTC) to read and manipulate the global audio pipeline.

## Usage

Clone the repository and install the native bindings:
```bash
pip install -r requirements.txt
```
Configure `GEMINI_API_KEY` in a local `.env` file, and execute `python main.py`.

For a breakdown of the specific kernel and user-space hooks employed, refer to [INTERNALS.md](INTERNALS.md).
