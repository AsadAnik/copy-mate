import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox


def run_adb_command(cmd):
    """Run an ADB command and return output as list of lines"""
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode(errors="ignore").splitlines()
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore").splitlines()


def browse_source():
    folder = filedialog.askdirectory(
        title="Select Source Folder (Phone Path if mounted)"
    )
    if folder:
        src_entry.delete(0, tk.END)
        src_entry.insert(0, folder)


def browse_destination():
    folder = filedialog.askdirectory(title="Select Destination Folder (External Drive)")
    if folder:
        dest_entry.delete(0, tk.END)
        dest_entry.insert(0, folder)


def start_copy():
    source = src_entry.get().strip()
    dest = dest_entry.get().strip()

    if not source or not dest:
        messagebox.showwarning(
            "Missing Info", "Please select both Source and Destination."
        )
        return

    if not os.path.exists(dest):
        os.makedirs(dest)

    chunk_size = 50
    count = 0

    output_box.insert(
        tk.END,
        f"\n📱 Source: {source}\n💾 Destination: {dest}\nChunk size: {chunk_size}\n\n",
    )
    output_box.see(tk.END)
    root.update()

    # Check device connection (optional, skip if copying locally)
    devices = run_adb_command("adb devices")
    if not any("device" in d and not "List" in d for d in devices):
        output_box.insert(tk.END, "⚠️ No ADB device detected. Assuming local copy...\n")

    # If phone is mounted as drive (not via ADB), list files locally
    if os.path.exists(source):
        filelist = os.listdir(source)
    else:
        # Get file list via ADB shell
        filelist = run_adb_command(f'adb shell "ls {source}"')

    if not filelist:
        messagebox.showerror("Error", "No files found or invalid source path.")
        return

    for filename in filelist:
        filename = filename.strip()
        if not filename:
            continue

        dest_file = os.path.join(dest, filename)

        # Skip already existing files
        if os.path.exists(dest_file):
            output_box.insert(tk.END, f"⏩ Skipping (exists): {filename}\n")
        else:
            output_box.insert(tk.END, f"📂 Copying: {filename}\n")
            root.update()

            # Handle either local or adb copy
            if os.path.exists(source):
                try:
                    subprocess.run(
                        f'copy "{os.path.join(source, filename)}" "{dest_file}"',
                        shell=True,
                    )
                except Exception as e:
                    output_box.insert(tk.END, f"❌ Failed: {filename} ({e})\n")
            else:
                subprocess.run(
                    f'adb pull "{source}/{filename}" "{dest_file}"', shell=True
                )

            output_box.insert(tk.END, f"✅ Done: {filename}\n")

        count += 1
        if count >= chunk_size:
            output_box.insert(tk.END, f"⏸️ Pausing after {chunk_size} files...\n\n")
            output_box.see(tk.END)
            root.update()
            count = 0

    output_box.insert(tk.END, "\n🎉 All done! Files copied successfully.\n")
    output_box.see(tk.END)
    messagebox.showinfo("Completed", "Backup completed successfully!")


def about():
    messagebox.showinfo(
        "About",
        "📱 ADB Backup Tool\nCreated by Programming with Asad\nChunk-based phone file copier with skip support.",
    )


# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("📁 Android ADB Backup Tool")
root.geometry("700x520")
root.resizable(False, False)

# Source Picker
tk.Label(
    root, text="📱 Source (phone or local folder):", font=("Segoe UI", 10, "bold")
).pack(pady=(10, 0))
frame_src = tk.Frame(root)
frame_src.pack(pady=5)
src_entry = tk.Entry(frame_src, width=60)
src_entry.pack(side=tk.LEFT, padx=5)
browse_src_btn = tk.Button(frame_src, text="Browse", command=browse_source)
browse_src_btn.pack(side=tk.LEFT)

# Destination Picker
tk.Label(
    root, text="💾 Destination (external drive folder):", font=("Segoe UI", 10, "bold")
).pack(pady=(10, 0))
frame_dest = tk.Frame(root)
frame_dest.pack(pady=5)
dest_entry = tk.Entry(frame_dest, width=60)
dest_entry.pack(side=tk.LEFT, padx=5)
browse_dest_btn = tk.Button(frame_dest, text="Browse", command=browse_destination)
browse_dest_btn.pack(side=tk.LEFT)

# Start Button
tk.Button(
    root,
    text="🚀 Start Copy",
    font=("Segoe UI", 10, "bold"),
    bg="#4CAF50",
    fg="white",
    command=start_copy,
).pack(pady=10)

# Output Textbox
output_box = tk.Text(
    root, width=80, height=18, bg="#1e1e1e", fg="#dcdcdc", font=("Consolas", 9)
)
output_box.pack(pady=10)

# Menu Bar
menu = tk.Menu(root)
menu.add_command(label="About", command=about)
root.config(menu=menu)

root.mainloop()
